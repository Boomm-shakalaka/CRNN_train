# -*- coding: utf-8 -*-
import os
import lmdb # install lmdb by "pip install lmdb"
import cv2
import numpy as np
import tqdm
#from genLineText import GenTextImage
 
def checkImageIsValid(imageBin):
    if imageBin is None:
        return False
    imageBuf = np.fromstring(imageBin, dtype=np.uint8)
    img = cv2.imdecode(imageBuf, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return False
    imgH, imgW = img.shape[0], img.shape[1]
    if imgH * imgW == 0:
        return False
    return True
 
 
def writeCache(env, cache):
    with env.begin(write=True) as txn:
        for k, v in cache.iteritems():
            txn.put(k, v)
 
 
def createDataset(outputPath, imagePathList, labelList, lexiconList=None, checkValid=True):
    """
    Create LMDB dataset for CRNN training.
    ARGS:
        outputPath    : LMDB output path
        imagePathList : list of image path
        labelList     : list of corresponding groundtruth texts
        lexiconList   : (optional) list of lexicon lists
        checkValid    : if true, check the validity of every image
    """
    #print (len(imagePathList) , len(labelList))
    assert(len(imagePathList) == len(labelList))
    nSamples = len(imagePathList)
    print( '...................')
    # map_size=1073741824 定义最大空间是1GB
    env = lmdb.open(outputPath, map_size=4073741824)
    
    cache = {}
    cnt = 1
    for i in xrange(nSamples):
        imagePath = imagePathList[i]
        label = labelList[i]
        if not os.path.exists(imagePath):
            print('%s does not exist' % imagePath)
            continue
        with open(imagePath, mode='r') as f:
            imageBin = f.read()

        if checkValid:
            if not checkImageIsValid(imageBin):
                print('%s is not a valid image' % imagePath)
                continue

 
        ########## .mdb数据库文件保存了两种数据，一种是图片数据，一种是标签数据，它们各有其key
        imageKey = 'image-%09d' % cnt
        labelKey = 'label-%09d' % cnt
        cache[imageKey] = imageBin
        cache[labelKey] = label
        ##########
        if lexiconList:
            lexiconKey = 'lexicon-%09d' % cnt
            cache[lexiconKey] = ' '.join(lexiconList[i])
        if cnt % 1000 == 0:
            writeCache(env, cache)
            cache = {}
            print('Written %d / %d' % (cnt, nSamples))
        cnt += 1
    nSamples = cnt-1
    cache['num-samples'] = str(nSamples)
    writeCache(env, cache)
    print('Created dataset with %d samples' % nSamples)
 
 
def read_text(path):
    
    with open(path) as f:
        text = f.read()
    text = text.strip()
    
    return text

import glob
if __name__ == '__main__':
    
    #lmdb 输出目录
    outputPath = '/home/cjy/Desktop/CRNN_data/data/date_testdata_lmdb'
 
    # 训练图片路径，标签是txt格式，名字跟图片名字要一致，如123.jpg对应标签需要是123.txt
    path = '/home/cjy/Desktop/CRNN_data/data/date_testdata/*.jpg'
    imagePathList = glob.glob(path)
    print ('------------',len(imagePathList),'------------')
    imgLabelLists = []
    print(len(imagePathList))
    for p in imagePathList:
        try:
           imgLabelLists.append((p,read_text(p.replace('.jpg','.txt'))))
           #print(p)
        except:
            continue
    print("finish append")
    #imgLabelList = [ (p,read_text(p.replace('.jpg','.txt'))) for p in imagePathList]
    ##sort by lebelList
    imgLabelList = sorted(imgLabelLists,key = lambda x:len(x[1]))
    print(len(imgLabelList))
    imgPaths = [ p[0] for p in imgLabelList]
    txtLists = [ p[1] for p in imgLabelList]
    print("start create")
    createDataset(outputPath, imgPaths, txtLists, lexiconList=None, checkValid=True)
