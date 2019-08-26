import readdata
import os

def allvideo2img():
    vfolder = 'data/douyin/'
    ifolder = 'data/imgs/'
    videos = os.listdir(vfolder)
    for num, video in enumerate(videos):
        if num % 25 == 0:
            print('%4d/%4d' % (num, len(videos)))
        savefolder = ifolder + video[:-4] + '/'
        if not os.path.exists(savefolder):
            os.mkdir(savefolder)
        if len(os.listdir(savefolder)) != 0:
            continue
        readdata.video2img(vfolder + video, savefolder)
    print(videos[3170:3173])

allvideo2img()
