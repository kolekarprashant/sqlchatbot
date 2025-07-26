from fastapi import FastAPI, Request
from pydantic import BaseModel
from fast_api.agent_utils import get_sql_agent
import hashlib
from langchain_core.messages import HumanMessage
from uuid import uuid4

app = FastAPI(debug=True)

class QueryRequest(BaseModel):
    question: str

chat_histories = {}

# Function to get a simple in-memory session ID based on client IP
def get_session_id(request: Request) -> str:
    return hashlib.md5(request.client.host.encode()).hexdigest()


agent = get_sql_agent()

@app.post("/query")
async def query_db(request: QueryRequest):
        session_id = str(uuid4())
        user_input = request.question
        if session_id not in chat_histories:
            chat_histories[session_id] = []

        history = chat_histories[session_id]
        history.append(HumanMessage(user_input))
        response = agent.invoke({
             "input": user_input,
             "chat_history": history
        })
        return {"question": user_input, "response":  response["output"]}
    