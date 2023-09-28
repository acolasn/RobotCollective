import threading
import queue
import speech.chat_commanding as chat_commanding
import speech.chat_driving as chat_driving
import QR.main_w_queue as main

# Create a new queue
data_queue = queue.Queue()

# Create two threads
t1 = threading.Thread(target= chat_commanding.openAI_driver, args=(data_queue,))
t2 = threading.Thread(target= chat_driving.chat_driver, args=(data_queue,))
t3 = threading.Thread(target= main.run_qr_detection, args= (data_queue,))

# Start the threads
t1.start()
t2.start()
t3.start()

# Wait for both threads to complete
t1.join()
t2.join()
t3.join()
print("Done!")