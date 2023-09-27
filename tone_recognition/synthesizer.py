import pyaudio
import numpy as np

# Define the parameters for the tone generation
frequency = 659  # Frequency in Hz (e.g., 440 Hz for A4)
duration = 2    # Duration in seconds
volume = 0.5    # Volume (0.0 to 1.0)

#Choose your frequency, duration must be 2s at start
#    439: ("Arya", "arya.wav"),
#    523: ("Antonio", "antonio.wav"),
#    554: ("Vince", 'vince.wav'),
#    587: ("Meg", "meg.wav"),
#    622: ("Vasco", "vasco.wav"),
#    659: ("Cris", "cris.wav"),
#    698: ("Orsi", "orsi.wav"),
#    739: ('Bariscan', 'bariscan.wav'),
#    783: ("Francesca","francesca.wav"),
#   830: ("Masahiro", "masahiro.wav")

# Use a higher sample rate and bit depth for a purer tone
sample_rate = 96000  # Standard audio sample rate (samples per second)
bit_depth = 24  # Bit depth for the waveform (16 bits is common)

# Calculate the number of samples needed
num_samples = int(sample_rate * duration)

# Generate the time values for the waveform
t = np.linspace(0, duration, num_samples, endpoint=False)

# Generate the sine wave at the specified frequency
tone = volume * np.sin(2 * np.pi * frequency * t)

# Scale the waveform to the specified bit depth
tone = np.int16(tone * (2**15 - 1))


# Initialize PyAudio
p = pyaudio.PyAudio()

# Open a stream to play the tone
stream = p.open(format=pyaudio.paInt16,  # Use 16-bit audio format
                channels=1,
                rate=sample_rate,
                output=True)

# Play the tone
stream.start_stream()
stream.write(tone.tobytes())
stream.stop_stream()
stream.close()

# Terminate PyAudio
p.terminate()
