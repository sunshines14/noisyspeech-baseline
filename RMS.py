import wave
import struct
import math

# Mono, 2byte, 16,000 sample rate

f = wave.open('result2.wav', 'rb')
length = f.getnframes() # get sample 
dataArr = []

nRead = 1

for i in range(0, length) :
    waveData = f.readframes(1)
    data = struct.unpack("<h", waveData)
    dataArr.append(data[0])
    
 
currentLength = 0 

while currentLength < length :
    tempArr = [ 0 for i in range(1600) ]
    
    for i in range(currentLength, currentLength + 1600) :
    
        a = dataArr[i]
        b = pow(a,2) 
        tempArr[i-(currentLength)] = b

    sumValue = 0
    tempLength = len(tempArr)
    for j in range(tempLength) : 
        sumValue = sumValue + tempArr[j]
             
    c = sumValue / 1600         
    RMS = math.sqrt(c)     
    print (RMS)
    
    currentLength = currentLength + 160 # 10m/s
    
f.close()
        
        

    
    
    




