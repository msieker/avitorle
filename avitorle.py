#!/usr/bin/env python

import cv
import itertools
import math
from struct import *

filename = '/media/BadApple.mp4'
newwidth = 220
newheight = 165

minrun=3
maxcopy=127

capture = cv.CaptureFromFile(filename)
outputpath = '/media/badapple/'

print "Frames:", cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_COUNT)
print "Width:", cv.GetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_WIDTH)
print "Height:", cv.GetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_HEIGHT)
print "FPS:",cv.GetCaptureProperty(capture,cv.CV_CAP_PROP_FPS)

resizedframe = cv.CreateImage((newwidth,newheight),cv.IPL_DEPTH_8U,3)
bwframe = cv.CreateImage((newwidth,newheight),cv.IPL_DEPTH_8U,1)
binframe = cv.CreateImage((newwidth,newheight),cv.IPL_DEPTH_8U,1)

def processimagebuffer(imgbuffer, f):
    runs=[(len(list(group)),name) for name, group in itertools.groupby(imgbuffer)]
    output = []
    smallruns = []    
    
    for run in runs:
        if run[0] > minrun:
            
            if len(smallruns)>0:
                f.write(pack('cs',chr(len(smallruns)),''.join(smallruns)))
                smallruns = []
            
            if run[0] > maxcopy:
                runcount = int(math.floor(run[0]/maxcopy))
                remainder = run[0] % maxcopy
                if runcount > 0:
                    f.write(''.join([pack('cc',chr(128+maxcopy),chr(run[1]))]*runcount))
                if remainder > 0:
                    f.write(pack('cc',chr(128+remainder),chr(run[1])))
            else:
                f.write(pack('cc',chr(run[0]),chr(run[1])))
        else:
            if len(smallruns) + run[0] > maxcopy:
                f.write(pack('cs',chr(len(smallruns)),''.join(smallruns)))
                smallruns = []
            smallruns.extend([chr(run[1])]*run[0])
    return output

for i in xrange(0, int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_COUNT)),2):
#for i in xrange(0,35):
    frame = cv.QueryFrame(capture)
    cv.Resize(frame,resizedframe,cv.CV_INTER_NN)
    cv.CvtColor(resizedframe,bwframe,cv.CV_RGB2GRAY)
#    cv.SaveImage(outputpath + str(i) + '.png', bwframe)

    mat =cv.GetMat(bwframe)

    imagebuffer=[0]*((newheight-1)*(newwidth-1))
    offset=0
    print i
    for y in range(0,newheight-1):
        for x in range(0,newwidth-1):
            imagebuffer[offset]=int(mat[y,x])
            offset+=1
    with open(outputpath + str(i).zfill(4) + '.rle','wb') as f:
        processimagebuffer(imagebuffer,f)


