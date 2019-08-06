from PIL import Image
import numpy as np
import pickle
import readdata
import os
import random

def saveimage(savefolder, res, imgs):
    if os.path.exists(savefolder):
        os.system('rm %s*' % savefolder)
    else:
        os.mkdir(savefolder)
    for num, [i, j] in enumerate(res):
        img = imgs[i + 1]
        Image.fromarray(img).save(savefolder + '%03d-%06d.jpg' % (num, i))

def RGB2HSV(a):
    a = np.array(a, dtype='int32')
    R, G, B = a.T
    m = np.min(a,len(a.shape) - 1).T
    M = np.max(a,len(a.shape) - 1).T
    C = M - m
    Cmsk = C != 0
    H = np.zeros(R.shape, int)
    mask = (M == R) & Cmsk
    H[mask] = np.mod(60 * (G - B) // C, 360)[mask]
    mask = (M == G) & Cmsk
    H[mask] = (60 * (B - R) // C + 120)[mask]
    mask = (M == B) & Cmsk
    H[mask] = (60 * (R - G)//C + 240)[mask]
    H *= 255
    H //= 360
    V = M
    S = np.zeros(R.shape, int)
    S[Cmsk] = ((255 * C) // V)[Cmsk]
    return np.array(np.stack((H, S, V)).T, dtype='uint8')

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

def is_similar_near(imgarr, MIN_KEY_FRAME = 20, NEAR_THRESHOLD = 0.8):
    res = []
    imgarr = np.array(imgarr, dtype='int32')
    for num, [i1, i2] in enumerate(zip(imgarr[:-1], imgarr[1:])):
        res.append([num, near_similarity(i1, i2, 0)])
    res.sort(key = lambda x : x[1])
    #print('\n'.join([str(x[0]) + ' ' + str(x[1]) for x in res]))
    for i in range(len(res)):
        if i >= MIN_KEY_FRAME and res[i][0] >= NEAR_THRESHOLD:
            return res[:i]
    return res

def hist_similarity(img1, img2, norm = False):
    if norm:
        hist1, _1 = np.histogram(img1.reshape(-1), 256)
        hist2, _2 = np.histogram(img2.reshape(-1), 256)
    else:
        hist1, _1 = np.histogram(img1.reshape(-1), 256, (0, 255))
        hist2, _2 = np.histogram(img2.reshape(-1), 256, (0, 255))
    #print(norm, _1[0], _1[-1], _2[0], _2[-1], img1.min(), img1.max(), img2.min(), img2.max())
    total = hist1.sum()
    res = 0
    now2 = 0
    for num, i in enumerate(hist1):
        while i != 0:
            delta = min(i, hist2[now2])
            res += delta * abs(now2 - num)
            i -= delta
            hist2[now2] -= delta
            if hist2[now2] == 0:
                now2 += 1
    return 1 - res / total / 256

def is_similar_histogram(imgarr, mixarr = np.array([0.299, 0.587, 0.114]), norm = False, MIN_KEY_FRAME = 20, NEAR_THRESHOLD = 0.95):
    res = []
    imgarr = np.array(imgarr.dot(mixarr), dtype='int32')
    for num, [i1, i2] in enumerate(zip(imgarr[:-1], imgarr[1:])):
        res.append([num, hist_similarity(i1, i2, norm)])
    res.sort(key = lambda x : x[1])
    #print('\n'.join([str(x[0]) + ' ' + str(x[1]) for x in res]))
    for i in range(len(res)):
        if i >= MIN_KEY_FRAME and res[i][0] >= NEAR_THRESHOLD:
            return res[:i]
    return res

if __name__ == '__main__':
    videofolder = 'data/douyin/'
    framesfolder = 'data/frames/'
    files = os.listdir(videofolder)
    random.shuffle(files)
    for file in files:
        readdata.video2img(videofolder + file, framesfolder)
        imgs = readdata.readimgs(framesfolder)
        if len(imgs) > 600:
            continue

        print('start rgbnear')
        res = is_similar_near(imgs)
        print('\n'.join([str(x[0]) + ' ' + str(x[1]) for x in res]))
        saveimage('data/results/rgbnear/', res, imgs)
        
        print('start rgbhistogram')
        res = is_similar_histogram(imgs, norm = True)
        print('\n'.join([str(x[0]) + ' ' + str(x[1]) for x in res]))
        saveimage('data/results/rgbhistogram/', res, imgs)

        print('start hsvhistogram')
        hsvimgs = RGB2HSV(imgs)
        res = is_similar_histogram(imgs, np.array([1, 0, 0]))
        print('\n'.join([str(x[0]) + ' ' + str(x[1]) for x in res]))
        saveimage('data/results/hhistogram/', res, imgs)

        print(file, 'over')
        input()