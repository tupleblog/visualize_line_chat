import line_utils
import numpy as np
from midiutil.MidiFile import MIDIFile


def generate_midi_text(file_name, output_file_name= 'midi.mid'):
    chats_dict = line_utils.read_line_chat(file_name)
    users = line_utils.get_users(chats_dict)
    chats_split = [line_utils.split_chat(chat, users) for (date, chat) in chats_dict['chats']]
    chats = [chat for (t, u, chat) in chats_split if chat is not None]
    chats_len = np.array([len(c) for c in chats])
    variations_round = np.array([int(v/10) for v in chats_len])

    # setting up MIDI
    track = 0
    time = 0
    channel = 0
    tempo = 120
    duration = 1
    volumn = 100
    base_pitch = 60
    midi = MIDIFile(numTracks=1, adjust_origin=time)
    midi.addTrackName(track, time, "testing")
    midi.addTempo(track, time, tempo)

    # add variation out of
    variations_round = base_pitch + (variations_round[0:100] + np.round(10 * np.random.randn(100)))

    # chord stuff
    for t, v in enumerate(list(variations_round)):
        midi.addNote(track, channel, int(v), t + 1, duration, volumn)
        midi.addNote(track, channel, int(v) + 4, t + 1, duration, volumn)
        midi.addNote(track, channel, int(v) + 7, t + 1, duration, volumn)

    with open(output_file_name, 'wb') as file:
        midi.writeFile(file)
    print('done converting to midi file!')
