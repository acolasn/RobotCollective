import pyaudio
import numpy as np
from scipy.signal import butter, lfilter
import wave
import time

# Set sound recording format
CHUNK = 1600                # Buffer size
FORMAT = pyaudio.paInt16    # Data type
CHANNELS = 1                # Number of channels
RATE = 16000                # Sample rate (Hz)

# Bandpass filter parameters
LOWCUT = 150                # Low cutoff frequency (Hz)
HIGHCUT = 4000              # High cutoff frequency (Hz)

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

# Initialize variables for recording and note detection
recording = False
frames = []
recording_in_progress = False  # New variable to track recording status

# Target note frequencies with tolerance
TARGET_FREQUENCIES = [(439, 1), (523, 1), (554,1), (587, 1), (622,1), (659, 1), (698, 1), (739, 1.5), (783,3), (830,1)]  # B,C, D, D sharp, E, F, G

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
    783: ("Francesca","francesca.wav"),
    830: ("Masahiro", "masahiro.wav")
}


# Initialize the detected person and WAV file name
detected_person = None
detected_wav_file = None

# Initialize variables for tone detection and recording start time
detected_tone = None
start_time = None
continuous_tone_start_time = None  # New variable to track continuous tone start time

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
    recording_duration = 0
    max_recording_time = 90  # Maximum recording time (in seconds)

    while True:
        # Read audio data from the stream
        raw_data = stream.read(CHUNK)
        audio_data = np.frombuffer(raw_data, dtype=np.int16)

        # Apply the bandpass filter to the audio data
        filtered_audio_data = apply_bandpass_filter(audio_data)

        # Calculate the average frequency of the filtered audio
        average_freq = calculate_average_frequency(filtered_audio_data)

        # Check if the frequency matches one of the target frequencies with tolerance
        matching_target = None
        for target_freq, tolerance in TARGET_FREQUENCIES:
            if abs(average_freq - target_freq) <= tolerance:
                matching_target = target_freq
                break

        if matching_target is not None:
            # Detected a tone within tolerance
            if detected_tone == matching_target:
                # Continuous tone detected
                if start_time is None:
                    start_time = time.time()
                    continuous_tone_start_time = time.time()  # Set continuous tone start time
                elif time.time() - start_time >= 2:
                    # Start recording if tone has been continuous for 2 seconds
                    if not recording_in_progress:
                        detected_person, detected_wav_file = PEOPLE[matching_target]
                        print(f"Recording started for {detected_person}...")
                        frames = []  # Clear frames
                        recording = True
                        recording_in_progress = True  # Set recording status to True
                        start_time = time.time()  # Reset the start time
            else:
                # New tone detected
                detected_tone = matching_target
                start_time = time.time()
                if recording_in_progress:
                    print("Recording stopped due to continuous tone...")
                    print(f"You are listening to {detected_person}")

                    # Save the recorded audio to the corresponding WAV file
                    if detected_wav_file is not None:
                        wf = wave.open(detected_wav_file, 'wb')
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(2)
                        wf.setframerate(RATE)
                        wf.writeframes(b''.join(frames))
                        wf.close()

                    recording_in_progress = False  # Set recording status to False
                    recording = False

                    # Save the last detected person to the text file
                    if detected_person is not None:
                        with open(last_person_file, 'w') as file:
                            file.write(detected_person)
                    detected_person = None
                    detected_wav_file = None
        else:
            # No tone detected
            detected_tone = None
            start_time = None

        if recording:
            frames.append(raw_data)  # Record audio

            # Check for continuous tone and stop recording if detected for 2 seconds
            if continuous_tone_start_time is not None and time.time() - continuous_tone_start_time >= 2:
                print("Recording stopped due to continuous tone...")
                print(f"You are listening to {detected_person}")

                # Save the recorded audio to the corresponding WAV file
                if detected_wav_file is not None:
                    wf = wave.open(detected_wav_file, 'wb')
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(2)
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))
                    wf.close()

                recording_in_progress = False  # Set recording status to False
                recording = False
                detected_person = None
                detected_wav_file = None

        # Update recording duration
        if recording_in_progress and start_time is not None:
            recording_duration = time.time() - start_time

        # Check for maximum recording time (90 seconds)
        if recording_duration >= max_recording_time:
            print("Recording stopped after 90 seconds...")
            print(f"You are listening to {detected_person}")

            # Save the recorded audio to the corresponding WAV file
            if detected_wav_file is not None:
                wf = wave.open(detected_wav_file, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()

            recording_in_progress = False  # Set recording status to False
            recording = False
            detected_person = None
            detected_wav_file = None

except KeyboardInterrupt:
    pass

finally:
    if recording_in_progress:
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