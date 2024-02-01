import os
from fastapi import FastAPI, File, UploadFile
from typing import Union
import uuid
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import time
from langchain_openai import ChatOpenAI
from langchain.schema import (SystemMessage, HumanMessage, AIMessage)

from dotenv import load_dotenv



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

@app.get("/list_pdfs/{session_id}/")
def get_pdfs(session_id: str):
    pdfs = []
    for dirs in os.listdir(f"data/{session_id}"):
        pdfs.append(dirs)
    return pdfs


@app.post("/upload/{session_id}/")
async def upload_pdf_file(session_id: str, file: UploadFile = File(...)):
    # print(file.filename)
    if session_id in os.listdir("data/"):

        contents = await file.read()
        foldername = file.filename.split('.')[0]
        if not os.path.exists(f"data/{session_id}/{foldername}/"):
            os.mkdirs(f"data/{session_id}/{foldername}/")

        with open(f"data/{session_id}/{foldername}/{foldername}.pdf", "wb") as f:
            f.write(contents)
        with open(f"data/{session_id}/{foldername}/history.txt", "w") as f:
            f.write("This is the history of the previous chat between human and AI: ")

        return {"filename": foldername}

    else:
        return {"Error": "Please enter a valid session id"}

def setups(pdf_location:str):
    load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.environ.get('OPENAI_API_KEY')

    pdf_reader = PdfReader(pdf_location)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    
    embeddings = OpenAIEmbeddings()
    knowledge_base = FAISS.from_texts(chunks, embeddings)

    return knowledge_base
    


def query_ans(location: str, query:str, contexts: list):

    chat = ChatOpenAI(temperature=0)
    sysmsg = [SystemMessage(content="You are a chatbot who gives accurate answer from the given context.")]
    msg = []
    with open(f"{location}history.txt", 'r') as file:
        history = file.read()

    msg.append(HumanMessage(content=history+query))
    q = sysmsg+ contexts + msg
    st_time = time.time()
    # print(q)
    assistant_response = chat(msg)
    msg.append(AIMessage(content=assistant_response.content))

    print("time taken: ", time.time() -st_time)
    # print(assistant_response)

    with open(f"{location}history.txt", 'w') as file:
        file.write(str(msg))

    return {"response": assistant_response.content}

@app.get("/get_response/{session_id}/{pdf_name}/{query}")
async def query_on_pdf(session_id: str, pdf_name: str, query: str):
    sessions = os.listdir("data")
    if session_id in sessions:
        pdfs = os.listdir(f"data/{session_id}")
        if pdf_name in pdfs:
            location = f"data/{session_id}/{pdf_name}/"
            pdf_location = f"{location}{pdf_name}.pdf"
            KB = setups(pdf_location=pdf_location)
            context = KB.similarity_search(query, k=2)
            return query_ans(location=location, query=query, contexts=context)
        else:
            return {"Error": "Please upload the pdf"}

    else:
        return {"Error": "Please enter a valid session id"}