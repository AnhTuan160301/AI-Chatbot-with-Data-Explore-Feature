import pdfplumber
from langchain.chains import ConversationalRetrievalChain
from langchain.llms.ai21 import AI21
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
import os
import dotenv

dotenv.load_dotenv()
HUGGINGFACE_KEY = os.getenv("HUGGINGFACEHUB_API_TOKEN")
AI21_API_KEY = os.getenv("AI21_LLM_key")
llm = AI21(ai21_api_key=AI21_API_KEY, temperature=0.1, verbose=False)


def get_pdf_text(pdf):
    with pdfplumber.open(pdf) as pdf_file:
        text = ""
        for page in pdf_file.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(chunks):
    embed = HuggingFaceEmbeddings(encode_kwargs={"normalize_embeddings": True})
    vectorstore = FAISS.from_texts(chunks, embed)
    return vectorstore.as_retriever()


def create_chain(retriever):
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=False)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory
    )
    return conversation_chain


text_chunks = None
retriever = None
chain = None


async def load_chain():
    global chain
    chain = create_chain(retriever)


async def process_pdf(docs):
    global text_chunks, retriever
    text_chunks = get_text_chunks(docs)
    retriever = get_vectorstore(text_chunks)
