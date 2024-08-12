import csv
import os
import random
import time

import dotenv
import requests
import streamlit as st
from langchain.agents import initialize_agent
from langchain.llms.ai21 import AI21
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import SystemMessage

from chatbot_api.src.agents.agents import tools
from chatbot_api.src.utils.csv_agents import csv_agent
from chatbot_api.src.utils.pdf_processing import get_pdf_text, retriever


def show_chatbot_page():
    global agent1, agent
    dotenv.load_dotenv()
    HUGGINGFACE_KEY = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    AI21_API_KEY = os.getenv("AI21_LLM_key")
    CHATBOT_URL = os.getenv("CHATBOT_URL", "http://localhost:8000")
    docs_pdf = None
    docs_csv = None
    PREFIX = """Answer the following questions as best you can only using the following tools:
 Calculator: Useful for when you need to answer questions about math and arithmetics.
 python_repl: Useful when you need to execute python commands.
 duckduckgo: Useful for when you need to search the internet for something another tool cannot find.
 Datetime:useful to return the current datetime 
 """
    FORMAT_INSTRUCTIONS = """Use the following format:

 Question: the input question you must answer
 Thought: you should always think about what to do. Always use a tool
 Action: the action to take, should be one of [{tool_names}]
 Action Input: the input to the action
 Observation: the result of the action 
 ... (this Thought/Action/Action Input/Observation can repeat N time)
 Thought: I now know the final answer
 Final Answer: the final answer to the original input question

 If you can't find the answer, you will respond as follows: Final Answer: Sorry 😔, I don't know the answer. I will do my best next time!

 """
    SUFFIX = """Begin! Remmember to give the observation as a final answer:

 Question: {input}
 Thought:{agent_scratchpad}"""
    sys_msg = """Assistant is a large language model trained by AI21 Studio.

Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

Unfortunately, Assistant is very terrible at maths . When provided with any questions, no matter how simple, assistant always refers to it's trusty tools and absolutely does NOT try to answer questions by itself

Overall, Assistant is a powerful system that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
"""

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
    system_message = SystemMessage(
        content=sys_msg
    )
    agent_kwargs = {
        "system_message ": system_message
    }

    llm = AI21(ai21_api_key=AI21_API_KEY, temperature=0.1, verbose=False)
    memory = ConversationBufferWindowMemory(
        memory_key='chat_history',
        k=5,
        return_messages=True,
        verbose=True,
    )
    if 'agent' not in st.session_state:
        agent = initialize_agent(
            llm=llm,
            agent='conversational-react-description',
            prefix=PREFIX,
            suffix=SUFFIX,
            format_instructions=FORMAT_INSTRUCTIONS,
            tools=tools,
            max_iteration=10,
            handle_parsing_errors=True,
            verbose=True,
            agent_kwargs=agent_kwargs,
            memory=memory,
            early_stopping_method="generate",
        )
        st.session_state.agent = agent

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

        response = f'Echo {prompt}'
        response += ":hushed:"
        response = st.session_state.agent.run(prompt)
        substrings_to_remove = ['AI:']
        for substring in substrings_to_remove:
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
            regenerated_response = st.session_state.agent.run(input=last_user_input)
            substrings_to_remove = ['AI:']
            for substring in substrings_to_remove:
                regenerated_response = regenerated_response.replace(substring, '')
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

        response = requests.post(url=CHATBOT_URL + "/process_csvs/")
        st.sidebar.subheader("Ask a Question ❓")
        if response.json()["message"] == "success":
            agent1 = csv_agent
        prompt = st.sidebar.text_input("Enter your question about the file")
        ask_button = st.sidebar.button("Send 🚀")

        if ask_button:
            if prompt:
                with st.spinner("Analyzing... 🔄"):
                    output = agent1.run(prompt)
                st.subheader("Assistant's Response 🤖")
                st.info(output)

    st.sidebar.title("PDF Document Queries 📑")
    user_pdf = st.sidebar.file_uploader("Upload your PDF files 📂", type="pdf")
    if 'conversation' not in st.session_state:
        st.session_state.conversation = None
    if user_pdf is not None:
        with st.spinner("Analyzing the PDF... 🔄"):
            payload = {"data": get_pdf_text(user_pdf)}
            response = requests.post(url=CHATBOT_URL + "/process_pdfs", data=payload)
            if response.json()["message"] == "success":
                st.session_state.conversation = retriever
        st.sidebar.subheader("Ask a Question ❓")
        prompt = st.sidebar.text_input("Enter your question about the file")
        ask_button = st.sidebar.button("Send 🚀")
        if ask_button:
            if prompt:
                with st.spinner("Analyzing... 🔄"):
                    output = st.session_state.conversation(prompt)
                st.subheader("Assistant's Response 🤖")
                answer = output.get('answer')
                st.info(answer)


if __name__ == "__main__":
    show_chatbot_page()
