import struct
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

ff=open('output_434_sort_rec.wav', 'rb')

a=ff.read(81117318)
h = ''
for i in range(0, 40558659) :
    h = h+'h'


aa = struct.unpack(h, a)

npa=np.asarray(aa, dtype=np.float32)

#print npa
#print npa.shape

aaa=np.fft.fft(npa, n=512)
#print aaa
#print aaa.shape

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
#print f
#print f.shape
#print t
#print t.shape
#print Sxx.shape

# ---------------------------------------------------------------------------------------------------------------------
def get_index(f) :
    iArr = []
    c = 0

    for i in f :
        
        if i == float(1000) or i == float(2000) or i == float(3000) or i == float(4000) or  i == float(5000) :
            iArr.append(c)   
            c = c+1
        else :
            c = c+1 
    
    return (iArr)


def get_value(iArr, f, Sxx) :
    c = 0
    vSum = 0
    v2Sum = 0
    vArr = []
    v2Arr = []

    fSh = f.shape
    tSh = t.shape

    l = len(iArr)
    l2 = int(fSh[0] - l)
    
    while c < tSh[0] :
        for x in range(fSh[0]) :
            tmp = Sxx[x][c]
            if x in iArr :
                vSum = np.add(vSum, tmp)
            else :
                v2Sum = np.add(v2Sum, tmp)
 
        vSum = np.divide(vSum, l)
        v2Sum = np.divide(v2Sum, l2)

        vArr.append(vSum)
        v2Arr.append(v2Sum)

        c = c+1
        
    return (vArr, v2Arr)


def get_ratio(vArr, v2Arr) :
    ratio = 0
    ratioArr = []
    
    for x in range(len(vArr)) :
        ratio = np.divide(vArr[x], v2Arr[x])
        ratioArr.append(ratio)
    
    return ratioArr


iArr = get_index(f)
vArr, v2Arr = get_value(iArr, f, Sxx)
ratioArr = get_ratio(vArr, v2Arr)
for result in ratioArr :
    print result

ff.close()
