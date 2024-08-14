import os
import random
import time

import dotenv
import matplotlib.pyplot as plt
import pandas as pd
import pdfplumber
import requests
import streamlit as st

from response_process import extract_code_from_response


def show_chatbot_page():
    dotenv.load_dotenv()
    CHATBOT_URL = os.getenv("CHATBOT_URL", "http://localhost:8000")
    FILE_STORAGE_DIR = os.getenv("FILES_STORAGE_DIR")
    YOUR_FULL_PATH = os.getenv("FULL_PATH_DIR")
    if not os.path.exists(YOUR_FULL_PATH):
        os.mkdir(YOUR_FULL_PATH)
    contexts = [
        [
            "Give me a joke",
            "Tell me a funny story",
            "Share a humorous anecdote",
            "Make me laugh",
            "Tell a pun",
            "Share a comic one-liner",
            "Recite a witty quote",
            "Entertain me with a humorous fact",
            "Give me a laugh",
            "Tell a light-hearted joke"
        ],
        [
            "Tell me about the history of Rome",
            "Discuss Rome's cultural heritage",
            "Tell me about famous Roman emperors",
            "Discuss Rome's architectural marvels",
            "Share stories about Roman mythology",
            "Explore Roman ruins and landmarks",
        ],
        [
            "Give me a simple function in Python",
            "Write a simple Python function for me",
            "Explain a basic Python function",
            "Show how to define a simple function in Python",
            "Share an easy Python function example",
            "Teach me a beginner-level Python function",
            "Explain a fundamental Python function"
        ],
        [
            "Give me ideas",
            "Provide creative inspiration",
            "Share innovative suggestions",
            "Offer brainstorming concepts",
            "Give me creative thoughts",
            "Provide inspiration for new projects",
            "Suggest imaginative ideas",
            "Share innovative concepts",
            "Offer unique and creative suggestions",
            "Provide ideas for exploration"
        ]
    ]

    # Function to get input and store in session state
    def get_input():
        p1 = st.session_state.get('p1')
        p2 = st.session_state.get('p2')
        p3 = st.session_state.get('p3')
        p4 = st.session_state.get('p4')

        if not (p1 and p2 and p3 and p4):
            p1, p2, p3, p4 = (
                random.choice(contexts[0]),
                random.choice(contexts[1]),
                random.choice(contexts[2]),
                random.choice(contexts[3]),

            )
            st.session_state['p1'] = p1
            st.session_state['p2'] = p2
            st.session_state['p3'] = p3
            st.session_state['p4'] = p4

        return p1, p2, p3, p4

    # Get the input
    if 'context' not in st.session_state:
        p1, p2, p3, p4 = get_input()
    else:
        p1 = st.session_state['p1']
        p2 = st.session_state['p2']
        p3 = st.session_state['p3']
        p4 = st.session_state['p4']

    def get_pdf_text(pdf):
        with pdfplumber.open(pdf) as pdf_file:
            text = ""
            for page in pdf_file.pages:
                text += page.extract_text()
        return text

    def type_effect(response):
        if response:
            words = response.split()
            displayed_text = st.empty()
            for i in range(len(words)):
                displayed_text.write(" ".join(words[:i + 1]))
                time.sleep(0.2)
                if i == len(words) - 1:
                    break

    def generate_welcoming_message():
        markdown = """
    <style>
    @keyframes fadeInUp {
        0% {
            opacity: 0;
            transform: translateY(20px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    </style>
    <div style="display: flex; justify-content: center; align-items: center; height: 90vh;">
        <div style="text-align: center; animation: fadeInUp 1s ease-out;">
            <h2 style="color: #FFD700; font-size: 36px;">
            <br><br>Welcome Again! How can I assist you today?<br> 🤖
            </h2>
        </div>
    </div>
    """
        return markdown

    if 'empty_space' not in st.session_state:
        # Create empty_space and store it in session state
        st.session_state.empty_space = st.empty()
        welcoming_message = generate_welcoming_message()
        st.session_state.empty_space.markdown(welcoming_message, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    if 'button1' not in st.session_state:
        st.session_state.button1_clicked = False
    if 'button2' not in st.session_state:
        st.session_state.button2_clicked = False
    if 'button3' not in st.session_state:
        st.session_state.button3_clicked = False
    if 'button4' not in st.session_state:
        st.session_state.button4_clicked = False
    if not st.session_state.get('all_buttons_clicked', False):
        col1_empty = st.empty()
        col2_empty = st.empty()

        with col1:
            if not st.session_state.button1_clicked:
                button1 = st.button(p1, help="Click to start a conversation")
                if button1:
                    st.session_state.button1_clicked = True
                    st.session_state.all_buttons_clicked = True
                    col1_empty.empty()

            if not st.session_state.button3_clicked:
                button3 = st.button(p3, help="Click to start a conversation")
                if button3:
                    st.session_state.button3_clicked = True
                    st.session_state.all_buttons_clicked = True
                    col1_empty.empty()

        with col2:
            if not st.session_state.button2_clicked:
                button2 = st.button(p2, help="Click to start a conversation")
                if button2:
                    st.session_state.button2_clicked = True
                    st.session_state.all_buttons_clicked = True
                    col2_empty.empty()

            if not st.session_state.button4_clicked:
                button4 = st.button(p4, help="Click to start a conversation")
                if button4:
                    st.session_state.button4_clicked = True
                    st.session_state.all_buttons_clicked = True
                    col2_empty.empty()

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message["content"], unsafe_allow_html=True)

    if st.session_state.button1_clicked:
        prompt = p1
    elif st.session_state.button2_clicked:
        prompt = p2
    elif st.session_state.button3_clicked:
        prompt = p3
    elif st.session_state.button4_clicked:
        prompt = p4
    else:
        prompt = st.chat_input('Message to ChatBot...')

    if prompt:

        with st.chat_message("user"):
            st.session_state.all_buttons_clicked = True
            st.markdown(prompt)

        st.session_state.messages.append({'role': 'user', 'content': str(prompt)})

        data = {"user_message": prompt}
        response_dict = requests.post(url=CHATBOT_URL + "/chat", json=data)
        substrings_to_remove = ['AI:']
        for substring in substrings_to_remove:
            response = response_dict.json()["output"]
            response = response.replace(substring, '')
        with st.spinner("Thinking...Please wait..."):
            time.sleep(1.9)
        with st.chat_message("assistant"):
            segments = response.split("```")
            for i, segment in enumerate(segments):
                if i % 2 == 0:
                    type_effect(segment.strip())
                else:
                    code_block = segment.strip()
                    if code_block:
                        st.code(code_block)

        st.session_state.messages.append({'role': 'assistant', 'content': response})
        st.rerun()

    if st.button("Regenerate 🔄", help="Click to regenerate the response"):
        messages_reversed = st.session_state.messages[::-1]
        last_user_input = None
        for message in messages_reversed:
            if message['role'] == 'user':
                last_user_input = message['content']
                break
        if not last_user_input:
            st.error('Oops! Please Enter Your Prompt', icon="⚠️")
        else:
            with st.spinner("Thinking...Please wait..."):
                time.sleep(1.9)
            data = {"user_message": last_user_input}
            regenerate_response_dict = requests.post(url=CHATBOT_URL + "/chat", json=data)
            substrings_to_remove = ['AI:']
            for substring in substrings_to_remove:
                regenerated_response = regenerate_response_dict.json()["output"].replace(substring, '')
            del st.session_state.messages[-1]
            with st.chat_message("assistant"):
                segments = regenerated_response.split("```")
                for i, segment in enumerate(segments):
                    if i % 2 == 0:
                        type_effect(segment.strip())
                    else:
                        code_block = segment.strip()
                        if code_block:
                            st.code(code_block)
            st.session_state.messages.append({'role': 'assistant', 'content': regenerated_response})
            st.rerun()

    st.sidebar.title("CSV Data Analysis 📊")

    user_csv = st.sidebar.file_uploader("Upload your CSV file 📂", type="csv")

    if user_csv is not None:
        file_path = os.path.join(YOUR_FULL_PATH, user_csv.name)
        with open(file_path, "wb") as f:
            f.write(user_csv.getbuffer())

        df = pd.read_csv(file_path)
        st.sidebar.subheader("Ask a Question ❓")
        prompt = st.sidebar.text_input("Enter your question about the file", key="csv_prompt")
        ask_button = st.sidebar.button("Send 🚀", key="csv")

        if ask_button:
            if prompt:
                with st.spinner("Analyzing... 🔄"):
                    data = {"data": file_path, "user_message": prompt}
                    response = requests.post(url=CHATBOT_URL + "/process_csvs", json=data)
                    st.subheader("Assistant's Response 🤖")
                    if response.status_code == 200:
                        code_to_execute = extract_code_from_response(response.json()["output"])

                        if code_to_execute:
                            try:
                                # Making df available for execution in the context
                                exec(code_to_execute, globals(), {"df": df, "plt": plt})
                                fig = plt.gcf()  # Get current figure
                                st.plotly_chart(fig)  # Display using Streamlit
                            except Exception as e:
                                st.write(f"Error executing code: {e}")
                        else:
                            st.info(response.json()["output"])
                    else:
                        output_text = """An error occurred while processing your message.
                                    Please try again or rephrase your message."""
                        st.info(output_text)

    st.sidebar.title("PDF Document Queries 📑")
    user_pdf = st.sidebar.file_uploader("Upload your PDF files 📂", type="pdf")
    if 'conversation' not in st.session_state:
        st.session_state.conversation = None
    if user_pdf is not None:
        with st.spinner("Analyzing the PDF... 🔄"):
            pdf_data = get_pdf_text(user_pdf)
        st.sidebar.subheader("Ask a Question ❓")
        prompt = st.sidebar.text_input("Enter your question about the file", key="pdf_prompt")
        ask_button = st.sidebar.button("Send 🚀", key="pdf")
        if ask_button:
            if prompt:
                with st.spinner("Analyzing... 🔄"):
                    data = {"data": pdf_data, "user_message": prompt}
                    response = requests.post(url=CHATBOT_URL + "/process_pdf", json=data)
                    st.subheader("Assistant's Response 🤖")
                    if response.status_code == 200:
                        answer = response.json()["output"]
                        st.info(answer)
                    else:
                        output_text = """An error occurred while processing your message.
                                    Please try again or rephrase your message."""
                        st.info(output_text)


if __name__ == "__main__":
    show_chatbot_page()
