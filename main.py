import readdata
import video
import keyframe
import vhash

#输入：文件名 输出：[[相似视频 相似度]...]
def videores(src, tmp = 'data/tmp.mp4'):
    #TODO: 不用文件交互
    readdata.to240p30f(src, tmp)
    kf, kfnum = keyframe.keyframe(tmp)
    hashs = vhash.calchash(kf)
    #print('hashs', hashs)
    return video.videomain(hashs)
    
#输入：文件名 输出：[[相似视频 相似度]...]
def audiores(src):
    return []

def md5check(src):
    return None

#输入：待测视频文件名 输出：[[[总相似文件名 相似度]...][[视频相似 相似度]...][[音频相似 相似度]...]]
def main(src):
    md5res = md5check(src)
    if md5res != None:
        return [[[md5res, 1]], [[md5res, 1]], [[md5res, 1]]]
    vr = videores(src)
    ar = audiores(src)
    return [[], vr, ar]

if __name__ == '__main__':
    res = main('data/input.mp4')
    print(res)
