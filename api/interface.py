import os
import json
import mimetypes
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

import api.files_service as fs
import api.agent_service as ags

from api.config import interface_config

backend_api = Flask(__name__)

backend_api.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
backend_api.secret_key = "alklkjhasdkjfhkasljd"

@backend_api.route('/', methods=['GET'])
def status():
    return jsonify({'message': 'API is running'}), 200

# Beispielroute für das Hochladen einer Datei
@backend_api.route('/upload', methods=['POST'])
def upload_file():
    input_json = request.get_json(force=True)
    if 'fullPath' not in input_json:
        return jsonify({"error": "'fullPath' key missing"}), 400
    elif 'path' not in input_json:
        return jsonify({"error": "'path' key missing"}), 400
    full_path, user_path = input_json["fullPath"], input_json["path"]
    if full_path == "":
        return jsonify({"error": "'fullPath' value missing"}), 400
    elif user_path == "":
        return jsonify({"error": "'path' value missing"}), 400
    file_name = os.path.basename(user_path)
    if not fs.allowed_file(file_name):
        return jsonify({"error": "file type not supported"}), 400
    file_path = secure_filename(user_path)
    fs.download_file_from_bucket(file_path, full_path, user_path)
    try:
        if mimetypes.guess_type(file_path)[0] == 'text/plain':
            fs.upload_text(file_path)
        elif mimetypes.guess_type(file_path)[0] == 'application/pdf':
            fs.upload_pdf(file_path)
    except Exception as e:
        return jsonify({"error": f"error: {e}"}), 400
    vector_store_ids = fs.get_uploaded_ids(file_path, interface_config.upload_table_name)
    return jsonify({'vector_store_ids': vector_store_ids}), 200

# Beispielroute für das Stellen einer Frage
@backend_api.route('/prompt', methods=['POST'])
def processclaim():
    try:
        input_json = request.get_json(force=True)
        if 'school_type' not in request.get_json(force=True):
            return jsonify({"error": "'school_type' key missing"}), 400
        if 'subject' not in request.get_json(force=True):
            return jsonify({"error": "'subject' key missing"}), 400
        if 'topic' not in request.get_json(force=True):
            return jsonify({"error": "'topic' key missing"}), 400
        if 'grade' not in request.get_json(force=True):
            return jsonify({"error": "'grade' key missing"}), 400
        if 'state' not in request.get_json(force=True):
            return jsonify({"error": "'state' key missing"}), 400
        if 'keywords' not in request.get_json(force=True):
            return jsonify({"error": "'keywords' key missing"}), 400
        if 'context' not in request.get_json(force=True):
            return jsonify({"error": "'context' key missing"}), 400
        try:
            output = ags.get_answer(input_json)
        except Exception as e:
            return jsonify({"error": f"error: {e}"}), 400
        return output
    except:
        return jsonify({"error": "some error occured"}), 400


if __name__ == "__main__":
    backend_api.run(host="0.0.0.0", port=5005)
