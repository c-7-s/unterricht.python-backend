import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.supabase import SupabaseVectorStore
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from supabase.client import create_client, Client

load_dotenv("../.env")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_API_KEY")
supabase_client: Client = create_client(url, key)

UPLOAD_FOLDER = 'docs/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "alklkjhasdkjfhkasljd"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        if file.mimetype == 'text/plain':
            upload_text(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        elif file.mimetype == 'application/pdf':
            upload_pdf(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return jsonify({'message': 'File uploaded successfully'}), 200
    return jsonify({'error': 'Unsupported file type'}), 400

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

if __name__ == '__main__':
    app.debug = True
    app.run()