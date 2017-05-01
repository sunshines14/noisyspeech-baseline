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
            if (ext == '.wav') and (f == 'beep') :
                infiles.append(f)
            
    return infiles


def Merge(infiles) :
    data = []
    
    outfile = raw_input("file name : ")
    outfile = outfile + ".wav"
    
    for infile in infiles:
        try :
            d = wave.open(infile, 'rb')
            b = wave.open('beepCode1.wav', 'rb')
            
            data.append([d.getparams(), d.readframes(d.getnframes())])
            data.append([b.getparams(), b.readframes(b.getnframes())])
            
            d.close()
            b.close()
            
        except IOError as e:
            print (e)

    output = wave.open(outfile, 'wb')
    
    try :
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(16000)
        output.setparams(data[0][0]) 
        
        for i in data :
            output.writeframes(i[1])
            
    except (IndexError, AttributeError) as e :   
        print (e)
    
    output.close()
    
    
def Main() :
    
    path = SetPath()
    infiles = SetFiles(path)
    for i in infiles :
        print (i + '\n')
    Merge(infiles)


Main()


