import argparse
import json
import os
import whisper

def transcribe_file(input_file, output_file):
    # Load the Whisper model
    model = whisper.load_model("base")

    # Transcribe the audio file
    result = model.transcribe(input_file, verbose=False)

    # Prepare the output JSON
    transcription_data = {
        "transcription": result["text"],
        "language": result["language"],
        "segments": [
            {
                "text": segment["text"],
                "start": segment["start"],
                "end": segment["end"],
            }
            for segment in result["segments"]
        ],
    }

    # Write the JSON to the output file
    with open(output_file, "w") as f:
        json.dump(transcription_data, f, indent=4)

    print(f"Transcription saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe an audio file and save the result as JSON.")
    parser.add_argument("input_file", help="Path to the input audio file.")
    parser.add_argument("output_file", help="Path to the output JSON file.")

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Error: Input file {args.input_file} does not exist.")
        exit(1)

    transcribe_file(args.input_file, args.output_file)