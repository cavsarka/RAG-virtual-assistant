import os
import argparse
import shutil
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
import openai
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader




load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

#Set where to save the Vector Database
CHROMA_PATH = "chroma"
DATA_PATH = "./data"

def main():
    generate_data_store(DATA_PATH)

def generate_data_store(path: str):
    documents = load_directory(path)
    # chunks = split_text(documents)
    save_to_chroma(documents)
    #manual_save(documents)

def load_directory(path: str):
    documents = []

    for name in os.listdir(path):
        file_path = os.path.join(DATA_PATH, name)
        documents.extend(load_document(file_path))

    return documents

def load_document(path: str):
    #loader = DirectoryLoader(DATA_PATH)
    documents = []

    trimmedPath = path.lstrip("./data/")
    fileName, fileExt = os.path.splitext(trimmedPath)

    if fileExt == ".csv":
        loader = CSVLoader(path)
        documents = loader.load()
    elif fileExt == ".pdf":
        loader = PyPDFLoader(path)
        documents = loader.load()
    

    return documents


def calculate_chunk_ids(chunks):

    # This will create IDs like "data/Lenovo_Docks_Data:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


def save_to_chroma(chunks: list[Document]):

    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=OpenAIEmbeddings())

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
    else:
        print("✅ No new documents to add")
    

def deleteItems(path: str):
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=OpenAIEmbeddings)

    path_length = len(path)

    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])

    for id in existing_ids:
        if id[0:(path_length)] == path.rstrip():
            db.delete(id)

