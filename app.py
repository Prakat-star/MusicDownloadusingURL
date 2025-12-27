import subprocess
import os
import uuid
from flask import Flask, jsonify, request, render_template
from supabase import create_client
from dotenv import load_dotenv


load_dotenv()
SUPABASE_KEY = os.getenv("SUPABASE_KEY") #afno hala
SUPABASE_URL = os.getenv("SUPABASE_URL") #yo pani afnai hala

BUCKET_NAME = "mp3-storage"
AUDIO_QUALITY = "192k"

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    
    output_template = os.path.join(
        DOWNLOAD_FOLDER,
        "%(title)s-%(id)s.%(ext)s"
    )

   
    try:
        subprocess.run(
            [
                "python", "-m", "yt_dlp",
                "-x",
                "--audio-format", "mp3",
                "--audio-quality", AUDIO_QUALITY,
                "-o", output_template,
                url
            ],
            check=True
        )
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"yt-dlp failed: {e}"}), 500

    uploaded_files = []

    # 2️⃣ Upload everything downloaded
    for file in os.listdir(DOWNLOAD_FOLDER):
        if file.endswith(".mp3"):
            file_path = os.path.join(DOWNLOAD_FOLDER, file)

            try:
                with open(file_path, "rb") as f:
                    supabase.storage.from_(BUCKET_NAME).upload(file, f)

                signed = supabase.storage.from_(BUCKET_NAME).create_signed_url(
                    file, 3600, options={"download": True}
                )

                mp3_url = (
                    signed.get("signedURL")
                    or signed.get("signed_url")
                    or signed
                )

                uploaded_files.append({
                    "name": file,
                    "url": mp3_url
                })

            finally:
                os.remove(file_path)

    return jsonify({
        "success": True,
        "files": uploaded_files
    })

if __name__ == "__main__":
    app.run(debug=True)
