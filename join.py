# -*- coding:utf-8 -*- 
# C:\Users\SLLap\Documents\python project

import os
import sys
import wave
import time 

def SetPath() :
    path = raw_input("path : ")
    path.replace("\\", "\\\\")
    
    return path


def SetFiles(path) :   
    infiles = []
    
    for root, dirs, files in os.walk(path) :
        for f in files :
            ext = os.path.splitext(f)[-1]
            if (ext == '.wav') and (f != 'beep_processed.wav') :
                infiles.append(f)
    infiles.sort()

    return infiles


def Merge(infiles) :
    dataArr = []
    
    #outfile = raw_input("file name : ")
    #outfile = outfile + ".wav"
    outfile = "join_output.wav"
    
    bFile = wave.open('beep_processed.wav', 'rb')
    beep = [bFile.getparams(), bFile.readframes(bFile.getnframes())]
    dataArr.append(beep)
        
    for infile in infiles :
        cFile = wave.open(infile, 'rb')   
        dataArr.append([cFile.getparams(), cFile.readframes(cFile.getnframes())])
        dataArr.append(beep)        
        
        cFile.close()
        
    bFile.close()
    output = wave.open(outfile, 'wb')  
        
    output.setnchannels(1)
    output.setsampwidth(2)
    output.setframerate(16000)  
    output.setparams(dataArr[0][0]) 
    
    for i in dataArr :
        output.writeframes(i[1])
    
    output.close() 
    
def Main() :
    count = 0
    #path = SetPath()
    path = "/home/antman/soonshin/join"
    infiles = SetFiles(path)
    for i in infiles :
        count = count + 1
        #print (i + '\n')
    Merge(infiles)
    print count 
Main()
