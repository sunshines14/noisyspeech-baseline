import struct
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

ff=open('result2.wav', 'rb')

a=ff.read(320000)
h = ''
for i in range(0, 160000):
    h = h+'h'


aa = struct.unpack(h, a)

npa=np.asarray(aa, dtype=np.float32)

# print npa
# print npa.shape

aaa=np.fft.fft(npa, n=512)
# print aaa
# print aaa.shape

freq = np.fft.fftfreq(aaa.shape[-1])

fs = 16e3
N = 160e3
amp = 2 * np.sqrt(2)
noise_power = 0.01 * fs / 2
time = np.arange(N) / float(fs)
mod = 500*np.cos(2*np.pi*0.25*time)
carrier = amp * np.sin(2*np.pi*3e3*time + mod)
noise = np.random.normal(scale=np.sqrt(noise_power), size=time.shape)
noise *= np.exp(-time/5)
x = carrier + noise

f, t, Sxx = signal.spectrogram(npa, fs, nperseg=512, noverlap=352, nfft=512, return_onesided=True)
# plt.pcolormesh(t, f, Sxx)
# plt.ylabel('Frequency [Hz]')
# plt.xlabel('Time [sec]')
# plt.show()
print f
print f.shape
print t
print t.shape
print Sxx.shape
print Sxx[100]

ff.close()