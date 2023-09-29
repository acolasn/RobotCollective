from tone_recognition.hearme import HearMe
from tone_recognition.understandme import UnderstandMe

# comment out this when running __name__
# from hearme import HearMe
# from understandme import UnderstandMe


def recognize_speech(data_queue, command_queue):
    while True:
        if command_queue.queue[-1] == 'SEARCH':
            HearMe(command_queue)
            transcript = UnderstandMe()
            data_queue.put(transcript)
            command_queue.put('SPEAK')
        if command_queue.queue[-1] == 'SPEAK':
            print('speaking now so this thread is not doing anything')


if __name__ == "__main__":
    print('hear me')
    HearMe()
    print('hear me done. now understand me')
    transcript = UnderstandMe()
    print('understand me done : ', transcript)
