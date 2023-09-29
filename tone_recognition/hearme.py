import pyaudio
import numpy as np
from scipy.signal import butter, lfilter
import wave
import time
import queue

# Set sound recording format
CHUNK = 1600                # Buffer size
FORMAT = pyaudio.paInt16    # Data type
CHANNELS = 1                # Number of channels
RATE = 16000                # Sample rate (Hz)

# Bandpass filter parameters
LOWCUT = 150                # Low cutoff frequency (Hz)
HIGHCUT = 4000              # High cutoff frequency (Hz)

TARGET_FREQUENCIES = [(439, 3), (523, 3), (554, 3), (587, 3), (622, 3), (
    659, 3), (698, 3), (739, 3), (783, 3), (830, 3)]  # B,C, D, D sharp, E, F, G

# Map target frequencies to people and their corresponding WAV file names
PEOPLE = {
    439: ("Arya", "arya.wav"),
    523: ("Antonio", "antonio.wav"),
    554: ("Vince", 'vince.wav'),
    587: ("Meg", "meg.wav"),
    622: ("Vasco", "vasco.wav"),
    659: ("Cris", "cris.wav"),
    698: ("Orsi", "orsi.wav"),
    739: ('Bariscan', 'bariscan.wav'),
    783: ("Francesca", "francesca.wav"),
    830: ("Masahiro", "masahiro.wav")
}

# Initialize PyAudio
pya = pyaudio.PyAudio()

# Function to apply a bandpass filter to the audio data


def apply_bandpass_filter(audio_data):
    # Normalize the audio data
    audio_data = audio_data / 32768.0

    # Design a bandpass filter using Butterworth filter design
    nyquist = 0.5 * RATE
    low = LOWCUT / nyquist
    high = HIGHCUT / nyquist
    b, a = butter(5, [low, high], btype='band')

    # Apply the filter
    filtered_audio = lfilter(b, a, audio_data)

    # Scale the filtered audio back to 16-bit integer range
    filtered_audio = (filtered_audio * 32768.0).astype(np.int16)

    return filtered_audio


def calculate_average_frequency(filtered_audio_data, num_ffts=5):
    # Initialize variables to store cumulative FFT data
    cumulative_fft = np.zeros(len(filtered_audio_data))

    for _ in range(num_ffts):
        # Apply a Hamming window to the audio data
        hamming_window = np.hamming(len(filtered_audio_data))
        windowed_audio = filtered_audio_data * hamming_window

        # Perform FFT
        fft_data = np.fft.fft(windowed_audio)
        cumulative_fft += np.abs(fft_data)

    # Average the FFT results
    average_fft = cumulative_fft / num_ffts

    # Calculate the frequency values corresponding to each point in the FFT
    frequencies = np.fft.fftfreq(len(average_fft), 1 / RATE)

    # Find the frequency with the maximum magnitude
    max_magnitude_index = np.argmax(np.abs(average_fft))
    average_frequency = np.abs(frequencies[max_magnitude_index])

    return average_frequency


def start_recording(matching_target, command_queue):
    command_queue.put('LISTEN')
    detected_person, detected_wav_file = PEOPLE[matching_target]
    print(
        f"Recording started for {detected_person}...")
    frames = []  # Clear frames
    recording = True
    record_starting_time = time.time()
    return frames, recording, record_starting_time, detected_person, detected_wav_file


def stop_recording(detected_wav_file, frames):
    print("Recording stopped due to continuous tone.")
    # print(f"You are listening to {detected_person}")

    # Save the recorded audio to the corresponding WAV file
    if detected_wav_file is not None:
        wf = wave.open(detected_wav_file, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
    # elif detected_wav_file is None:
    #     recording=False
    recording = False
    detected_person = None
    detected_wav_file = None

    return recording, detected_person, detected_wav_file


def HearMe(command_queue=None):
    """
    record audio and save it to a WAV file
    """
    if not command_queue:
        command_queue = queue.Queue()
    # Initialize variables for recording and note detection
    recording = False
    frames = []

    # Target note frequencies with tolerance

    # Initialize the detected person and WAV file name
    detected_person = None
    detected_wav_file = None

    # Initialize variables for tone detection and recording start time
    detected_tone = None
    start_time = None
    # New variable to track continuous tone start time
    continuous_tone_start_time = None

    # Initialize the path to the last person text file
    last_person_file = "last_person.txt"
    try:
        # Open audio stream (from default device)
        stream = pya.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          start=False,
                          frames_per_buffer=CHUNK)

        # Start streaming audio
        stream.start_stream()

        # Initialize variables for recording duration and maximum recording time
        record_starting_time = 0
        max_recording_time = 60  # Maximum recording time (in seconds)

        while True:
            # Read audio data from the stream

            raw_data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(raw_data, dtype=np.int16)

            # Apply the bandpass filter to the audio data
            filtered_audio_data = apply_bandpass_filter(audio_data)

            # Calculate the average frequency of the filtered audio
            average_freq = calculate_average_frequency(filtered_audio_data)
            #print(average_freq)

            # Check if the frequency matches one of the target frequencies with tolerance
            matching_target = None
            for target_freq, tolerance in TARGET_FREQUENCIES:
                if abs(average_freq - target_freq) <= tolerance:
                    matching_target = target_freq
                    break

            if matching_target:
                # Detected a tone within tolerance
                if detected_tone == matching_target:
                    # Continuous tone detected
                    if start_time is None:
                        start_time = time.time()
                    elif time.time() - start_time >= 1.5:
                        if not recording:
                            frames, recording, record_starting_time, detected_person, detected_wav_file = start_recording(
                                matching_target, command_queue)
                        else:  # is recording
                            recording, detected_person, detected_wav_file = stop_recording(
                                detected_wav_file, frames)
                            break
                        start_time = None
                else:
                    # New tone detected
                    detected_tone = matching_target
                    start_time = None
            else:
                # No tone detected
                detected_tone = None
                start_time = None

            if recording:
                frames.append(raw_data)  # Record audio
            else:  # not recording
                record_starting_time = 0

            # Check for maximum recording time (60 seconds)
            if time.time() - record_starting_time >= 60 and record_starting_time != 0:
                recording, detected_person, detected_wav_file = stop_recording(
                    detected_wav_file, frames)
                break

    except KeyboardInterrupt:
        pass

    finally:
        if recording:
            print("Recording stopped due to interruption...")
        if frames:
            # Stop recording and save the recorded audio
            stream.stop_stream()
            stream.close()

            wf = wave.open("speech.wav", 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

        pya.terminate()


if __name__ == "__main__":
    HearMe()
