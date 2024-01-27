import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from api.files_service import allowed_file, upload_text, upload_pdf

from api.ai_service import getanswer

myapp = Flask(__name__)

UPLOAD_FOLDER = 'docs/'

myapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
myapp.secret_key = "alklkjhasdkjfhkasljd"

# Beispielroute für das Hochladen einer Datei
@myapp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(myapp.config["UPLOAD_FOLDER"], filename))
        if file.mimetype == 'text/plain':
            upload_text(os.path.join(myapp.config["UPLOAD_FOLDER"], filename))
        elif file.mimetype == 'application/pdf':
            upload_pdf(os.path.join(myapp.config["UPLOAD_FOLDER"], filename))
        os.remove(os.path.join(myapp.config["UPLOAD_FOLDER"], filename))
        return jsonify({'message': 'File uploaded successfully'}), 200
    return jsonify({'error': 'Unsupported file type'}), 400

# Beispielroute für das Stellen einer Frage
@myapp.route('/prompt', methods=['POST'])
def processclaim():
    try:
        input_json = request.get_json(force=True)
        query = input_json["query"]
        output=getanswer(query)
        return output
    except:
        return jsonify({"Status":"Failure --- some error occured"})

if __name__ == "__main__":
    myapp.run(host="0.0.0.0", port=5005)
