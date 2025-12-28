const form = document.getElementById("downloadForm");
const urlInput = document.getElementById("urlInput");
const resultDiv = document.getElementById("result");
const downloadLink = document.getElementById("downloadLink");
const audioPlayer = document.getElementById("audioPlayer");
const errorDiv = document.getElementById("error");
const loadingDiv = document.getElementById("loading");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  errorDiv.classList.add("hidden");
  resultDiv.classList.add("hidden");
  loadingDiv.classList.remove("hidden");
  downloadLink.href = "#";
  audioPlayer.src = "";

  const url = urlInput.value.trim();
  if (!url) {
    loadingDiv.classList.add("hidden");
    errorDiv.textContent = "Please enter a valid YouTube URL.";
    errorDiv.classList.remove("hidden");
    return;
  }

  try {
    const response = await fetch("/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    const data = await response.json();

    loadingDiv.classList.add("hidden");

    if (!response.ok) {
      throw new Error(data.error || "Download failed");
    }

 
    const mp3Url = data.files[0].url;

    downloadLink.href = mp3Url;
    downloadLink.download = "";
    audioPlayer.src = mp3Url;

    resultDiv.classList.remove("hidden");
  } catch (err) {
    loadingDiv.classList.add("hidden");
    errorDiv.textContent = err.message;
    errorDiv.classList.remove("hidden");
  }
});
