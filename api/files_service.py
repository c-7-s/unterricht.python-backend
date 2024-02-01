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
    loader = TextLoader(path, autodetect_encoding=True)
    output = loader.load_and_split(
        CharacterTextSplitter(separator=['\n\n', '\n', '. ', ' ']))
    supa = SupabaseVectorStore.from_documents(
                output, 
                OpenAIEmbeddings(),
                supabase_client, 
                interface_config.upload_table_name,
        )
    return None

def upload_pdf(path):
    loader = PyPDFLoader(path, autodetect_encoding=True)
    output = loader.load_and_split(
        CharacterTextSplitter(separator='. '))
    supa = SupabaseVectorStore.from_documents(
        output, OpenAIEmbeddings(),
        client=supabase_client,
        table_name=interface_config.upload_table_name,
    )
    return None

def get_uploaded_ids(filepath, upload_table_name):
    data, _cnt = supabase_client.table(upload_table_name).select('id').contains('metadata', {'source':filepath}).execute()
    return [data[1][i].get("id") for i in range(len(data[1]))]

def download_file_from_bucket(destination: str, full_path: str, path: str):
    full_path_list = full_path.split("/")
    bucket_name = full_path_list[0]
    with open(destination, 'wb+') as f:
        storage_file = supabase_client.storage.from_(bucket_name).download(path)
        f.write(storage_file)