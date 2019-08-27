import os
import pandas

def videocandidate(vhashs, cap = 0.5):
    tot = len(vhashs)
    res = []
    for vh in vhashs:
        res.append(index.knn(vh, 10))
    res = np.array(res)
    vc = pandas.Series(res.reshape(-1)).value_counts()
    return np.array(cv[cv > cap * tot].index)

def videosimilarity(data1, data2):
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