import xml.etree.ElementTree as ElementTree
import mido
import win32ui


class Key:
    def __init__(self, type, pitch, velocity, tick):
        self.type = type
        self.pitch = pitch
        self.velocity = velocity
        self.tick = tick
        self.interval = 0


class BPM:
    def __init__(self, time, value):
        self.time = time
        self.value = value


key_num = 0
key_list = []
bpm_list = []

dlg = win32ui.CreateFileDialog(1)  # 1表示打开文件对话框
dlg.SetOFNInitialDir('C:/Users/56223/Music/music')  # 设置打开文件对话框中的初始显示目录
dlg.DoModal()

file_name = dlg.GetPathName()  # 获取选择的文件名称
tree = ElementTree.parse(file_name)
root = tree.getroot()
header = tree.find('header')
bpm = float(header.find('first_bpm').text) / 100000

event_data = tree.find('event_data')
for event in event_data:
    time = round(int(event.find("start_timing_msec").text) / 1000)
    value = round(int(event.find("value").text) / 100000)
    if value == 0:
        continue
    else:
        bpm_list.append(BPM(time, value))

note_data = tree.find('note_data')
bpm_num = 0
for note in note_data:
    sub_note_data = note.find('sub_note_data')
    for sub_note in sub_note_data:
        time_start = float(sub_note.find('start_timing_msec').text) / 1000
        time_end = float(sub_note.find('end_timing_msec').text) / 1000
        pitch = int(sub_note.find('scale_piano').text) + 12 + 8
        velocity = int(sub_note.find('velocity').text)
        track_index = int(sub_note.find('track_index').text)

        key_num += 1
        # if len(bpm_list) > 1:
        #     if time_start > bpm_list[bpm_num].time and time_start > bpm_list[bpm_num + 1].time:
        #         bpm_num += 1
        key_list.append(Key('note_on', pitch, velocity,
                            round(time_start * 480 * bpm / 60)))
        key_list.append(Key('note_off', pitch, velocity,
                            round(time_end * 480 * bpm / 60)))

key_list.sort(key=lambda key: key.tick)
key_list[0].interval = key_list[0].tick
for i in range(1, len(key_list)):
    key_list[i].interval = key_list[i].tick - key_list[i - 1].tick

mid = mido.MidiFile()
track = mido.MidiTrack()
track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm)))
# for i in bpm_list:
#     track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(i.value), time=round(i.time * 480 * i.value / 60)))
mid.tracks.append(track)

for key in key_list:
    track.append(mido.Message(type=key.type, note=key.pitch, velocity=key.velocity, time=key.interval))

mid.save(dlg.GetPathName() + '.mid')

print(f'notes: {len(note_data)}')
print(f'keys:  {key_num}')
