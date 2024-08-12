from io import BytesIO
from typing import Any

from fastapi import FastAPI

from models.models import ProcessInput
from utils.csv_agents import load_csv_agent
from utils.pdf_processing import process_pdf, load_chain

app = FastAPI(
    title="Data Explore Chatbot",
    description="Endpoints for a Data Explore chatbot",
    swagger_ui_parameters={"syntaxHighlight": False}
)


@app.get("/")
async def get_status():
    return {"status": "running"}


@app.post("/process_pdfs")
async def process_pdfs(processInput: ProcessInput) -> Any:
    try:
        await process_pdf(processInput.data)
        await load_chain()
        return {"message": "success"}
    except Exception as err:
        return {"message": str(err)}


@app.post("/process_csvs")
async def process_csvs(processInput: ProcessInput) -> Any:
    try:
        await load_csv_agent(processInput.data)
        return {"message": "success"}
    except Exception as err:
        return {"message": str(err)}
