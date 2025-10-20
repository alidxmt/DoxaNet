# app/main.py
from fastapi import FastAPI, Query
from app.logic import EpistemicSpace

app = FastAPI()

@app.get("/possibilities")
def get_possibilities(n_props: int = Query(3, ge=1, le=20)):
    """
    Return all possibilities for n_props propositions.
    n_props: number of propositions (default 3)
    """
    space = EpistemicSpace(n_props)
    # Return as a list of bitstrings
    return {"n_props": n_props, "possibilities": list(space)}
