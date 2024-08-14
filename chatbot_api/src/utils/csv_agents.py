import os
import dotenv
from langchain.llms.ai21 import AI21
from langchain_experimental.agents import create_csv_agent

dotenv.load_dotenv()
HUGGINGFACE_KEY = os.getenv("HUGGINGFACEHUB_API_TOKEN")
AI21_API_KEY = os.getenv("AI21_LLM_key")
llm = AI21(ai21_api_key=AI21_API_KEY, temperature=0.1, verbose=False)

csv_agent = None


async def load_csv_agent(csv_file_path, user_message):
    global csv_agent
    csv_agent = create_csv_agent(llm, csv_file_path, agent='zero-shot-react-description', handle_parsing_errors=True,
                                 verbose=True)
    return csv_agent.run(user_message)
