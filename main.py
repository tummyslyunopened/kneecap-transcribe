from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Text, DateTime
from threading import Thread
from datetime import datetime
import tempfile
import whisper
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///jobs.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
model = whisper.load_model("base")


# Define the Job model
class Job(db.Model):
    id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    audio_path = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)


# Initialize the database
with app.app_context():
    db.create_all()


# Background worker to process jobs
def process_job(job_id):
    with app.app_context():
        job = Job.query.get(job_id)
        if not job:
            return

        try:
            # Update status to processing
            job.status = "processing"
            job.updated_at = datetime.now()
            db.session.commit()

            # Process transcription
            result = model.transcribe(job.audio_path, verbose=False)
            transcription = result["text"]
            segments = result["segments"]

            # Update job with results
            job.status = "completed"
            job.result = json.dumps(
                {
                    "transcription": transcription,
                    "language": result["language"],
                    "segments": [
                        {
                            "text": segment["text"],
                            "start": segment["start"],
                            "end": segment["end"],
                        }
                        for segment in segments
                    ],
                }
            )
            job.updated_at = datetime.now()
            db.session.commit()

        except Exception as e:
            # Update job with error
            job.status = "failed"
            job.error = str(e)
            job.updated_at = datetime.now()
            db.session.commit()


@app.route("/start", methods=["POST"])
def start_transcription():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    if audio_file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Generate unique job ID
    job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Save audio file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        audio_file.save(temp_file.name)
        audio_path = temp_file.name

    # Create job record
    job = Job(
        id=job_id,
        status="queued",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        audio_path=audio_path,
    )
    db.session.add(job)
    db.session.commit()

    # Start processing in background
    Thread(target=process_job, args=(job_id,)).start()

    return jsonify(
        {"job_id": job_id, "status": "queued", "created_at": job.created_at.isoformat()}
    )


@app.route("/status/<job_id>", methods=["GET"])
def get_job_status(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    response = {
        "job_id": job.id,
        "status": job.status,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }

    if job.result:
        response["result"] = json.loads(job.result)
    if job.error:
        response["error"] = job.error

    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8001)

