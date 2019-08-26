import ffmpeg
import os
import numpy as np
from PIL import Image
import json

def video2img(videoname, savefolder, cutstart = 0, cutend = 0):
    os.system('rm %s*' % savefolder)
    if cutend != 0:
        t = getprobe(videoname)[0] - cutstart - cutend
        ffmpeg.input(videoname).output(savefolder + '%06d.jpg', ss = cutstart, t = t, r = 30).run(quiet = True, overwrite_output = True)
        return
    ffmpeg.input(videoname).output(savefolder + '%06d.jpg', r = 30).run(quiet = True, overwrite_output = True)

def readimgs(savefolder, size = None):
    imgs = os.listdir(savefolder)
    res = []
    for file in imgs:
        img = Image.open(savefolder + file)
        if size != None:
            img = img.resize(size, Image.ANTIALIAS)
        img = np.array(img)
        #print(img.shape, img.dtype)
        res.append(img)
    res = np.stack(res)
    return res

def getprobe(videoname):
    probe = ffmpeg.probe(videoname)
    length = float(probe['format']['duration'])
    for s in probe['streams']:
        if s['codec_type'] == 'video':
            frames = int(s['nb_frames'])
            fps = frames / float(s['duration'])
            x = int(s['width'])
            y = int(s['height'])
    return length, fps, frames, x, y
    

if __name__ == '__main__':
    videofolder = 'data/douyin/'
    files = os.listdir(videofolder)
    for file in files:
        probe = getprobe(videofolder + file)
        print(file, '%7.3f %7.3f %7d %7d %7d' % probe)
        video2img(videofolder + file, 'data/frames/', 0, 3)
        print(file)
        input()