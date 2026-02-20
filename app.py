from flask import Flask, request, jsonify, send_from_directory, render_template
import edge_tts
import asyncio
import os
import uuid
from rvc_service import convert_voice, init_rvc

app = Flask(__name__)

# Initialize RVC locally if possible
try:
    init_rvc()
except Exception as e:
    print(f"RVC intialization failed: {e}")

# Directory to store generated audio files
AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'audio')
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# Dictionary of available free voices
VOICES = {
    'nam_minh_northern_male': 'vi-VN-NamMinhNeural',
    'hoai_my_southern_female': 'vi-VN-HoaiMyNeural'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/synthesize', methods=['POST'])
def synthesize():
    data = request.json
    if not data or 'text' not in data or 'voice' not in data:
        return jsonify({"error": "Missing text or voice in request"}), 400
    
    text = data['text']
    voice_key = data['voice']
    anime_voice = data.get('anime_voice', 'none') # Can be 'none' or 'mahiru'

    if voice_key not in VOICES:
         return jsonify({"error": "Invalid base voice selected"}), 400
    
    voice_id = VOICES[voice_key]
    
    # Generate a unique filename
    base_filename = f"{uuid.uuid4()}_base.mp3"
    final_filename = f"{uuid.uuid4()}_final.mp3"
    
    base_filepath = os.path.join(AUDIO_DIR, base_filename)
    final_filepath = os.path.join(AUDIO_DIR, final_filename)
    
    # We use asyncio to run the edge-tts generation
    async def _generate_audio():
        communicate = edge_tts.Communicate(text, voice_id)
        await communicate.save(base_filepath)
    
    try:
        # Step 1: Generate Base TTS Audio
        asyncio.run(_generate_audio())
        
        # Step 2: Apply RVC if requested
        if anime_voice == 'mahiru':
            convert_voice(base_filepath, final_filepath)
            # We serve the final (cloned) file
            serve_filename = final_filename
            # Cleanup base if you want, but leaving it is fine for debugging.
        else:
            # If no anime voice, serve the base TTS directly
            serve_filename = base_filename

        return jsonify({
            "success": True, 
            "audio_url": f"/audio/{serve_filename}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)