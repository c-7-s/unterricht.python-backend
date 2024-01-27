import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from api.files_service import allowed_file, upload_text, upload_pdf

from api.ai_service import getanswer
from waitress import serve
import api as my_app

app = Flask(__name__)

UPLOAD_FOLDER = 'docs/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "alklkjhasdkjfhkasljd"

# Beispielroute für das Hochladen einer Datei
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

# Beispielroute für das Stellen einer Frage
@app.route('/prompt', methods=['POST'])
def processclaim():
    try:
        input_json = request.get_json(force=True)
        query = input_json["query"]
        output=getanswer(query)
        return output
    except:
        return jsonify({"Status":"Failure --- some error occured"})

if __name__ == "__main__":
    serve(my_app, host="localhost", port=5005)
