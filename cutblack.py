import numpy as np
from PIL import Image

def cutblack(imgs, size = (240, 426), cap = 16):
    res = []
    for img in imgs:
        x1 = 999999
        y1 = 999999
        x2 = 0
        y2 = 0
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if (img[i][j] >= cap).sum() == 3:
                    if x1 > i:
                        x1 = i
                    if y1 > j:
                        y1 = j
                    if x2 < i:
                        x2 = i
                    if y2 < j:
                        y2 = j
        if x1 >= x2:
            x1 = 0
            x2 = 1
        if y1 >= y2:
            y1 = 0
            y2 = 1
        img = img[x1:x2,y1:y2]
        img = Image.fromarray(img).resize(size, Image.ANTIALIAS)
        res.append(np.array(img))
    return np.stack(res)

if __name__ == '__main__':
    import readdata
    source = 'data/douyin/6530581774991363331.mp4'
    folder = 'data/results/keyframes/6530581774991363331/'
    res, _ = readdata.readimgs(folder)
    res = cutblack(res)
    for num, img in enumerate(res):
        Image.fromarray(img).save('data/cut/%06d.jpg' % num)