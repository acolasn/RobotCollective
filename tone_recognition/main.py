from hearme import HearMe
from understandme import UnderstandMe


def recognize_speech(data_queue, command_queue):
    while True:
        if command_queue.queue[-1] == 'HEARME':
            HearMe()
            transcript = UnderstandMe()
            data_queue.put(transcript)
            command_queue.put('SPEAK')


if __file__ == "__main__":
    print('hear me')
    HearMe()
    print('here me done. now understand me')
    UnderstandMe()
    print('understand me done')
