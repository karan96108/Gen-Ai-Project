import streamlit as st
import google.generativeai as genai
import PyPDF2
import os
import time

st.set_page_config(page_title="🖊️PDF and Text Summarizer Chatbot")

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


# Gemini API Credentials
with st.sidebar:
    st.title('🖊️PDF and Text Summarizer Chatbot')
    
    # API key configuration
    st.subheader("🔑 API Configuration")
    default_api_key = "AIzaSyAyTtleDxudyfh53okK6yn9GvDyS7cd-3c"  # Your Gemini API key
    user_api_key = st.text_input(
        "Enter your Google Gemini API Key:", 
        value=default_api_key, 
        type="password", 
        help="Get your API key from https://makersuite.google.com/app/apikey"
    )
    
    if user_api_key and user_api_key != "AIzaSyDWUSCkYgcmYxNRPCDnkWM7zZ7zIX3Y02o":
        gemini_api_key = user_api_key
        st.success('Gemini API key configured!', icon='✅')
    else:
        gemini_api_key = default_api_key
        st.success('Using default Gemini API key!', icon='✅')
    
    uploaded_file = st.file_uploader("Upload a PDF or Text file", type=["pdf", "txt"])
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'pdf_text' not in st.session_state:
        st.session_state.pdf_text = ""
    if uploaded_file is not None and uploaded_file != st.session_state.uploaded_file:
        if uploaded_file.type == "application/pdf" or uploaded_file.name.lower().endswith(".pdf"):
            with st.spinner("Extracting text from PDF..."):
                st.session_state.pdf_text = extract_text_from_pdf(uploaded_file)
            st.success("PDF uploaded and text extracted!")
        elif uploaded_file.type == "text/plain" or uploaded_file.name.lower().endswith(".txt"):
            with st.spinner("Reading text file..."):
                st.session_state.pdf_text = uploaded_file.read().decode("utf-8")
            st.success("Text file uploaded and read!")
        else:
            st.session_state.pdf_text = ""
            st.warning("Unsupported file type.")
        st.session_state.uploaded_file = uploaded_file
    pdf_text = st.session_state.pdf_text

    st.markdown('''
        Developed by Karan Juneja - 2024  
        Visit my GitHub profile <a href="https://github.com/karan96108" style="color:white; background-color:#3187A2; padding:3px 5px; text-decoration:none; border-radius:5px;">here</a>
        ''', unsafe_allow_html=True)

# Configure Gemini client and get model
genai.configure(api_key=gemini_api_key)

# List available models and use the first available one
def get_available_model():
    try:
        models = genai.list_models()
        # Build a lookup of available short model names that support generateContent
        available = []
        for m in models:
            try:
                short_name = m.name.split("/")[-1] if hasattr(m, "name") else str(m)
                methods = set(getattr(m, "supported_generation_methods", []) or [])
                if "generateContent" in methods:
                    available.append(short_name)
            except Exception:
                continue

        # Preferred models in order of preference
        preferred_models = [
            "gemini-1.5-flash-latest",
            "gemini-1.5-pro-latest",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro",
        ]

        for pref in preferred_models:
            if pref in available:
                return pref

        # If no preferred model found, return first available supporting generateContent
        if available:
            return available[0]

        # Hard fallback
        return "gemini-1.5-flash-latest"
    except:
        return "gemini-1.5-flash-latest"

model_name = "gemini-1.5-flash-latest"
model = genai.GenerativeModel(model_name)

# Show which model is being used in sidebar
with st.sidebar:
    st.info(f"Using model: {model_name}", icon='🤖')

# Test API connection
def test_api_connection():
    try:
        # List available models first
        models = genai.list_models()
        st.write("Available models:", [model.name for model in models])
        st.write(f"Using model: {model_name}")
        
        response = model.generate_content("Hello")
        return True
    except Exception as e:
        st.error(f"API Connection Test Failed: {str(e)}")
        return False

# Store LLM generated responses
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Upload a PDF file from the sidebar to get started."}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Upload a PDF file from the sidebar to get started."}]


def generate_gemini_response(text, question):
    # Build conversation memory (last 5 turns)
    history_messages = []
    for msg in st.session_state.messages[-10:]:  # up to last 5 user+assistant pairs
        if msg["role"] in ("user", "assistant"):
            # Convert to Gemini format
            if msg["role"] == "user":
                history_messages.append({"role": "user", "parts": [{"text": msg["content"]}]})
            else:
                history_messages.append({"role": "model", "parts": [{"text": msg["content"]}]})
    
    # Create conversation history for Gemini
    chat = model.start_chat(history=history_messages)
    
    system_prompt = (
        "You are a helpful assistant that answers questions based on the provided context. "
        "For every answer, justify your response by referencing the original document (e.g., 'Paragraph 3 of Section 1'). "
        "Use the previous conversation as memory to handle follow-up questions."
    )
    
    prompt = f"{system_prompt}\n\nHere is the context:\n\n{text[:5000]}\n\nNow answer this question:\n{question}"
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = chat.send_message(prompt)
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and "quota" in error_str.lower():
                if attempt < max_retries - 1:
                    st.warning(f"Rate limit reached. Waiting 60 seconds before retry {attempt + 1}/{max_retries}...")
                    time.sleep(60)
                    continue
                else:
                    return "Sorry, the API rate limit has been exceeded. Please try again later or upgrade your Gemini API plan."
            else:
                return f"Error generating response: {error_str}"
    
    return "Failed to generate response after multiple attempts."


def send_message(pdf_text):
    question = st.session_state["chat_input"]
    if question:
        user_message = {"role": "user", "content": question}
        st.session_state.messages.append(user_message)
        response = generate_gemini_response(pdf_text, question)
        assistant_message = {"role": "assistant", "content": response}
        st.session_state.messages.append(assistant_message)
        st.session_state["chat_input"] = ""  # Safe to clear here

def generate_logic_question(pdf_text):
    prompt = f"Read the following document and generate ONE logic-based question that tests understanding of its content. Only output the question, nothing else.\n\nDocument:\n{pdf_text[:5000]}"
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and "quota" in error_str.lower():
                if attempt < max_retries - 1:
                    st.warning(f"Rate limit reached. Waiting 60 seconds before retry {attempt + 1}/{max_retries}...")
                    time.sleep(60)
                    continue
                else:
                    return "Sorry, the API rate limit has been exceeded. Please try again later or upgrade your Gemini API plan."
            else:
                st.error(f"API Error: {error_str}")
                return f"Error generating question: {error_str}"
    
    return "Failed to generate question after multiple attempts."

def evaluate_answer(question, user_answer, pdf_text):
    prompt = f"Document:\n{pdf_text[:5000]}\n\nQuestion: {question}\nUser's Answer: {user_answer}\n\nEvaluate the user's answer for correctness and provide brief feedback."
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and "quota" in error_str.lower():
                if attempt < max_retries - 1:
                    st.warning(f"Rate limit reached. Waiting 60 seconds before retry {attempt + 1}/{max_retries}...")
                    time.sleep(60)
                    continue
                else:
                    return "Sorry, the API rate limit has been exceeded. Please try again later or upgrade your Gemini API plan."
            else:
                return f"Error evaluating answer: {error_str}"
    
    return "Failed to evaluate answer after multiple attempts."

# Generate a new response if a PDF is uploaded
if pdf_text:
    user_input = st.text_input("Enter your question:", key="chat_input", on_change=send_message, args=(pdf_text,))

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

