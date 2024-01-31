import os
from fastapi import FastAPI, File, UploadFile
from typing import Union
import uuid


app = FastAPI()


@app.get("/")
def read_get():
    return {"api": "running"}

@app.get("/get_sessions")
def get_existing_sessions():
    return os.listdir("data")

@app.get("/create_new_session")
def get_a_new_session():
    session_name = f"{uuid.uuid4()}"
    parent_dir = "data/"
    path = os.path.join(parent_dir, session_name) 
    os.mkdir(path) 
    return {"Current session ": session_name}

@app.get("/{session_id}/list")
def get_pdfs(session_id: str):
    pdfs = []
    for dirs in os.listdir(f"data/{session_id}"):
        if dirs[-3:] == "pdf":
            pdfs.append(dirs)
    return pdfs


@app.post("/{session_id}/upload/")
async def create_up_file(session_id: str, file: UploadFile = File(...)):

    print(file.filename)
    # file.filename = f"{uuid.uuid4()}.jpg"
    contents = await file.read()

    with open(f"data/{session_id}/{file.filename}", "wb") as f:
        f.write(contents)

    return {"filename": file.filename}