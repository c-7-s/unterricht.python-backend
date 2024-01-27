# -*- coding: utf-8 -*-
"""
Created on Sat Jan 27 17:07:41 2024

@author: ruedi
"""

# getestet mit Postman
# upload: json
# ask: pdf

from flask import Flask, request, jsonify

app = Flask(__name__)

# Beispielroute für das Hochladen einer Datei
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    # Verarbeite die hochgeladene Datei und speichere sie
    # Hier könntest du die Datei speichern und in der Datenbank referenzieren
    return jsonify({'message': 'File uploaded successfully'}), 200

# Beispielroute für das Stellen einer Frage
@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    # question = data['question']
    # Verarbeite die gestellte Frage und gib eine Antwort zurück
    # Hier könntest du die Frage beantworten und die Antwort zurückgeben
    return jsonify(data), 200

if __name__ == '__main__':
    app.run(debug=True)
