import readdata
import video
import keyframe
import check_md5
import recognize
import fingerprint
import extractFrame

#输入：文件名 输出：[[相似视频 相似度]...]
def videores(src, tmp = 'data/tmp.mp4'):
    #TODO: 不用文件交互
    readdata.to240p30f(src, tmp)
    #kf, kfnum = keyframe.keyframe(tmp)
    #print(kfnum)
    kf, kfnum = extractFrame.extractFrame(tmp)
    print(kfnum)
    hashs = fingerprint.fingerprint(kf)
    #print('hashs', len(hashs[0][0]), len(hashs[0][1]), len(hashs[0][2]))
    return video.videomain(hashs)
    
#输入：文件名 输出：[[相似视频 相似度]...]
def audiores(src):
    return recognize.recognize_mp4(src)

#输入：待测视频文件名 变换参数(如果要变换)
#输出：[[[总相似文件名 相似度]...][[视频相似 相似度]...][[音频相似 相似度]...]]
def main(src, mc = None):
    if mc != None:
        readdata.makechange(src, src + '.convert', mc)
        src += '.convert'
    md5res = check_md5.check_md5_exists(src)
    print(md5res)
    #TODO: 正式时删去False
    if False and md5res != None and md5res != '':
        return [[[md5res, 1]], [[md5res, 1]], [[md5res, 1]]]
    vr = videores(src)
    ar = audiores(src)
    return [[], vr, ar]

if __name__ == '__main__':
    filename = input().strip()
    if filename == '':
        filename = 'data/input.mp4'
    res = main(filename)
    print(res)
