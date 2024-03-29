from pydub import AudioSegment
import os

class SoundSystem:
    def __init__(self, agents_count):
        self.agents_count = agents_count
        self.sounds = [AudioSegment.silent(duration=0)] * agents_count
        self.ticks = [0] * agents_count

        self.path = os.path.join(os.path.dirname(__file__), '../assets/sounds/')

        self.audio = {}
        self.audio['zombie_hurt'] = AudioSegment.from_file(self.path + 'zombie_hurt.ogg')
        self.audio['dirt_break'] = AudioSegment.from_file(self.path + 'dirt_break.ogg')

    def get(self, id, last_tick, cur_tick, events):
        assert(id >= 0 and id < self.agents_count), "id should be in the range of [0, agents_count)"

        # Make sure the length of the sound >= (cur_tick - last_tick) * 50 * 2
        if len(self.sounds[id]) == 0 or self.ticks[id] + len(self.sounds[id]) < last_tick:
            self.sounds[id] = AudioSegment.silent(duration=(cur_tick - last_tick) * 50 * 2)
            self.ticks[id] = last_tick
        elif self.ticks[id] < last_tick:
            self.sounds[id] = self.sounds[id][(last_tick - self.ticks[id]) * 50:]
            self.ticks[id] = last_tick
        
        if len(self.sounds[id]) < (cur_tick - last_tick) * 50 * 2:
            self.sounds[id] += AudioSegment.silent(duration=(cur_tick - last_tick) * 50 * 2 - len(self.sounds[id]))

        # Update the sound
        for event in events:
            audio = None
            if event['type'] == 'entityHurt':
                if event['entity_name'] == 'zombie':
                    audio = self.audio['zombie_hurt']
            elif event['type'] == 'blockIsBeingBroken':
                audio = self.audio['dirt_break']
            
            if audio is not None:
                self.__update(id, last_tick, cur_tick, event['tick'], audio)
        
        assert(len(self.sounds[id]) >= (cur_tick - last_tick) * 50), "sound length should be greater than or equal to (cur_tick - last_tick) * 50"

        ret = self.sounds[id][: (cur_tick - last_tick) * 50]
        self.sounds[id] = self.sounds[id][(cur_tick - last_tick) * 50:]

        return ret
    
    def __update(self, id, last_tick, cur_tick, tick, audio):
        assert(last_tick <= tick and tick <= cur_tick), "tick should be in the range of [last_tick, cur_tick]"

        self.sounds[id] = self.sounds[id].overlay(audio, position=(tick - last_tick) * 50)

