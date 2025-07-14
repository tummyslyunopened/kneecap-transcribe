import os
import json
import subprocess
import unittest

class TestCliTranscribe(unittest.TestCase):
    def setUp(self):
        self.input_file = ".data/test-cli.mp3"
        self.output_file = "test_output.json"

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_transcription_output(self):
        # Run the CLI script
        result = subprocess.run(
            ["python", "cli_transcribe.py", self.input_file, self.output_file],
            capture_output=True,
            text=True
        )

        # Check if the script ran successfully
        self.assertEqual(result.returncode, 0, f"CLI failed with error: {result.stderr}")

        # Check if the output file was created
        self.assertTrue(os.path.exists(self.output_file), "Output file was not created.")

        # Validate the JSON structure of the output file
        with open(self.output_file, "r") as f:
            data = json.load(f)

        self.assertIn("transcription", data, "Missing 'transcription' key in output JSON.")
        self.assertIn("language", data, "Missing 'language' key in output JSON.")
        self.assertIn("segments", data, "Missing 'segments' key in output JSON.")
        self.assertIsInstance(data["segments"], list, "'segments' should be a list.")

if __name__ == "__main__":
    unittest.main()