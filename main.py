

#输入：文件名 输出：[[相似视频 相似度]...]
def videores(src):
    #TODO: 不用文件交互
    readdata.to240p30f(src)
    kf = keyframe.keyframe(src)
    hashs = hash.calchash(kf)
    return video.videomain(hashs)
    


#输入：待测视频文件名 输出：[[[总相似文件名（无相似为None）, 相似度]...][[视频相似 相似度]...][[音频相似 相似度]...]]
def main(src):
    md5res = md5check(src):
    if md5res != None:
        return [[md5res, 1], [md5res, 1], [md5res, 1]]
    vr = videores(src)

