# PDF Summarizer Chatbot using Google Gemini

A modern Streamlit web app that lets you upload PDF files, chat with the document, and challenge yourself with logic-based questions—powered by Google's Gemini AI.

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
3. **Get your Google Gemini API key**
   - Visit [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
   - Sign up and get your API key
   - You need to enter your own API key in the sidebar to use the app
4. **Run the app**
   ```bash
     python -m streamlit run app.py
   ```
5. **Configure API Key (Required)**
   - When the app starts, you'll see an "API Configuration" section in the sidebar
   - Enter your Google Gemini API key to use the app
   - The app requires a valid Gemini API key to function

## Usage
- Upload a PDF in the sidebar.
- Chat with your document using the chat input.
- Click "Challenge Me" to test your understanding with logic-based questions.

## Author & Contact
- **GitHub:** [karan96108](https://github.com/karan96108)
- **Portfolio:** [karanjuneja.com](https://karanjuneja.com)
- **Email:** karan@karanjuneja.com
