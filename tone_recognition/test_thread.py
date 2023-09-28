import threading
import queue
import main as tone_recognition

# Create a new queue
recorded_audio_queue = queue.Queue()
audio_command_queue = queue.Queue()
audio_command_queue.put('HEARME')

# audio commands
# 'HEARME'
# 'SPEAK'

# motor commands
# 'SEARCH'

t4 = threading.Thread(
    target=tone_recognition.recognize_speech, args=(recorded_audio_queue, audio_command_queue))

# Start the threads
t4.start()

# Wait for both threads to complete
t4.join()
print("Done!")
