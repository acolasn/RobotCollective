import threading
import queue
import chat_commanding
import chat_driving
import QR.capture_stream_with_downsampling_and_read_qr.

# Create a new queue
data_queue_motor = queue.Queue()
data_queue_qr = queue.Queue()


# Create two threads
t1 = threading.Thread(target= chat_commanding.openAI_driver, args=(data_queue,))
t2 = threading.Thread(target= chat_driving.chat_driver, args=(data_queue,))
t2 = threading.Thread(target= chat_driving.chat_driver, args=(data_queue,))


# Start the threads
t1.start()
t2.start()

# Wait for both threads to complete
t1.join()
t2.join()

print("Done!")