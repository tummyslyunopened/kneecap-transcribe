from flask import Flask, request, jsonify
import tempfile
import whisper
import sqlite3
from threading import Thread
from datetime import datetime
import json

app = Flask(__name__)
model = whisper.load_model("base")

# Create jobs database if it doesn't exist
def init_db():
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            audio_path TEXT,
            result TEXT,
            error TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Background worker to process jobs
def process_job(job_id):
    # Create app context for the thread
    with app.app_context():
        conn = sqlite3.connect('jobs.db')
        c = conn.cursor()
        
        # Get job details
        c.execute('SELECT audio_path FROM jobs WHERE id = ?', (job_id,))
        result = c.fetchone()
        if not result:
            conn.close()
            return
        
        audio_path = result[0]
        
        try:
            # Update status to processing
            c.execute('''
                UPDATE jobs 
                SET status = 'processing', 
                    updated_at = ? 
                WHERE id = ?
            ''', (datetime.now(), job_id))
            conn.commit()
            
            # Process transcription
            result = model.transcribe(audio_path, verbose=False)
            transcription = result["text"]
            segments = result["segments"]
            
            # Update job with results
            c.execute('''
                UPDATE jobs 
                SET status = 'completed', 
                    result = ?,
                    updated_at = ? 
                WHERE id = ?
            ''', (
                json.dumps({
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
                }),
                datetime.now(),
                job_id
            ))
            conn.commit()
            
        except Exception as e:
            # Update job with error
            c.execute('''
                UPDATE jobs 
                SET status = 'failed', 
                    error = ?,
                    updated_at = ? 
                WHERE id = ?
            ''', (str(e), datetime.now(), job_id))
            conn.commit()
        finally:
            conn.close()

@app.route('/start', methods=['POST'])
def start_transcription():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Generate unique job ID
    job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Save audio file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        audio_file.save(temp_file.name)
        audio_path = temp_file.name
    
    # Create job record
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO jobs (id, status, created_at, updated_at, audio_path)
        VALUES (?, 'queued', ?, ?, ?)
    ''', (job_id, datetime.now(), datetime.now(), audio_path))
    conn.commit()
    conn.close()
    
    # Start processing in background
    Thread(target=process_job, args=(job_id,)).start()
    
    return jsonify({
        'job_id': job_id,
        'status': 'queued',
        'created_at': datetime.now().isoformat()
    })

@app.route('/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT status, result, error, created_at, updated_at 
        FROM jobs 
        WHERE id = ?
    ''', (job_id,))
    
    result = c.fetchone()
    conn.close()
    
    if not result:
        return jsonify({'error': 'Job not found'}), 404
    
    status, result_json, error, created_at, updated_at = result
    
    response = {
        'job_id': job_id,
        'status': status,
        'created_at': created_at,
        'updated_at': updated_at
    }
    
    if result_json:
        response['result'] = json.loads(result_json)
    if error:
        response['error'] = error
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
