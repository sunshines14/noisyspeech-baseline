import os 
import sys
import wave


def User(start_pt, time_user) : 
    infiles = [] 

    time_user = time_user.split("/")
    time_length = (int(time_user[0])*3600) + (int(time_user[1])*60) + (int(time_user[2]))

    with open("list_all.txt", "r") as path_list :
        for path in path_list.readlines() : 
            infiles.append(path.splitlines()[0])

    return infiles, start_pt, time_length


def Set(infiles, start_pt, time_length) :
    mergeArr = []
    sum_samples = 1008000 # beep(3s) 48000, slience(60s) 960000
    start = infiles.index(start_pt)
    mergeArr = infiles[start:]

    for f in mergeArr : 
        ff = wave.open(f, "rb")
        samples = ff.getnframes() 
        sum_samples = sum_samples + samples + 48000
        ff.close

        if (sum_samples/16000) >= time_length :
            end = mergeArr.index(f)
            mergeArr = mergeArr[:end]
            break

    tmp = open("list_merge.txt", "w")
    for f in mergeArr :
        tmp.write(f)
        tmp.write("\n")

    return mergeArr


def Merge(mergeArr, outFile_name) :
    dataArr = []
    sFile = wave.open("slience.wav", "rb")
    slience = [sFile.getparams(), sFile.readframes(sFile.getnframes())]
    dataArr.append(slience)

    bFile = wave.open("beep.wav", "rb")
    beep = [bFile.getparams(), bFile.readframes(bFile.getnframes())]
    dataArr.append(beep) 

    for f in mergeArr :
        inFile = wave.open(f, "rb")
        dataArr.append([inFile.getparams(), inFile.readframes(inFile.getnframes())])
        dataArr.append(beep)

        inFile.close()
        
    sFile.close()
    bFile.close()

    outFile = wave.open(outFile_name, "wb")
    outFile.setnchannels(1)
    outFile.setsampwidth(2)
    outFile.setframerate(16000)
    outFile.setparams(dataArr[0][0])

    for f in dataArr :
        outFile.writeframes(f[1])

    outFile.close()


def Main() :
    infiles, start_pt, time_length = User(sys.argv[1], sys.argv[2])
    mergeArr = Set(infiles, start_pt, time_length)
    Merge(mergeArr, sys.argv[3]) 
    print "Completed (%d)" % (len(mergeArr))

Main()
