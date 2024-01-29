import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from api.files_service import allowed_file, upload_text, upload_pdf, get_uploaded_ids
from api.ai_service import getanswer

from api.config import interface_config

UPLOAD_FOLDER = interface_config.upload_source_folder

backend_api = Flask(__name__)

backend_api.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
backend_api.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
backend_api.secret_key = "alklkjhasdkjfhkasljd"

@backend_api.route('/', methods=['GET'])
def status():
    return jsonify({'message': 'API is running'}), 200

# Beispielroute für das Hochladen einer Datei
@backend_api.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported file type'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(backend_api.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        if file.mimetype == 'text/plain':
            upload_text(filepath)
        elif file.mimetype == 'application/pdf':
            upload_pdf(filepath)
        id_array = get_uploaded_ids(filepath, interface_config.upload_table_name)
        os.remove(filepath)
        return jsonify({'id_array': id_array}), 200



# Beispielroute für das Stellen einer Frage
@backend_api.route('/prompt', methods=['POST'])
def processclaim():
    try:
        input_json = request.get_json(force=True)
        if 'query' not in request.get_json(force=True):
            return jsonify({"error": "no query given"}), 400
        query = input_json["query"]
        if query == "":
            return jsonify({"error": "empty query given"}), 400
        output=getanswer(query)
        return output
    except:
        return jsonify({"error": "some error occured"}), 400


if __name__ == "__main__":
    backend_api.run(host="0.0.0.0", port=5005)
