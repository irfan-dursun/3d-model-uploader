
from flask import Flask, request, jsonify, send_from_directory
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload_files():
    files = request.files.getlist("images")
    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    for file in files:
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

    # Meshroom batch işlemini çalıştır
    output_path = os.path.abspath(OUTPUT_FOLDER)
    input_path = os.path.abspath(UPLOAD_FOLDER)
    subprocess.run(["meshroom_batch", "--input", input_path, "--output", output_path])

    for root, dirs, files in os.walk(output_path):
        for file in files:
            if file.endswith(".obj") or file.endswith(".stl"):
                return jsonify({
                    "downloadUrl": f"http://localhost:5000/download/{file}"
                })

    return jsonify({"error": "STL dosyası oluşturulamadı"}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
