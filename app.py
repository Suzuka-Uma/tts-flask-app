from flask import Flask, request, jsonify, send_from_directory, render_template
import edge_tts
import asyncio
import os
import uuid

app = Flask(__name__)

# Config
AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'audio')

if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# Dictionaries of available free voices
VOICES = {
    # Vietnamese
    'nam_minh_northern_male': 'vi-VN-NamMinhNeural',
    'hoai_my_southern_female': 'vi-VN-HoaiMyNeural',
    # English
    'jenny_us_female': 'en-US-JennyNeural',
    'guy_us_male': 'en-US-GuyNeural',
    # Japanese
    'nanami_jp_female': 'ja-JP-NanamiNeural',
    'keita_jp_male': 'ja-JP-KeitaNeural'
}

@app.route('/')
def index_vi():
    return render_template('index.html')

@app.route('/en')
def index_en():
    return render_template('en.html')

@app.route('/jp')
def index_jp():
    return render_template('jp.html')

@app.route('/api/synthesize', methods=['POST'])
def synthesize():
    data = request.json
    if not data or 'text' not in data or 'voice' not in data:
        return jsonify({"error": "Missing text or voice in request"}), 400
    
    text = data['text']
    voice_key = data['voice']
    
    # Check if voice_key exists
    if voice_key not in VOICES:
        return jsonify({"error": "Invalid voice selected"}), 400

    voice_id = VOICES[voice_key]
    
    # Generate a unique filename
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)
    
    # We use asyncio to run the edge-tts generation
    async def _generate_audio():
        communicate = edge_tts.Communicate(text, voice_id)
        await communicate.save(filepath)
    
    try:
        # Generate base TTS
        asyncio.run(_generate_audio())
            
        return jsonify({
            "success": True, 
            "audio_url": f"/audio/{filename}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
