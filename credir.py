# -*- coding: utf-8 -*-
#python3
"""
2017年9月6日
@author: 409200093@qq.com
模仿windows创建文件夹，若已经存在会自动在文件夹后面添加数字，直到成功。
"""
import os
import shutil
namenum=0
def mdirs(name,num):#递归创建文件夹，知道成功
    global namenum
    try:
        os.makedirs(name+str(namenum))
    except:
        namenum+=1
        mdirs(name,namenum)

def CreDir(namedirs,fdirs=os.getcwd()):#
    file1=os.listdir(fdirs)
    os.chdir(fdirs)
    try:
        os.makedirs(namedirs)
    except:
        mdirs(namedirs,0)
    file2=os.listdir(fdirs)
    return os.path.join(fdirs,[i for i in file2 if i not in file1][0])#return new dirs

def smove(suffix,fpath,newdir):#后缀，路径
    cfdir=CreDir(newdir,fpath)#create new dir
    for f in os.listdir(fpath):
        if os.path.splitext(f)[-1]=='.%s'%suffix:
            shutil.move(os.path.join(fpath,f),os.path.join(cfdir,f))
            
if __name__=='__main__':
    print('will crate ok in current dirs')
    print(CreDir('ok'))
