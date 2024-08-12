from fastapi import FastAPI
from streamlit.runtime.uploaded_file_manager import UploadedFile

from utils.pdf_processing import process_pdf, load_chain
from utils.csv_agents import load_csv_agent

app = FastAPI(
    title="Data Explore Chatbot",
    description="Endpoints for a Data Explore chatbot",
)


@app.post("/process_pdfs/")
async def process_pdfs(docs: str):
    try:
        await process_pdf(docs)
        await load_chain()
        return {"message": "success"}
    except Exception as err:
        return {"error": str(err)}


@app.post("/process_csvs/")
async def process_csvs(docs: UploadedFile):
    try:
        await load_csv_agent()
        return {"message": "success"}
    except Exception as err:
        return {"error": str(err)}
