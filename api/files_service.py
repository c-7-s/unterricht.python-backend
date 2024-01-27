import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.supabase import SupabaseVectorStore
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv
from supabase.client import create_client, Client

ALLOWED_EXTENSIONS = set(['txt', 'pdf'])

load_dotenv("../.env")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_API_KEY")
supabase_client: Client = create_client(url, key)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_text(path):
    loader = TextLoader(path)
    output = loader.load_and_split(
        CharacterTextSplitter(separator=['\n\n', '\n', '. ', ' ']))
    supa = SupabaseVectorStore.from_documents(
        output, OpenAIEmbeddings(),
        supabase_client, 'documents_new')
    print(supa)

def upload_pdf(path):
    loader = PyPDFLoader(path)
    output = loader.load_and_split(
        CharacterTextSplitter(separator='. '))
    supa = SupabaseVectorStore.from_documents(
        output, OpenAIEmbeddings(),
        client=supabase_client,
        table_name="documents_new",
    )
    print(supa)