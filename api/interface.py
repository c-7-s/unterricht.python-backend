import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from api.files_service import allowed_file, upload_text, upload_pdf
from api.ai_service import getanswer

backend_api = Flask(__name__)

UPLOAD_FOLDER = 'docs/'

backend_api.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
backend_api.secret_key = "alklkjhasdkjfhkasljd"

@backend_api.route('/', methods=['GET'])
def status():
    return jsonify({'message': 'API is running'}), 200

# Beispielroute für das Hochladen einer Datei
@backend_api.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.get_json(force=True):
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(backend_api.config["UPLOAD_FOLDER"], filename))
        if file.mimetype == 'text/plain':
            upload_text(os.path.join(backend_api.config["UPLOAD_FOLDER"], filename))
        elif file.mimetype == 'application/pdf':
            upload_pdf(os.path.join(backend_api.config["UPLOAD_FOLDER"], filename))
        os.remove(os.path.join(backend_api.config["UPLOAD_FOLDER"], filename))
        return jsonify({'message': 'File uploaded successfully'}), 200
    return jsonify({'error': 'Unsupported file type'}), 400

# Beispielroute für das Stellen einer Frage
@backend_api.route('/prompt', methods=['POST'])
def processclaim():
    try:
        input_json = request.get_json(force=True)
        if 'query' not in request.get_json(force=True):
            return jsonify({"Status":"Failure --- no query given"}), 400
        query = input_json["query"]
        if query == "":
            return jsonify({"Status":"Failure --- empty query given"}), 400
        output=getanswer(query)
        return output
    except:
        return jsonify({"Status":"Failure --- some error occured"}), 400


if __name__ == "__main__":
    backend_api.run(host="0.0.0.0", port=5005)
