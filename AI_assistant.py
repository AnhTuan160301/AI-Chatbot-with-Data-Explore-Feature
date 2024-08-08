import dotenv
import langchain
from langchain.llms import HuggingFaceHub
from dotenv import load_dotenv
import streamlit as st
import os
import speech_recognition as sr
import pyttsx3
import time
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory, ConversationEntityMemory, ConversationBufferWindowMemory
from langchain.chains import ConversationChain
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.llms.ai21 import AI21
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain.agents import initialize_agent
from langchain.agents import load_tools
from pydantic import BaseModel, Field
from langchain.chains import LLMMathChain
from langchain.agents import Tool
from langchain_experimental.utilities import PythonREPL
from langchain.tools import WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage
from agents import tools
import random
from PyPDF2 import PdfReader
from io import BytesIO
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
import os


def show_chatbot_page():
    dotenv.load_dotenv()
    HUGGINGFACE_KEY = os.getenv("HUGGINGFACEHUB_API_TOKEN")

    PREFIX = """Answer the following questions as best you can only using the following tools:
    Calculator: Useful for when you need to answer questions about math and arithmetics.
    python_repl: Useful when you need to execute python commands.
    duckduckgo: Useful for when you need to search the internet for something another tool cannot find. 
    Datetime: Useful to return the current datetime. 
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

    def get_input():
        p1 = st.session_state.get('p1')
        p2 = st.session_state.get('p2')
        p3 = st.session_state.get('p3')
        p4 = st.session_state.get('p4')

        if not(p1 and p2 and p3 and p4):
            p1, p2, p3, p4 = (
                random.choice(contexts[0]),
                random.choice(contexts[1]),
                random.choice(contexts[2]),
                random.choice(contexts[3]),
            )

        return p1, p2, p3, p4

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


