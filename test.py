import requests
import json
import time

audio_path = ".data/test.mp3"
url = "http://localhost:8002/start"

with open(audio_path, "rb") as f:
    files = {"audio": f}
    response = requests.post(url, files=files)

if response.status_code != 200:
    print("Failed to start transcription:", response.text)
    exit(1)

job_id = response.json()["job_id"]
print("Job started:", job_id)

# Poll for status
status_url = f"http://localhost:8002/status/{job_id}"

while True:
    status_response = requests.get(status_url)
    if status_response.status_code != 200:
        print("Failed to get status:", status_response.text)
        exit(1)
    status_data = status_response.json()
    if status_data["status"] == "completed":
        print("Transcription completed.")
        with open(".data/example.json", "w") as out:
            json.dump(status_data["result"], out, indent=2)
        print("Transcript saved to .data/example.json")
        break
    elif status_data["status"] == "failed":
        print("Transcription failed:", status_data.get("error"))
        break
    else:
        print("Status:", status_data["status"])
        time.sleep(2)