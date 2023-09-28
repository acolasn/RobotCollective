import threading
import queue
import speech.chat_commanding as chat_commanding
import speech.chat_driving as chat_driving

import QR.main_w_queue as main
import tone_recognition.main as tone_recognition

# Create a new queue
chatgpt_queue = queue.Queue()
recorded_audio_queue = queue.Queue()
command_queue = queue.Queue()
command_queue.put('SEARCH')
qr_queue = queue.Queue()

# audio commands
# 'LISTEN' : when hear the tone, stop the motor
# 'SPEAK' : after transcribing the detected audio, speak
# 'SEARCH' : search for robots

# Create two threads
t1 = threading.Thread(target= chat_commanding.openAI_driver_function, args=(chatgpt_queue, qr_queue))
t2 = threading.Thread(target= chat_driving.chat_driver, args=(chatgpt_queue, ))
t3 = threading.Thread(target= main.run_qr_detection, args= (qr_queue,))
t4 = threading.Thread(
    target=tone_recognition.recognize_speech, args=(recorded_audio_queue, command_queue))

# Start the threads
t1.start()
t2.start()
t3.start()
t4.start()

# Wait for both threads to complete
t1.join()
t2.join()
t3.join()
t4.join()
print("Done!")