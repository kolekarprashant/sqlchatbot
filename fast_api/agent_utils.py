from langchain_openai import AzureChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.agents.agent_toolkits import create_sql_agent
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import sqlite3
import requests
from sqlalchemy.pool import StaticPool

# Load environment variables
load_dotenv()

AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_DEPLOYMENT_NAME = "GPTO4_training"
AZURE_ENDPOINT = "https://gen-ai-training-internal-july.openai.azure.com/"
AZURE_API_VERSION = "2024-12-01-preview"

def get_llm():
    return AzureChatOpenAI(
        azure_deployment=AZURE_DEPLOYMENT_NAME,
        api_key=AZURE_API_KEY,
        api_version=AZURE_API_VERSION,
        azure_endpoint=AZURE_ENDPOINT,
        openai_api_type="azure",
        model_kwargs={
        "messages": [
            {"role": "system", "content": "You are a helpful SQL assistant. Always return only SQL queries."}
        ]
    }
        
    )

def get_sql_database():
    url = "https://raw.githubusercontent.com/jpwhite3/northwind-SQLite3/main/src/create.sql"
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.executescript(requests.get(url).text)
    engine = create_engine("sqlite://", creator=lambda: connection, poolclass=StaticPool,
                           connect_args={"check_same_thread": False})
    return SQLDatabase(engine)

def get_sql_agent():
    llm = get_llm()
    db = get_sql_database()
    return create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=True,
        handle_parsing_errors=True
    )
