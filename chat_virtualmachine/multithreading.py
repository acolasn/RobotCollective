import threading
import queue
import chat_commanding
import chat_driving


# Create a new queue
data_queue = queue.Queue()

# Create two threads
t1 = threading.Thread(target=chat_commanding.openAI_driver, args=(data_queue,))
t2 = threading.Thread(target=chat_driving.chat_driver, args=(data_queue,))

# Start the threads
t1.start()
t2.start()

# Wait for both threads to complete
t1.join()
t2.join()

print("Done!")