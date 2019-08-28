import os
import pandas
import vhash
import numpy as np

def videocandidate(vhashs, cap = 0.5):
    tot = len(vhashs)
    '''
    res = []
    for vh in vhashs:
        res.append(index.knn(vh, 10))
    res = np.array(res)
    '''
    res = vhash.knn(vhashs, 10)
    vc = pandas.Series(res.reshape(-1)).value_counts()
    return np.array(vc[vc > cap * tot].index)

def videosimilarity1(data1, data2):
    sim = []
    for i in data1:
        smallest = 1e100
        for j in data2:
            i -= j
            dist = (i * i).mean()
            if smallest > dist:
                smallest = dist
        sim.append(smallest)
    sim.sort()
    return (sim[len(sim) // 2] + sim[(len(sim) - 1) // 2]) / 2

def videosimilarity(vhashs, ovc):
    sim = []
    for vh in vhashs:
        dist = vhash.dist(vhashs, ovc)
        sim.append(dist)
    sim.sort()
    return (sim[len(sim) // 2] + sim[(len(sim) - 1) // 2]) / 2

def videomain(vhashs, CAP = 0.8):
    res = []
    vc = videocandidate(vhashs)
    for ovc in vc:
        s = videosimilarity(vhashs, ovc)
        if s > CAP:
            res.append([ovc, s])
    return res
