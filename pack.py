from PIL import Image
import numpy as np
import pickle
import os

foldername = 'data/img/'
picklename = 'data/pickle/img.pkl'

files = os.listdir(foldername)

res = []

for file in files:
    img = np.array(Image.open(foldername + file))
    #print(img.shape, img.dtype)
    res.append(img)

res = np.stack(res)
print(res.shape, res.dtype)

pickle.dump(res, open(picklename, 'wb'))