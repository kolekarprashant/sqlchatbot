from langchain_openai import AzureChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.agents import AgentExecutor,create_tool_calling_agent
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import sqlite3
import requests
from sqlalchemy.pool import StaticPool
from langchain.memory import ConversationBufferMemory
from langchain.agents.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Load environment variables
load_dotenv()

AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_DEPLOYMENT_NAME = "GPTO4_training"
AZURE_ENDPOINT = "https://gen-ai-training-internal-july.openai.azure.com/"
AZURE_API_VERSION = "2024-12-01-preview"

def get_llm():
    return AzureChatOpenAI(
        azure_deployment=AZURE_DEPLOYMENT_NAME,
        #api_key=AZURE_API_KEY,
        api_key="WCNEbWiHAYC0Us4aan2TYCbpn8jMLALfZ1CbN2f8KosNXYqAqK5nJQQJ99BDACYeBjFXJ3w3AAABACOG3COf",
        api_version=AZURE_API_VERSION,
        azure_endpoint=AZURE_ENDPOINT,
        openai_api_type="azure"
    )

def get_sql_database():
    url = "https://raw.githubusercontent.com/jpwhite3/northwind-SQLite3/main/src/create.sql"
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.executescript(requests.get(url).text)
    engine = create_engine("sqlite://", creator=lambda: connection, poolclass=StaticPool,
                           connect_args={"check_same_thread": False})
    return SQLDatabase(engine)

def get_sql_agent_with_memory(session_id: str, memory_store: dict):
    llm = get_llm()
    db = get_sql_database()
    toolkit = SQLDatabaseToolkit(llm=llm, db=db)

    # Create or reuse memory per session
    if session_id not in memory_store:
        memory_store[session_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )

    memory = memory_store[session_id]
    prompt = ChatPromptTemplate.from_messages([
        ("system", 
     "You are a helpful assistant that only answers questions by executing SQL queries on the provided database. "
     "You must only use the tools given to retrieve information. "
     "If the user asks anything outside the scope of the database (like weather, current events, etc.), respond with: "
     "'I'm only able to help with database-related questions.'"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    print("Session ID:", session_id)
    print("Current memory keys:", list(memory_store.keys()))
    print("Memory contents:", memory_store[session_id].load_memory_variables({}))

    # Create agent and wrap it in executor
    agent = create_tool_calling_agent(llm=llm, tools=toolkit.get_tools(),prompt=prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=toolkit.get_tools(),
        memory=memory,
        verbose=True,
        handle_parsing_errors=True
    )
    return executor
