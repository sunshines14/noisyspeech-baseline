import struct
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import wave
import os

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


def find_mValue(ratioArr) :
    beepArr = []
    lastArr = []
    tmpArr = []
    tmp2Arr = [] 
    inx = 0
    t = 0
    IsBeep = False 

    for value in ratioArr :

        inx = ratioArr.index(value)
        t = inx + 1
        
        tmpArr = ratioArr[inx-5 : inx]
        tmp2Arr = ratioArr[inx : inx+5]
        det1 = 0
        det2 = 0

        for x in tmpArr :
            if x>= 100 :
                det1 = det1 + 1 
        for x in tmp2Arr :
            if x>= 100 :
                det2 = det2 + 1 

        if (det1 == 0) and (det2 == 5) and (value >= float(100)) :
            IsBeep = True
            beepArr.append(t) # 시작값

        #elif (det1 != 0) and (IsBeep == True) and (value >= float(100)) : 
            #beepArr.append(t)

        elif (IsBeep == True) and (value < float(100)) :
            if det1 >= 3 :
                beepArr.append(t) # 끝값
            else :
                IsBeep = False
                beepArr.pop()
                beepArr.append('\n')
                lastArr.append((len(beepArr) - 1))

    mValueArr = []
    p1 = 0
    p2 = 0
    mValue = 0
    fst = 0

    for x in lastArr :
        if fst == 0 :
            p1 = 160 * (beepArr[0:x][0]) 
            p2 = 160 * (beepArr[0:x][-1])
            mValue = (p1 + p2) / 2 
            mValueArr.append(mValue)
            fst = x
        else :
            p1 = 160 * (beepArr[fst+1:x][0])
            p2 = 160 * (beepArr[fst+1:x][-1])
            mValue = (p1 + p2) / 2
            mValueArr.append(mValue)
            fst = x
    
    return mValueArr

def set_path() :
    #path = raw_input("path : ")
    path = "/home/antman/soonshin/corpus"
    path.replace("\\", "\\\\")

    return path


def set_files(path) :
    infiles = []
    
    for root, dirs, files in os.walk(path) :
        for f in files :
            ext = os.path.splitext(f)[-1]
            if (ext == '.wav') and (f != 'beep_processed.wav') :
                infiles.append(f)
 
    infiles.sort()

    return infiles


def seg_corpus(mValueArr, infiles) :
    n = 0
    p1 = 0
    p2 = 0
    length = 0
    tmp = 0

    while n < (len(mValueArr) - 1) :
        p1 = mValueArr[n] + 24000 
        p2 = mValueArr[n+1] - 24000
        length = p2 - p1

        inFile = wave.open("output_434_sort_rec.wav", 'rb')
        inFile.setpos(p1)
        tmp = inFile.readframes(length)

        outName = str(infiles[n])
        outFile = wave.open(outName, 'wb')
        outFile.setnchannels(1)
        outFile.setsampwidth(2)
        outFile.setframerate(16000)
        outFile.writeframes(tmp)

        #print "corpus %s : %d ~ %d\n" % (infiles[n], p1, p2) 
        n = n+1

        inFile.close()
        outFile.close()



iArr = get_index(f)
vArr, v2Arr = get_value(iArr, f, Sxx)
ratioArr = get_ratio(vArr, v2Arr)
#for result in ratioArr :
#    print result

path = set_path() 
infiles = set_files(path)
mValueArr = find_mValue(ratioArr)
seg_corpus(mValueArr, infiles)

ff.close()


