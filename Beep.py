import wave
import struct


bi = wave.open('beep_raw.wav', 'rb')
bo = wave.open('beep_processed.wav', 'wb')

sound = []
sample = bi.readframes(bi.getnframes())
sound.append(sample)

values = []

bo.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))

for i in range(0, 16000):
        
        value = 0
        
        packed_value = struct.pack('h', value)
        values.append(packed_value)

value_str = ''.join(values)
bo.writeframes(value_str)
bo.writeframes(sound[0])
bo.writeframes(value_str)

bi.close
bo.close


