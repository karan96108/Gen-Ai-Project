# PDF Summarizer Chatbot using LLaMa2 & OpenRouter

A modern Streamlit web app that lets you upload PDF files, chat with the document, and challenge yourself with logic-based questions—powered by LLaMa2 via OpenRouter.

## Features
- **PDF Upload & Parsing**: Instantly extract text from your PDFs.
- **Conversational Chatbot**: Ask questions about your document and get answers with references to the original text.
- **Follow-up Memory**: The chatbot remembers your previous questions for smarter, context-aware answers.
- **Challenge Me**: Generate logic-based questions from your document, answer them, and get instant feedback with references.
- **Light/Dark Theme**: Switch between light and dark modes for comfortable reading.

## Getting Started
1. **Clone the repository**
   ```bash
   git clone https://github.com/karan96108/Gen-Ai-Project.git
   cd Gen-Ai-Project
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Get your OpenRouter API key**
   - Visit [https://openrouter.ai/keys](https://openrouter.ai/keys)
   - Sign up and get your API key
   - The app comes with a default API key, but you can enter your own in the sidebar
4. **Run the app**
   ```bash
     python -m streamlit run app.py
   ```
5. **Configure API Key (Optional)**
   - When the app starts, you'll see an "API Configuration" section in the sidebar
   - Enter your own OpenRouter API key if you want to use your own credits
   - If you don't enter a key, the app will use the default key

## Usage
- Upload a PDF in the sidebar.
- Chat with your document using the chat input.
- Click "Challenge Me" to test your understanding with logic-based questions.

## Author & Contact
- **GitHub:** [karan96108](https://github.com/karan96108)
- **Portfolio:** [karanjuneja.com](https://karanjuneja.com)
- **Email:** karan@karanjuneja.com
