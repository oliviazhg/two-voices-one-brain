# api.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from agent import run_agent

app = FastAPI()

# Enable CORS so frontend can access this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or set to your frontend domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/run")
async def run(request: Request):
    data = await request.json()
    input_data = data.get("input")
    result = run_agent(input_data)
    return {"result": result}
