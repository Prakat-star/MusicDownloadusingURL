from flask import Flask, render_template, request, send_file
import requests
import os

app = Flask(__name__)

TEMP_FILE = "temp_audio"

@app.route("/", methods=["GET", "POST"])
def index():
    audio_url = None
    if request.method == "POST":
        audio_url = request.form.get("url")
    return render_template("index.html", audio_url=audio_url)

@app.route("/download")
def download():
    url = request.args.get("url")

    r = requests.get(url, stream=True)
    with open(TEMP_FILE, "wb") as f:
        for chunk in r.iter_content(1024):
            if chunk:
                f.write(chunk)

    return send_file(
        TEMP_FILE,
        as_attachment=True,
        download_name="downloaded_audio.mp3"
    )

if __name__ == "__main__":
    app.run(debug=True)
