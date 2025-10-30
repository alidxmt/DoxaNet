# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from belief_revision import BeliefRevision
import json
from typing import List

app = FastAPI()

# Templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ----------------------
# In-memory storage for agents
# ----------------------
agents = {}  # key: agent name, value: BeliefRevision instance

# ----------------------
# Routes
# ----------------------
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Create a new agent

@app.post("/agent/create")
async def create_agent(
    name: str = Form(...),
    propositions: List[str] = Form(...)
):
    try:
        agent = BeliefRevision(name=name, propositions=propositions)
        agents[name] = agent
        return {"status": "success", "message": f"Agent '{name}' created."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Add a proposition to an agent
@app.post("/agent/add_proposition")
async def add_proposition(
    name: str = Form(...),
    proposition: str = Form(...),
    is_core: bool = Form(False),
    rank: int = Form(0)
):
    if name not in agents:
        return JSONResponse({"status": "error", "message": "Agent not found."})
    agent = agents[name]
    agent.add_proposition(proposition, is_core=is_core, rank=rank)
    agent.sync_epistemic_space()  # keep consistent
    return JSONResponse({"status": "success", "K": agent.K, "core": list(agent.core), "entrenchment": agent.entrenchment})

# Contract a belief
@app.post("/agent/contract")
async def contract_belief(name: str = Form(...), belief: str = Form(...)):
    if name not in agents:
        return JSONResponse({"status": "error", "message": "Agent not found."})
    agent = agents[name]
    removed = list(agent.contract(belief))
    agent.sync_epistemic_space()  # keep consistent
    return JSONResponse({"status": "success", "removed": removed, "K": agent.K})

# Expand a belief
@app.post("/agent/expand")
async def expand_belief(name: str = Form(...), belief: str = Form(...)):
    if name not in agents:
        return JSONResponse({"status": "error", "message": "Agent not found."})
    agent = agents[name]
    agent.expand(belief)
    agent.sync_epistemic_space()  # keep consistent
    return JSONResponse({"status": "success", "K": agent.K})
# Get agent state
@app.get("/agent/state")
async def get_agent_state(name: str):
    if name not in agents:
        return JSONResponse({"status": "error", "message": "Agent not found."})
    agent = agents[name]
    return JSONResponse({
        "status": "success",
        "state": {
            "K": agent.K,
            "core": list(agent.core),
            "entrenchment": agent.entrenchment
        }
    })

