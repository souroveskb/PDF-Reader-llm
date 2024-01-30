from fastapi import FastAPI

import os
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI

from langchain.chains.question_answering import load_qa_chain
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain.prompts import PromptTemplate

from utils.utils import initializePinecone, existingVectorstore, newDataLoad, \
     extractDocMetaData, createIndex, testing, addToIndex, pinecone



load_dotenv()

os.environ["PINECONE_API_KEY"] = os.environ.get('pinecone_apikey')
os.environ["PINECONE_ENV"] = os.environ.get('pinecode_env')
os.environ["OPENAI_API_KEY"] = os.environ.get('OPENAI_API_KEY')


embeddings = OpenAIEmbeddings()
directory = "data"
index_name = "pdf_reader"

# print(len(docs))

initializePinecone()
vectorstore = existingVectorstore(index_name)



def get_similiar_docs(query, k=5, score=False):
  if score:
    similar_docs = vectorstore.similarity_search_with_score(query, k=k)
  else:
    similar_docs = vectorstore.similarity_search(query, k=k)
  # print(similar_docs)
  return similar_docs 
  
# print(get_similiar_docs(query)[0])


## GPT model answer retrieval part
model_name = "gpt-3.5-turbo-16k"
# model_name = "gpt-3.5-turbo"
llm = ChatOpenAI(temperature=0, model_name=model_name)


prompt_template = """You are a helpful AI assistant that answers question based on the context you are given\n\n\n

this is the context {context}
based on the context answer the following quesion and don't try to make up answers.\
 
Question: {question}"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

chain = load_qa_chain(llm, chain_type="stuff", prompt=PROMPT)

def get_answer(query):
  similar_docs = get_similiar_docs(query, k = 8)
  # answer = chain.run(input_documents=similar_docs, question=query)

  answer = chain({"input_documents": similar_docs, "question": query},return_only_outputs=True)
  return answer



app = FastAPI()


@app.get("/test/")
async def test_vector():
  return "testing called"


@app.get("/reload/")
async def load_vectorstores():
  docs = newDataLoad(directory = directory)
  addToIndex(index_name, documents=docs)
  return "re-filled the vectorstores"


class Question(BaseModel):
  query: str
  description: str | None = None


@app.post("/query/")
async def query_ans(question: Question):
  answer = get_answer(query=f'{question.query}')
  return answer


class Documents(BaseModel):
  index_name: str
  docs: list
  description: str | None = None




import streamlit as st
st.set_page_config(page_title="Ask your PDF")
st.header("Ask your PDF 💬")

# show user input
user_question = st.text_input("Ask a question about your PDF:")
if user_question:
  start_time = time.time()
  response = get_answer(f"{user_question}")
      
  response_time = time.time() - start_time
  st.write(response)