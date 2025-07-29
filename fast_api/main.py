from fastapi import FastAPI
from pydantic import BaseModel
from .agent_utils import get_sql_agent_with_memory

app = FastAPI(debug=True)

class QueryRequest(BaseModel):
    question: str
    session_id:str

# Memory store per session
memory_store = {}

@app.post("/query")
async def query_db(request: QueryRequest):
    user_input = request.question
    session_id = request.session_id
    agent = get_sql_agent_with_memory(session_id, memory_store)
    response = agent.invoke({"input": user_input})
    return {"question": user_input,"response": response["output"]}
