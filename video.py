import os
import pandas
import knn
import numpy as np

def videocandidate(vhashs, cap = 0.3):
    tot = len(vhashs)
    '''
    res = []
    for vh in vhashs:
        res.append(index.knn(vh, 10))
    res = np.array(res)
    '''
    res = knn.KNN(vhashs, 10)
    res = np.array(res)
    #print(res)
    vc = pandas.Series(res.reshape(-1)).value_counts()
    print(vc)
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
    sim = list(map(lambda x:x[0], knn.value(vhashs, ovc[:19])))
    print(sim)
    sim.sort()
    return (sim[len(sim) // 2] + sim[(len(sim) - 1) // 2]) / 2

def videomain(vhashs, CAP = 0.8):
    res = []
    vc = list(map(lambda x:x[:19], videocandidate(vhashs)))
    print(vc)
    for ovc in vc:
        s = videosimilarity(vhashs, ovc)
        if s > CAP:
            res.append([ovc, s])
    return res
