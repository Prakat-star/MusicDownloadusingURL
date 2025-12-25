from flask import Flask, request, render_template, jsonify, send_from_directory
from pytube import YouTube
import os
import uuid

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

queue = []  # Each track: {"id":..., "name":..., "file":...}

def download_youtube_audio(url):
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=True).first()
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.mp3"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    stream.download(output_path=DOWNLOAD_FOLDER, filename=filename)
    return filename, yt.title

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add", methods=["POST"])
def add_track():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400

    url = data.get("url")
    if not url:
        return jsonify({"success": False, "error": "No URL provided"}), 400

    try:
        filename, title = download_youtube_audio(url)
        track_id = str(uuid.uuid4())
        queue.append({"id": track_id, "name": title, "file": filename})
        return jsonify({"success": True, "queue": queue})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/queue")
def get_queue():
    return jsonify(queue)

@app.route("/action", methods=["POST"])
def queue_action():
    global queue
    data = request.get_json()
    action = data.get("action")
    if action == "next" and queue:
        queue.pop(0)
    elif action == "prev" and queue:
        track = queue.pop(0)
        queue.append(track)
    return jsonify({"success": True, "queue": queue})

@app.route("/downloads/<filename>")
def serve_audio(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
