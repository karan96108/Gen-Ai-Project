import streamlit as st
import openai
import PyPDF2
import os

st.set_page_config(page_title="🖊️PDF Summarizer Chatbot")

# Toggle light and dark mode themes
ms = st.session_state
if "themes" not in ms: 
    ms.themes = {"current_theme": "light",
                 "refreshed": True,
                    
                "light": {"theme.base": "dark",
                          "theme.backgroundColor": "#FFFFFF",
                          "theme.primaryColor": "#6200EE",
                          "theme.secondaryBackgroundColor": "#F5F5F5",
                          "theme.textColor": "000000",
                          "button_face": "🌜"},

                "dark":  {"theme.base": "light",
                          "theme.backgroundColor": "#121212",
                          "theme.primaryColor": "#BB86FC",
                          "theme.secondaryBackgroundColor": "#1F1B24",
                          "theme.textColor": "#E0E0E0",
                          "button_face": "🌞"},
                          }


def ChangeTheme():
    previous_theme = ms.themes["current_theme"]
    tdict = ms.themes["light"] if ms.themes["current_theme"] == "light" else ms.themes["dark"]
    for vkey, vval in tdict.items(): 
        if vkey.startswith("theme"): st._config.set_option(vkey, vval)

    ms.themes["refreshed"] = False
    if previous_theme == "dark": ms.themes["current_theme"] = "light"
    elif previous_theme == "light": ms.themes["current_theme"] = "dark"

btn_face = ms.themes["light"]["button_face"] if ms.themes["current_theme"] == "light" else ms.themes["dark"]["button_face"]
st.button(btn_face, on_click=ChangeTheme)

if ms.themes["refreshed"] == False:
    ms.themes["refreshed"] = True
    st.rerun()


# Function to extract pdf to text format
def extract_text_from_pdf(pdf_file):
    """Extract text from an uploaded PDF file."""
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


# OpenRouter Credentials
with st.sidebar:
    st.title('🖊️PDF Summarizer Chatbot')
    
    # API key configuration
    st.subheader("🔑 API Configuration")
    default_api_key = "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"
    user_api_key = st.text_input(
        "Enter your OpenRouter API Key:", 
        value=default_api_key, 
        type="password", 
        help="Get your API key from https://openrouter.ai/keys"
    )
    
    if user_api_key:
        openrouter_api_key = user_api_key
        st.success('API key configured!', icon='✅')
    else:
        openrouter_api_key = default_api_key
        st.info('Using default API key. You can enter your own key above.', icon='ℹ️')

    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    pdf_text = ""
    
    if uploaded_file:
        with st.spinner("Extracting text from PDF..."):
            pdf_text = extract_text_from_pdf(uploaded_file)
        st.success("PDF uploaded and text extracted!")

    st.markdown('''
        Developed by Karan Juneja - 2024  
        Visit my GitHub profile <a href="https://github.com/karan96108" style="color:white; background-color:#3187A2; padding:3px 5px; text-decoration:none; border-radius:5px;">here</a>
        ''', unsafe_allow_html=True)

# Configure OpenAI client for OpenRouter
client = openai.OpenAI(
    api_key=openrouter_api_key,
    base_url="https://openrouter.ai/api/v1"
)

# Test API connection
def test_api_connection():
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10,
            extra_headers={
                "HTTP-Referer": "https://github.com/karan96108/Gen-Ai-Project",
                "X-Title": "PDF Summarizer Chatbot"
            }
        )
        return True
    except Exception as e:
        st.error(f"API Connection Test Failed: {str(e)}")
        return False

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Upload a PDF file from the sidebar to get started."}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Upload a PDF file from the sidebar to get started."}]
    st.sidebar.button('Clear Chat History', on_click=clear_chat_history)


