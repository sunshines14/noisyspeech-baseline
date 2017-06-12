# /home/antman/soonshin/ui
import os
import sys
import wave

def User() :
    infiles = []

    #print "/home/antman/soonshin/ui_merge"
    #path = raw_input("path : ")

    start_pt = raw_input("start point : ")

    time_user = raw_input("time length(h/m/s) : ")
    time_user = time_user.split("/")

    time_length = (int(time_user[0])*3600) + (int(time_user[1])*60) + (int(time_user[2]))

    path_list = open("list_mk.txt", 'r')
    infiles = path_list.readlines() 
    
    with open("list_all.txt", 'r') as path_list :
        for path in path_list.readlines() :
            infiles.append(path.splitlines()[0])

    path_list.close()

    """
    for root, dirs, files in os.walk(path) :
        for f in files :
            ext = os.path.splitext(f)[-1]
            if (ext == '.wav') and (f != 'beep.wav') and (f != 'slience.wav') : 
                infiles.append(f)
  
    infiles.sort() 
    """

    return infiles, start_pt, time_length


def Set(infiles, start_pt, time_length) :
    mergeArr = []
    sum_samples = 1008000 # beep(3s) 48000, slience(60s) 960000
    start = infiles.index(start_pt)
    mergeArr = infiles[start:]
    
    """
    if Binary_Search(infiles, start_pt) == True :
        start = infiles.index(start_pt)
        mergeArr = infiles[start:]
    """ 

    for f in mergeArr :
        ff = wave.open(f, 'rb')
        samples = ff.getnframes()
        sum_samples = sum_samples + samples + 48000 
        ff.close()

        if (sum_samples/16000) >=  time_length :
            end = mergeArr.index(f)
            mergeArr = mergeArr[:end] 
            break 
    
    tmp = open("list_merge.txt", "w")
    for i in mergeArr :
       tmp.write(i)
       tmp.write("\n")

    return mergeArr 


def Merge(mergeArr) :
    dataArr = []
    outFile_name = raw_input("file name : ") 

    sFile = wave.open('slience.wav', 'rb')
    slience = [sFile.getparams(), sFile.readframes(sFile.getnframes())]
    dataArr.append(slience)
    
    bFile = wave.open('beep.wav', 'rb')
    beep = [bFile.getparams(), bFile.readframes(bFile.getnframes())]
    dataArr.append(beep)

    for f in mergeArr :
        inFile = wave.open(f, 'rb')
        dataArr.append([inFile.getparams(), inFile.readframes(inFile.getnframes())])
        dataArr.append(beep)

        inFile.close()

    sFile.close()
    bFile.close()

    outFile = wave.open(outFile_name, 'wb')
    outFile.setnchannels(1)
    outFile.setsampwidth(2)
    outFile.setframerate(16000)
    outFile.setparams(dataArr[0][0])

    for f in dataArr : 
        outFile.writeframes(f[1])

    outFile.close()


def Binary_Search(item_list, item) :
    first = 0
    last = len(item_list)-1
    found = False 

    while (first <= last and not found) :
        mid = (first + last)//2
        if item_list[mid] == item :
            found = True
        else : 
            if item < item_list[mid] :
                last = mid-1
            else :
                first = mid+1
    
    return found


def Main() : 
    infiles, start_pt, time_length = User()
    mergeArr = Set(infiles, start_pt, time_length)
    Merge(mergeArr)
    #os.chmod("merge.wav", 0755)
    #print mergeArr
    print "Completed"
    print (len(mergeArr)) 
    
Main() 

