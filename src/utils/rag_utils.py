from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import create_retriever_tool
from dotenv import load_dotenv
import os

load_dotenv(override=True)

loader = TextLoader(os.getenv("RAG_FILE_PATH"))
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=100, chunk_overlap=50
)
docs_splits = text_splitter.split_documents(documents)

vectorestore = Chroma.from_documents(
    documents=docs_splits, 
    embedding=OpenAIEmbeddings(), 
    persist_directory="./chroma_db"
    )

retriever = vectorestore.as_retriever(search_kwargs={"k": 3})

retriever_tool = create_retriever_tool(
    retriever=retriever,
    name="retriever_products_and_services_information",
    description="Useful for answering questions by retrieving relevant information from a custom knowledge base.",
)

def get_retriever_tool():
    return retriever_tool
