document.addEventListener('DOMContentLoaded', function () {
    const selectFolderButton = document.getElementById('select-folder');
    const coverImage = document.getElementById('cover-image');
    const songName = document.getElementById('song-name');
    const songSinger = document.getElementById('song-singer');
    const currentTimeElement = document.getElementById('current-time');
    const totalTimeElement = document.getElementById('total-time');
    const rangeElement = document.getElementById('range');
    const musicContainer = document.getElementById('music-container');
    const selectFolderContainer = document.getElementById('select-folder-container');
    const playButton = document.getElementById('play');
    const nextButton = document.querySelector('.bi-skip-forward');
    const prevButton = document.querySelector('.bi-skip-backward');
    const shuffleButton = document.getElementById('type');
    const heartButton = document.getElementById('heart');

    let musicFiles = [];
    let currentFolder = '';
    let currentSongIndex = 0;
    let isShuffleOn = false;
    let favoriteSongs = new Set();
    let audio = null;
    let coinInterval = null;

    // Reset to show folder selection after reload
    localStorage.removeItem('myMusicDB');

    // Event listeners for buttons
    selectFolderButton.addEventListener('click', selectFolder);
    playButton.addEventListener('click', togglePlayPause);
    nextButton.addEventListener('click', playNextSong);
    prevButton.addEventListener('click', playPreviousSong);
    shuffleButton.addEventListener('click', toggleShuffle);
    heartButton.addEventListener('click', toggleFavorite);

    function selectFolder() {
        const input = document.createElement('input');
        input.type = 'file';
        input.webkitdirectory = true;
        input.multiple = true;
        input.accept = 'audio/*';

        input.addEventListener('change', function () {
            const files = Array.from(input.files);
            musicFiles = {};

            files.forEach(file => {
                if (file.type.startsWith('audio/')) {
                    const pathParts = file.webkitRelativePath.split('/');
                    const folderName = pathParts.slice(1, -1).join('/') || 'Root';
                    if (!musicFiles[folderName]) {
                        musicFiles[folderName] = [];
                    }
                    musicFiles[folderName].push({
                        name: file.name,
                        url: URL.createObjectURL(file)
                    });
                }
            });

            localStorage.setItem('myMusicDB', JSON.stringify(musicFiles));
            loadMusic(musicFiles);
        });

        input.click();
    }

    function loadMusic(files) {
        // Switch UI to show the music player
        selectFolderContainer.style.display = 'none';
        musicContainer.style.display = 'block';

        currentFolder = Object.keys(files)[0];
        playSong(0);  // Start by playing the first song
    }

    function playSong(index) {
        if (audio) {
            audio.pause();
            clearInterval(coinInterval);
        }

        const song = musicFiles[currentFolder][index];
        songName.textContent = song.name;
        songSinger.textContent = currentFolder;

        audio = new Audio(song.url);
        audio.play();

        audio.addEventListener('timeupdate', updateProgress);
        audio.addEventListener('loadedmetadata', () => {
            totalTimeElement.textContent = formatTime(audio.duration);
        });

        audio.addEventListener('ended', playNextSong);  // Play the next song automatically

        currentSongIndex = index;
        playButton.classList.remove('bi-play-fill');
        playButton.classList.add('bi-pause-fill');

        // Disable user from changing the range (progress bar)
        rangeElement.setAttribute('disabled', true);

        // Start giving coins every second
        startCoinGiving();
    }

    function playNextSong() {
        if (isShuffleOn) {
            const randomIndex = Math.floor(Math.random() * musicFiles[currentFolder].length);
            playSong(randomIndex);
        } else {
            let nextIndex = currentSongIndex + 1;
            if (nextIndex >= musicFiles[currentFolder].length) {
                nextIndex = 0; // Loop back to the first song
            }
            playSong(nextIndex);
        }
    }

    function playPreviousSong() {
        let prevIndex = currentSongIndex - 1;
        if (prevIndex < 0) {
            prevIndex = musicFiles[currentFolder].length - 1; // Go to the last song
        }
        playSong(prevIndex);
    }

    function togglePlayPause() {
        if (audio.paused) {
            audio.play();
            playButton.classList.remove('bi-play-fill');
            playButton.classList.add('bi-pause-fill');
            startCoinGiving();  // Start coin interval when playing
        } else {
            audio.pause();
            playButton.classList.remove('bi-pause-fill');
            playButton.classList.add('bi-play-fill');
            clearInterval(coinInterval);  // Stop coin interval when paused
        }
    }

    function toggleShuffle() {
        const element = shuffleButton;
        if (element.classList.contains("bi-shuffle")) {
            element.classList.remove("bi-shuffle");
            element.classList.add("bi-repeat");
            isShuffleOn = false; // Switch to repeat mode
        } else if (element.classList.contains("bi-repeat")) {
            element.classList.remove("bi-repeat");
            element.classList.add("bi-repeat-1");
            isShuffleOn = false; // Switch to repeat one song mode
        } else if (element.classList.contains("bi-repeat-1")) {
            element.classList.remove("bi-repeat-1");
            element.classList.add("bi-shuffle");
            isShuffleOn = true; // Switch to shuffle mode
        }
    }

    function toggleFavorite() {
        const song = musicFiles[currentFolder][currentSongIndex];
        if (favoriteSongs.has(song.name)) {
            favoriteSongs.delete(song.name);
            heartButton.classList.remove("bi-heart-fill");
            heartButton.classList.add("bi-heart");
        } else {
            favoriteSongs.add(song.name);
            heartButton.classList.remove("bi-heart");
            heartButton.classList.add("bi-heart-fill");
        }
    }

    function updateProgress() {
        currentTimeElement.textContent = formatTime(audio.currentTime);
        rangeElement.value = (audio.currentTime / audio.duration) * 100;
    }

    function startCoinGiving() {
        coinInterval = setInterval(() => {
            // Call the Flask route to add 1 coin every second
            fetch("/tapping/add-coin", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.coins !== undefined) {
                        document.getElementById('coin-count').textContent = data.coins;
                        document.getElementById('user-level').textContent = data.level;
                        document.getElementById('progress-bar').style.width = data.progress + "%";
                    }
                })
                .catch((error) => console.error("Error:", error));
        }, 1000);
    }

    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        seconds = Math.floor(seconds % 60);
        return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    }

    if (localStorage.getItem('myMusicDB')) {
        musicFiles = JSON.parse(localStorage.getItem('myMusicDB'));
        loadMusic(musicFiles);
    }
});
