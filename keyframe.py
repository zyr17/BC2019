from PIL import Image
import numpy as np
import pickle
import readdata
import os
import random
import time

def saveimage(savefolder, res, imgs, saveorder = False):
    res = [[-1, 0.0]] + res
    if os.path.exists(savefolder):
        if len(os.listdir(savefolder)) > 0:
            os.system('rm %s*' % savefolder)
    else:
        os.mkdir(savefolder)
    for num, [i, j] in enumerate(res):
        img = imgs[i + 1]
        if saveorder:
            Image.fromarray(img).save(savefolder + '%03d-%06d.jpg' % (num, i + 2))
        else:
            Image.fromarray(img).save(savefolder + '%06d.jpg' % (i + 2))

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
        res.append([num, near_similarity(i1, i2, 1)])
    res.sort(key = lambda x : x[1])
    #print('\n'.join([str(x[0]) + ' ' + str(x[1]) for x in res]))
    for i in range(len(res)):
        if i >= MIN_KEY_FRAME and res[i][0] >= NEAR_THRESHOLD:
            return res[:i]
    return res

def localdiff(nowdiff, frame = 50, max = 0.2, delta = 0.5, similar = 0.99, top = 0.05):
    frame //= 2
    topnum = int(len(nowdiff) * top)
    diffwithid = list(zip(range(len(nowdiff)), nowdiff))
    diffwithid.sort(key=lambda x:x[1])
    biggest = np.zeros(len(nowdiff), dtype='bool')
    for i in range(topnum):
        biggest[diffwithid[i][0]] = True
    #print(biggest)
    #不要全局较小，完全局部性判断
    #biggest = True
    nowdiff = np.array(nowdiff, dtype='float')
    res = []
    for i in range(len(nowdiff)):
        if not biggest[i] or similar < nowdiff[i]:
            continue
        left = 0
        right = len(nowdiff)
        if left < i - frame:
            left = i - frame
        if right > i + frame:
            right = i + frame
        part = np.array(nowdiff[left:right])
        center = i - left
        #print(part.min(), part.max(), end='')
        part -= part.min()
        part /= part.max()
        #print(i, part)
        if center > 0 and part[center - 1] - part[center] > delta and part[center] < max:
            res.append([i, nowdiff[i]])
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
    res = localdiff([x[1] for x in res])
    return res
    '''
    res.sort(key = lambda x : x[1])
    #print('\n'.join([str(x[0]) + ' ' + str(x[1]) for x in res]))
    for i in range(len(res)):
        if i >= MIN_KEY_FRAME and res[i][0] >= NEAR_THRESHOLD:
            return res[:i]
    return res
    '''

def extractallkeyframe(dataf, destf, tmpf):
    if not os.path.exists(tmpf):
        os.mkdir(tmpf)
    if not os.path.exists(destf):
        os.mkdir(destf)
    files = os.listdir(dataf)
    lasttime = time.time()
    for num, file in enumerate(files):
        print(file)
        if num % 50 == 0:
            print(str(num) + '/' + str(len(files)), time.time() - lasttime)
            lasttime = time.time()
        dest = destf + file[:-4] + '/'
        if os.path.exists(dest) and len(os.listdir(dest)) > 0:
            continue
        readdata.video2img(dataf + file, tmpf)
        imgs, original = readdata.readimgs(tmpf, (64, 64))
        hsvimgs = RGB2HSV(imgs)
        res = is_similar_histogram(hsvimgs, np.array([1, 0, 0]))
        #print('\n'.join([str(x[0]) + ' ' + str(x[1]) for x in res]))
        saveimage(dest, res, original)

#输入：视频名称 输出：[[关键帧] [帧号]]
def keyframe(src, tmpf = 'data/frames/'):
    readdata.video2img(src, tmpf)
    imgs, original = readdata.readimgs(tmpf, (64, 64))
    hsvimgs = RGB2HSV(imgs)
    res = is_similar_histogram(hsvimgs, np.array([1, 0, 0]))
    print(res)
    res = [x[0] for x in res]
    kf = []
    framenum = []
    for one in [-1] + res:
        kf.append(original[one + 1])
        framenum.append(one + 2)
    kf = np.stack(kf)
    return kf, framenum

if __name__ == '__main__':
    '''
    videofolder = 'data/douyin/'
    framesfolder = 'data/frames/'
    files = os.listdir(videofolder)
    random.shuffle(files)
    for file in files:
        #file = '6629600868192750855.mp4'
        readdata.video2img(videofolder + file, framesfolder)
        imgs, original = readdata.readimgs(framesfolder, (64, 64))

        print('start rgbnear')
        res = is_similar_near(imgs)
        print('\n'.join([str(x[0]) + ' ' + str(x[1]) for x in res]))
        saveimage('data/results/rgbnear/', res, original, True)
        
        print('start rgbhistogram')
        res = is_similar_histogram(imgs, norm = True)
        print('\n'.join([str(x[0]) + ' ' + str(x[1]) for x in res]))
        saveimage('data/results/rgbhistogram/', res, original)

        print('start hsvhistogram')
        hsvimgs = RGB2HSV(imgs)
        res = is_similar_histogram(hsvimgs, np.array([1, 0, 0]))
        print('\n'.join([str(x[0]) + ' ' + str(x[1]) for x in res]))
        saveimage('data/results/hhistogram/', res, original)

        print(file, 'over')
        input()
    '''
    #extractallkeyframe('data/douyin/', 'data/results/keyframes/', 'data/frames/')
    #x, y = keyframe('data/douyin/6510522419826920717.mp4')
    #print(y)
    videofolder = 'data/douyin/'
    files = os.listdir(videofolder)
    for i in range(10000):
        file = files[random.randint(0, len(files) - 1)]
        print(file)
        readdata.makechange(videofolder + file, 'data/convert.mp4', ['resolution', 0.7, 0.7])
        x, y = keyframe('data/convert.mp4')
        #x, y = keyframe(videofolder + file)
        base = [int(x[:-4]) for x in os.listdir('data/results/keyframes/' + file[:-4])]
        bu = [0] * 3000
        for j in y:
            bu[j] += 1
        for j in base:
            bu[j] += 1
        same = []
        diff = []
        for num in range(len(bu)):
            if bu[num] == 2:
                same.append(num)
            elif bu[num] == 1:
                diff.append(num)
        if len(diff) > 0:
            print(y)
            print(base)
            print(same)
            print(diff)
            input()