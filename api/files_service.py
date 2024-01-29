from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.supabase import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings

from api.config import interface_config
from utils.utils import initialize_environment_variables, initialize_subabase_client, initialize_openai_client

initialize_environment_variables("../.env")

# Initialize Supabase Client
supabase_client = initialize_subabase_client()

# Initialize OpenAI Client
openai_client = initialize_openai_client()

ALLOWED_EXTENSIONS = set(interface_config.upload_allowed_formats)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_text(path):
    loader = TextLoader(path)
    output = loader.load_and_split(
        CharacterTextSplitter(separator=['\n\n', '\n', '. ', ' ']))
    supa = SupabaseVectorStore.from_documents(
                output, 
                OpenAIEmbeddings(),
                supabase_client, 
                interface_config.upload_table_name,
        )
    print(supa)

def upload_pdf(path):
    loader = PyPDFLoader(path)
    output = loader.load_and_split(
        CharacterTextSplitter(separator='. '))
    supa = SupabaseVectorStore.from_documents(
        output, OpenAIEmbeddings(),
        client=supabase_client,
        table_name=interface_config.upload_table_name,
    )
    print(supa)