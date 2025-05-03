import argparse
import requests

def main():
    parser = argparse.ArgumentParser(description='Test the audio transcription API')
    parser.add_argument('audio_file', help='Path to the audio file to transcribe')
    args = parser.parse_args()

    # Prepare the file for upload
    files = {'audio': open(args.audio_file, 'rb')}

    # Send the request to the API
    response = requests.post('http://localhost:8001/transcribe', files=files)

    # Process the response
    if response.status_code == 200:
        result = response.json()
        print(f"\nTranscription:")
        print("-" * 80)
        print(result['transcription'])
        print("-" * 80)
        print(f"\nDetected Language: {result['language']}")
        print("\nSegments with timestamps:")
        print("-" * 80)
        for segment in result['segments']:
            print(f"[{segment['start']:.2f} - {segment['end']:.2f}]: {segment['text'].strip()}")
        print("-" * 80)
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

if __name__ == '__main__':
    main()
