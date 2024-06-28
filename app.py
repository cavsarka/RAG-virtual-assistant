import shutil
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from pathlib import Path
import glob
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

app = Flask(__name__)
CORS(app)  # Enables CORS for all routes

# Import your functions
from create_database import generate_data_store
from query_data import query_database
from create_database import deleteItems


UPLOAD_FOLDER = './data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('frontend/home_page', 'website.html')

@app.route('/upload_page')
def upload_page():
    return send_from_directory('frontend/upload_document_page', 'upload_page.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('frontend', path)

@app.route('/list_files', methods=['GET'])
def list_files():
    files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    return jsonify(files)

@app.route('/download_file/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

@app.route('/delete_file', methods=['POST'])
def delete_file():
    data = request.json
    filename = data['filename']
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        deleteItems(file_path)
        return jsonify({'message': f'File {filename} deleted successfully'}), 200
    else:
        return jsonify({'error': f'File {filename} not found'}), 404


@app.route('/query_openai', methods=['POST'])
def query_openai_route():
    data = request.json
    query = data['query']
    result = query_database(query)
    return jsonify(result)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_path = os.path.join("./data", file.filename)

    file.save(file_path)

    try:
        # Update database after saving the file
        generate_data_store("./data")
        return jsonify({'message': 'File uploaded and database updated successfully', 'file_path': file_path}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to update the database'}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
