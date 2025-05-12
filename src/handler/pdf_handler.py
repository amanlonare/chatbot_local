import pypdfium2

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from pathlib import Path
from src.database.vectordb_handler import load_vectordb
from src.utils.utils import timeit
from src.utils import config_loader

PROJECT_ROOT = Path(__file__).parent.parent

config = config_loader.load_config(f"{PROJECT_ROOT}/config/config.yaml")


def get_pdf_texts(pdfs_bytes_list):
    return [extract_text_from_pdf(pdf_bytes.getvalue())
            for pdf_bytes in pdfs_bytes_list]


def extract_text_from_pdf(pdf_bytes):
    pdf_file = pypdfium2.PdfDocument(pdf_bytes)
    return "\n".join(
        pdf_file.get_page(page_number).get_textpage().get_text_range()
        for page_number in range(len(pdf_file)))


def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config["pdf_text_splitter"]["chunk_size"],
        chunk_overlap=config["pdf_text_splitter"]["overlap"],
        separators=config["pdf_text_splitter"]["separators"])
    return splitter.split_text(text)


def get_document_chunks(text_list):
    documents = []
    for text in text_list:
        for chunk in get_text_chunks(text):
            documents.append(Document(page_content=chunk))
    return documents


@timeit
def add_documents_to_db(pdfs_bytes):
    texts = get_pdf_texts(pdfs_bytes)
    documents = get_document_chunks(texts)
    vector_db = load_vectordb()
    vector_db.add_documents(documents)
    print("Documents added to db.")
