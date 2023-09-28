import openai
import os


def UnderstandMe():
    """
    OpenAI whisper function
    """
    # Define your OpenAI API key (replace 'YOUR_API_KEY' with your actual API key)
    openai.api_key = "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"

    # Read the content of the 'last_person.txt' file
    with open('last_person.txt', 'r') as last_person_file:
        detected_person = last_person_file.read().strip()

    # Check if 'detected_person' is not empty
    if detected_person:
        # Convert the first letter of the detected person's name to lowercase
        detected_person = detected_person[0].lower() + detected_person[1:]

        # Construct the path to the most recently recorded audio file
        # Assumes WAV files are named after the person
        audio_file_path = f"{detected_person}.wav"

        # Check if the audio file exists before attempting to transcribe
        if os.path.exists(audio_file_path):
            # Open the audio file for reading in binary mode
            with open(audio_file_path, "rb") as audio_file:
                # Transcribe the audio using the Whisper model
                transcription = openai.Audio.transcribe(
                    "whisper-1", audio_file)['text']

                # Print the transcription
                print(f"Transcription for {detected_person}:")
                print(transcription)
            return transcription
        else:
            print(f"Audio file '{audio_file_path}' does not exist.")
            return None
    else:
        print("No person detected for transcription.")
        return None


if __name__ == "__main__":
    UnderstandMe()
