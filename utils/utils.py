from langchain_openai.embeddings import OpenAIEmbeddings

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Pinecone
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from dotenv import load_dotenv

import os
import pinecone


load_dotenv()

os.environ["PINECONE_API_KEY"] = os.environ.get('PINECONE_API_KEY')
os.environ["PINECONE_ENV"] = os.environ.get('PINECONE_ENV')
os.environ["OPENAI_API_KEY"] = os.environ.get('OPENAI_API_KEY')

embeddings = OpenAIEmbeddings()


def initializePinecone():\
    pinecone.init(
        api_key=os.getenv("PINECONE_API_KEY"), 
        environment=os.getenv("PINECONE_ENV"), 
    )


def createIndex(index_name:str):
    if index_name not in pinecone.list_indexes():
        # we create a new index
        pinecone.create_index(
        name=index_name,
        metric='cosine',
        dimension=1536  
    )


def newDataLoad(directory:str):
    loader = DirectoryLoader(directory)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100, 
        separators=[" ", ",", "\n"]
    )
    return text_splitter.split_documents(documents)


def newIndex(index_name:str, directory:str):
    docs = newDataLoad(directory=directory)
    return Pinecone.from_documents(docs, embeddings, index_name=index_name)

def existingVectorstore(index_name:str):
    
    return Pinecone.from_existing_index(index_name, embeddings)

def addToIndex(index_name:str, documents:list):
    index = pinecone.Index(index_name)
    text_field = "text"
    vectorstore = Pinecone(index, embeddings, text_field)
    vectorstore.add_documents(documents)

def extractDocMetaData(docs:list):
    content = [x.page_content for x in (docs)]
    metadata = [x.metadata for x in (docs)]
    return content, metadata
