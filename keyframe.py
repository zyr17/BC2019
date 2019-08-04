from PIL import Image
import numpy as np
import pickle
import readdata
import os

color_RGB_threshold = 16
def similar_color_RGB(c1, c2):
    #print(c1, c2, np.sqrt(np.square((c1 - c2)).mean(axis=2)))
    return np.sqrt(np.square((c1 - c2)).mean(axis=2)) < color_RGB_threshold

def near_similarity(img1, img2, dist):

    have_similar = np.zeros(img1.shape[:2], dtype='int32')
    tmp = np.array(img1)
    for i in range(-dist, dist + 1):
        for j in range(-dist, dist + 1):
            tmp[:] = 1000
            #print(i, j)
            xl = xr = yl = yr = xl_ = xr_ = yl_ = yr_ = None
            if i < 0:
                xr = i
                xr_ = -i
            elif i > 0:
                xl = i
                xl_ = -i
            if j < 0:
                yr = j
                yr_ = -j
            elif j > 0:
                yl = j
                yl_ = -j
            #print(xl, xr, yl, yr, xr_, xl_, yr_, yl_)
            tmp[xl:xr,yl:yr] = img1[xr_:xl_,yr_:yl_]
            have_similar += similar_color_RGB(tmp, img2)
    same = (have_similar > 0).sum() / np.prod(have_similar.shape)
    return same

    '''
    #slow version
    diff = 0
    for x in range(img2.shape[0]):
        for y in range(img2.shape[1]):
            now = img2[x][y]
            flag = 1
            for ii in range(-dist, dist + 1):
                for jj in range(-dist, dist + 1):
                    if flag != 1:
                        break
                    i = ii + x
                    j = jj + y
                    if i >= 0 and j >= 0 and i < img1.shape[0] and j < img1.shape[1]:
                        if similar_color_RGB(now, img1[i][j]):
                            flag = 0
                if flag != 1:
                    break
            diff += flag
    diff /= img2.shape[0] * img2.shape[1]
    return 1 - diff
    '''

def is_similar(imgarr):
    res = []
    imgarr = np.array(imgarr, dtype='int32')
    for num, [i1, i2] in enumerate(zip(imgarr[:-1], imgarr[1:])):
        res.append([num, near_similarity(i1, i2, 0)])
    res.sort(key = lambda x : x[1])
    print('\n'.join([str(x[0]) + ' ' + str(x[1]) for x in res]))

if __name__ == '__main__':
    videofolder = 'data/douyin/'
    framesfolder = 'data/frames/'
    for file in os.listdir(videofolder):
        readdata.video2img(videofolder + file, framesfolder)
        is_similar(readdata.readimgs(framesfolder))
        input()