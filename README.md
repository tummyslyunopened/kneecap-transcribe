# kneecap-transcribe

A simple api to provide transcription services for the main Kneecap Project.

## Deployment Standard

By convention should be served ad subdomain transcribe.[kneecap_domain]

## Example Consumption 
```python
    # Prepare the file for upload
    files = {'audio': open(args.audio_file, 'rb')}

    # Send the request to the API
    response = requests.post('http://localhost:5000/transcribe', files=files)

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
```