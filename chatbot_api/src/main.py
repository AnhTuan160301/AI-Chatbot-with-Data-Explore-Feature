from io import BytesIO
from typing import Any

from fastapi import FastAPI

from agents.initial_agents import agent
from models.models import ProcessInput, ProcessOutput, QueryInput
from utils.csv_agents import load_csv_agent
from utils.pdf_processing import process_pdf

app = FastAPI(
    title="Data Explore Chatbot",
    description="Endpoints for a Data Explore chatbot",
    swagger_ui_parameters={"syntaxHighlight": False}
)


@app.get("/")
async def get_status():
    return {"status": "running"}


@app.post("/chat")
async def qa_chat(queryInput: QueryInput) -> ProcessOutput:
    qa_agent = agent
    response = qa_agent.run(queryInput.user_message)
    data = {"input": queryInput.user_message, "output": response}
    return ProcessOutput(**data)


@app.post("/process_pdf")
async def process_pdfs(processInput: ProcessInput) -> ProcessOutput:
    pdf_chain = await process_pdf(processInput.data)
    result = pdf_chain({"question": processInput.user_message})
    data = {"input": processInput.user_message, "output": result["answer"]}
    return ProcessOutput(**data)


@app.post("/process_csvs")
async def process_csvs(processInput: ProcessInput) -> ProcessOutput:
    response = await load_csv_agent(processInput.data, processInput.user_message)
    data = {"input": processInput.user_message, "output": response}
    return ProcessOutput(**data)