def generate_llama2_response(text, question):
    # Build conversation memory (last 5 turns)
    history_messages = []
    for msg in st.session_state.messages[-10:]:  # up to last 5 user+assistant pairs
        if msg["role"] in ("user", "assistant"):
            history_messages.append({"role": msg["role"], "content": msg["content"]})
    prompt = f"Here is the context:\n\n{text[:5000]}\n\nNow answer this question:\n{question}"
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324",
            messages=[
                {"role": "system", "content": (
                    "You are a helpful assistant that answers questions based on the provided context. "
                    "For every answer, justify your response by referencing the original document (e.g., 'Paragraph 3 of Section 1'). "
                    "Use the previous conversation as memory to handle follow-up questions."
                )},
                *history_messages,
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2000,
            extra_headers={
                "HTTP-Referer": "https://github.com/karan96108/Gen-Ai-Project",
                "X-Title": "PDF Summarizer Chatbot"
            }
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"


def send_message(pdf_text):
    question = st.session_state["chat_input"]
    if question:
        user_message = {"role": "user", "content": question}
        st.session_state.messages.append(user_message)
        response = generate_llama2_response(pdf_text, question)
        assistant_message = {"role": "assistant", "content": response}
        st.session_state.messages.append(assistant_message)
        st.session_state["chat_input"] = ""  # Safe to clear here

def generate_logic_question(pdf_text):
    prompt = f"Read the following document and generate ONE logic-based question that tests understanding of its content. Only output the question, nothing else.\n\nDocument:\n{pdf_text[:5000]}"
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates logic-based questions from documents."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=200,
            extra_headers={
                "HTTP-Referer": "https://github.com/karan96108/Gen-Ai-Project",
                "X-Title": "PDF Summarizer Chatbot"
            }
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return f"Error generating question: {str(e)}"

def evaluate_answer(question, user_answer, pdf_text):
    prompt = f"Document:\n{pdf_text[:5000]}\n\nQuestion: {question}\nUser's Answer: {user_answer}\n\nEvaluate the user's answer for correctness and provide brief feedback."
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324",
            messages=[
                {"role": "system", "content": (
                    "You are a helpful assistant that evaluates answers to logic-based questions from documents. "
                    "For every evaluation, justify your feedback by referencing the original document (e.g., 'Paragraph 3 of Section 1')."
                )},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=200,
            extra_headers={
                "HTTP-Referer": "https://github.com/karan96108/Gen-Ai-Project",
                "X-Title": "PDF Summarizer Chatbot"
            }
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error evaluating answer: {str(e)}"

# Generate a new response if a PDF is uploaded
if pdf_text:
    st.text_input("Enter your question:", key="chat_input")
    st.button("Send", key="send_btn", on_click=send_message, args=(pdf_text,))

    # Challenge Me logic
    if "challenge_question" not in st.session_state:
        st.session_state["challenge_question"] = None
    if "challenge_feedback" not in st.session_state:
        st.session_state["challenge_feedback"] = None
    if "challenge_answer" not in st.session_state:
        st.session_state["challenge_answer"] = ""

    def start_challenge():
        st.session_state["challenge_question"] = generate_logic_question(pdf_text)
        st.session_state["challenge_feedback"] = None
        st.session_state["challenge_answer"] = ""

    def submit_challenge():
        user_answer = st.session_state["challenge_answer"]
        feedback = evaluate_answer(st.session_state["challenge_question"], user_answer, pdf_text)
        st.session_state["challenge_feedback"] = feedback

    st.markdown("---")
    if st.session_state["challenge_question"] is None:
        st.button("Challenge Me", key="challenge_btn", on_click=start_challenge)
    else:
        st.write(f"**Challenge Question:** {st.session_state['challenge_question']}")
        st.text_input("Your Answer:", key="challenge_answer")
        st.button("Submit Answer", key="submit_challenge_btn", on_click=submit_challenge)
        if st.session_state["challenge_feedback"]:
            st.success(st.session_state["challenge_feedback"])
        st.button("Next Challenge", key="next_challenge_btn", on_click=start_challenge)

