from flask import Flask, request, jsonify
import tempfile
import whisper

app = Flask(__name__)

model = whisper.load_model("base")

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        audio_file.save(temp_file.name)
        result = model.transcribe(temp_file.name, verbose=False)
        transcription = result["text"]
        segments = result["segments"]
        
        return jsonify({
            'transcription': transcription,
            'language': result["language"],
            'segments': [
                {
                    'text': segment['text'],
                    'start': segment['start'],
                    'end': segment['end']
                }
                for segment in segments
            ]
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
