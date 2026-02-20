document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('text-input');
    const charCurrent = document.getElementById('char-current');
    const voiceSelect = document.getElementById('voice-select');
    const animeVoiceSelect = document.getElementById('anime-voice-select');
    const generateBtn = document.getElementById('generate-btn');
    const btnText = document.querySelector('.btn-text');
    const btnLoader = document.querySelector('.btn-loader');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const audioContainer = document.getElementById('audio-container');
    const audioPlayer = document.getElementById('audio-player');
    const downloadBtn = document.getElementById('download-btn');

    const MAX_CHARS = 1000;

    // Character counter
    textInput.addEventListener('input', () => {
        const text = textInput.value;
        const length = text.length;

        if (length > MAX_CHARS) {
            textInput.value = text.substring(0, MAX_CHARS);
            charCurrent.textContent = MAX_CHARS;
            charCurrent.style.color = 'var(--danger)';
        } else {
            charCurrent.textContent = length;
            charCurrent.style.color = 'var(--text-muted)';
        }
    });

    // Generate Button Click
    generateBtn.addEventListener('click', async () => {
        const text = textInput.value.trim();
        const voice = voiceSelect.value;
        const animeVoice = animeVoiceSelect.value;

        if (!text) {
            showError("Vui lòng nhập văn bản tiếng Việt.");
            textInput.focus();
            return;
        }

        // Hide old errors/audio
        errorMessage.classList.add('hidden');
        audioContainer.classList.add('hidden');

        // Setup Loading State
        if (animeVoice !== 'none') {
            btnLoader.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Cloning Anime Voice... (may take a minute)';
        } else {
            btnLoader.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
        }
        setLoading(true);

        try {
            const response = await fetch('/api/synthesize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text, voice, anime_voice: animeVoice })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate speech.');
            }

            // Success
            const uniqueUrl = data.audio_url + '?t=' + new Date().getTime(); // Prevent caching
            audioPlayer.src = uniqueUrl;
            downloadBtn.href = uniqueUrl;
            downloadBtn.download = `Vietnamese_TTS_${Date.now()}.mp3`;

            audioContainer.classList.remove('hidden');
            audioPlayer.play().catch(e => console.log("Auto-play blocked", e));

        } catch (error) {
            showError(error.message);
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        if (isLoading) {
            generateBtn.disabled = true;
            btnText.classList.add('hidden');
            btnLoader.classList.remove('hidden');
        } else {
            generateBtn.disabled = false;
            btnText.classList.remove('hidden');
            btnLoader.classList.add('hidden');
        }
    }

    function showError(message) {
        errorText.textContent = message;
        errorMessage.classList.remove('hidden');
    }
});
