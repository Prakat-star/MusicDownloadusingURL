const addTrackForm = document.getElementById("addTrackForm");
const trackUrl = document.getElementById("trackUrl");
const queueList = document.getElementById("queueList");
const nowPlaying = document.getElementById("nowPlaying");
const audio = document.getElementById("audioPlayer");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const status = document.getElementById("status");

let queue = [];
let currentIndex = 0;


async function fetchQueue() {
    const res = await fetch("/queue");
    queue = await res.json();
    renderQueue();
    if(queue.length && !audio.src){
        loadTrack(0);
    }
}

function renderQueue() {
    queueList.innerHTML = "";
    queue.forEach((track, i) => {
        const li = document.createElement("li");
        li.textContent = track.name;
        li.dataset.index = i;
        if(i === currentIndex) li.classList.add("current");
        queueList.appendChild(li);
    });
}

function loadTrack(index){
    if(!queue[index]) return;
    currentIndex = index;
    const track = queue[index];
    audio.src = `/downloads/${track.file}`;
    nowPlaying.textContent = "Now Playing: " + track.name;
    audio.play();
    renderQueue();
}


addTrackForm.addEventListener("submit", async e=>{
    e.preventDefault();
    const url = trackUrl.value.trim();
    if(!url) return;

    status.textContent = "Downloading...";
    const res = await fetch("/add", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({url})
    });
    const data = await res.json();
    status.textContent = "";

    if(data.success){
        trackUrl.value = "";
        await fetchQueue();
        loadTrack(queue.length - 1);
    } else {
        alert("Error adding track: " + data.error);
    }
});


nextBtn.addEventListener("click", async ()=>{
    await fetch("/action", {
        method:"POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({action:"next"})
    });
    fetchQueue();
});
prevBtn.addEventListener("click", async ()=>{
    await fetch("/action", {
        method:"POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({action:"prev"})
    });
    fetchQueue();
});


queueList.addEventListener("click", e=>{
    if(e.target.tagName==="LI"){
        const index = parseInt(e.target.dataset.index);
        loadTrack(index);
    }
});

// Auto fetch queue every 2 seconds
setInterval(fetchQueue, 2000);
fetchQueue();
