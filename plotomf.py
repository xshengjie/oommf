# -*- coding: utf-8 -*-
#python2.7
"""
2017年11月10日
@author: 409200093@qq.com
针对用omf2txt转换结果画图。
"""
import numpy as np
import os
from mayavi import mlab
import pandas as pd
import shutil
import re

class_color=11
red2blue=np.array([[ 0. ,  0. ,  1. ],#blue
       [ 0.2,  0.2,  1. ],
       [ 0.4,  0.4,  1. ],
       [ 0.6,  0.6,  1. ],
       [ 0.8,  0.8,  1. ],
       [ 1. ,  1. ,  1. ],#white
       [ 1. ,  0.8,  0.8],
       [ 1. ,  0.6,  0.6],
       [ 1. ,  0.4,  0.4],
       [ 1. ,  0.2,  0.2],
       [ 1. ,  0. ,  0. ]])#red

def read0(ffile):
    f=np.load(ffile)
    x,y,z,mx,my,mz=f['x'],f['y'],f['z'],f['mx'],f['my'],f['mz']
    return x.flatten(),y.flatten(),z.flatten(),mx.flatten(),my.flatten(),mz.flatten()

def read1(fpath,img_ratio,cl,cm,model_shape,Ms=None):
    '''
    输入内容是文件的地址，并进行按照某种步进刷选，不包括磁矩全为0的部分。
    '''
    assert isinstance(img_ratio,int),'img_ratio is int'
    assert cl.shape==(3,2),'clip_xyz is (3,2) array '
    assert cm.shape==(3,2),'clip_ms is (3,2) array'
    assert model_shape.shape==(3,),'model_shape is (3,) array'
    rat=img_ratio
    cx,cy,cz=cl[0],cl[1],cl[2]#坐标范围选择
    cmx,cmy,cmz=cm[0],cm[1],cm[2]#磁矩范围的选择。
    
    #read data
    try:
        d=np.loadtxt(fpath)
    except:
        d=pd.read_table(fpath,header=None,dtype=float,comment='#',delim_whitespace=True)#pandas read
        d=np.array(d)
    x,y,z,mx,my,mz=d[:,0],d[:,1],d[:,2],d[:,3],d[:,4],d[:,5]#read data
    
    #set Ms
    if Ms==None:
        Ms=np.max(np.sqrt(mz**2+my**2+mx**2))
    mx,my,mz=mx/Ms,my/Ms,mz/Ms#normal Ms
    del d#delete d
    
    #set model_shape
    if model_shape.prod()!=len(z):#
        model_shape=np.array([len(set(z)),len(set(y)),len(set(x))])#计算形状
        assert model_shape.prod()==len(x),'Please enter the correct model parameters'
    
    #按照三个方向固定间隔选择数据。
    x=x.reshape(model_shape)[::rat,::rat,::rat]
    y=y.reshape(model_shape)[::rat,::rat,::rat]
    z=z.reshape(model_shape)[::rat,::rat,::rat]
    mx=mx.reshape(model_shape)[::rat,::rat,::rat]
    my=my.reshape(model_shape)[::rat,::rat,::rat]
    mz=mz.reshape(model_shape)[::rat,::rat,::rat]
    '''
    #删除全是0的位置。并且用其他方法筛选数据。
    #这里得到需要的数据。两个条件相加是'或'的关系，想乘是'并'的关系。
    #distance=np.sqrt((yi-40e-9)**2+(zi-40e-9)**2)
    #example:
    >>>index=((mz!=0.0)*(x<100e-9)*(x>50e-9)*(z>40e-9)*(distance<40e-9)*(distance>28e-9))
    '''
    indexl=((x>cx[0])*(x<cx[1])*(y>cy[0])*(y<cy[1])*(z>cz[0])*(z<cz[1]))#位置筛选结果
    indexm=((mx>cmx[0])*(mx<cmx[1])*(my>cmy[0])*(my<cmy[1])*(mz>cmz[0])*(mz<cmz[1]))#磁矩筛选结果
    inde0=((np.fabs(mz)+np.fabs(mx)+np.fabs(my))!=0.0)#非零筛选结果。
    index=indexl*inde0*indexm#所有筛选结果求并集
    z,x,y=z[index],x[index],y[index]#筛选索引里的坐标数据
    mz,my,mx=mz[index],my[index],mx[index]#筛选索引里的磁矩数据
    return x,y,z,mx,my,mz
    
def color1d(x,y,z,mx,my,mz,img_color,img_color_reverse,class_color=11):
    '''输入的数据mz应该在(-1,1),-1对应blue,1对应red,只能用一列数据代表颜色'''
    #set color_coefficen
    if img_color_reverse:color_=-1#
    if not img_color_reverse:color_=1#    
    #set img_color ,颜色描述哪个磁矩，M选定的磁矩
    M={'mx':mx,'my':my,'mz':mz}[img_color]
    #把-1,1分成11份
    c=np.linspace(-1,1,class_color)         
    lz=np.searchsorted(c,color_*M)#把M插到c里面
    lz=red2blue[lz]#再把顺序变成0，1的颜色。
    df=pd.DataFrame(np.hstack([np.array([x,y,z,mx,my,mz]).T,lz]))
    df=df.groupby(by=[6,7,8])
    return list(df)

    
def omf_plot(x,y,z,mx,my,mz,img_bgcolor=(1,1,1),img_figsize=(1080,720),img_format='png',img_display='cone',img_view=np.array([0,90])\
    ,img_line_scale=0.9,img_axis=False,fname=None,fdir=None):
    #create color map
    data=color1d(x,y,z,mx,my,mz,img_color,img_color_reverse)
    #计算箭头的长度
    cal_step=lambda i:np.diff(np.sort(list(set(i)))[:2])[0]
    scale_factor=np.sqrt(cal_step(x)**2+cal_step(y)**2+cal_step(z)**2)*img_line_scale
    #开始画图
    f=mlab.figure(bgcolor=img_bgcolor,size=img_figsize)#图片的
    for i in range(len(data)):#循环画图class_color**3次
        color,pf=data[i][0],data[i][1]#DataFrame,[x,y,z,mx,my,mz,lx,ly,lz]
        mlab.quiver3d(pf[0],pf[1],pf[2],pf[3],pf[4],pf[5],color=color,scale_factor=scale_factor,mode=img_display)#cone
        
    if img_axis:
        #创建三个坐标轴方向
        maxx,maxy,maxz=np.max(x),np.max(y),np.max(z)
        #z
        mlab.quiver3d(0,1.0*maxy,1.3*maxz,0,0,1,color=(0,0,1),mode='arrow',scale_factor=scale_factor*2,)
        mlab.text3d(0,1.0*maxy,1.3*maxz+scale_factor*2,'z',color=(0,0,0),scale=scale_factor*0.8)   
        #y    
        mlab.quiver3d(0,1.0*maxy,1.3*maxz,0,1,0,color=(0,1,0),mode='arrow',scale_factor=scale_factor*2)
        mlab.text3d(0,1.0*maxy+scale_factor*2,1.3*maxz,'y',color=(0,0,0),scale=scale_factor*0.8)        
        #x    
        mlab.quiver3d(0,1.0*maxy,1.3*maxz,1,0,0,color=(1,0,0),mode='arrow',scale_factor=scale_factor*2,)
        mlab.text3d(scale_factor*2,1.0*maxy,1.3*maxz,'x',color=(0,0,0),scale=scale_factor*0.8)
        #########################################
    
    for view in img_view:
        mlab.view(img_view[0],img_view[1])#观察角度    
        if isinstance(fname,str) and isinstance(fdir,str) and img_save:
            if GOODGPU:
                mlab.savefig(os.path.join(fdir,'%s-z%d-x%d.%s'%(fname,img_view[0],img_view[1],img_format)),magnification=5)
            else:
                mlab.savefig(os.path.join(fdir,'%s-z%d-x%d.%s'%(fname,img_view[0],img_view[1],img_format)))

    if img_show==True:
        #print u"需手动关掉图片，才会继续画图！！"
        print "Need to manually turn off the picture, will continue drawing!"
        mlab.show()#显示图片
    if not img_show:
        mlab.close()#关闭画布

namenum=0
def mdirs(name,num):#递归创建文件夹，直到成功
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
    
def ana(fpath):#总的分析
    fname=fpath.split(os.sep)[-1].split('.')[0]#文件的名字
    fdir=os.path.dirname(fpath)#文件夹
    if file_suffix=='txt':
        x,y,z,mx,my,mz=read1(fpath,img_ratio,clip_xyz,clip_ms,model_shape,Ms)
    if file_suffix=='npz':
        x,y,z,mx,my,mz=read0(fpath)
    omf_plot(x,y,z,mx,my,mz,img_bgcolor,img_figsize,img_format,img_display,img_view,img_line_scale,img_axis,fname,fdir)

if __name__=='__main__':
    #基本参数,按需更改
    Ms=None#饱和磁矩,如果不知道可以设置成 None
    model_shape=np.array([0,0,0])                    #array,模型大小，分别为:z,y,x三个方向点的个数,也可以设置为[0,0,0]   
    clip_xyz=np.array([[0,1],[0,1],[0e-9,200e-9]])   #array,x,y,z坐标范围的选择，
    clip_ms=np.array([[-1,1],[-1,1],[-1,1]])         #array,磁矩除以Ms后mx,my,mz磁矩范围的选择

    #画图相关，按需更改
    img_figsize=[2080,1320]              #list,图片大小.
    img_bgcolor=(1,1,1)                 #tuple,图片背景,rgb格式,(1,1,1)为白色.
    img_format='jpg'                    #str,图片格式，jpg,png,tiff.....
    img_display='arrow'                 #str,or 'cone'......
    img_ratio=2                         #int,整数且大于1，画图时模型的缩放比例。
    img_view=np.array([0,0])        #array,theta观察角度与Z轴夹角,phi观察角度与X轴夹角。可以为数组。
    img_axis=True                      #bool,是否显示坐标轴指示
    img_show=False                      #bool,画图之后是否展示出来，之后的程序不能运行,可以手动。
    img_color='mz'                      #str,颜色标记，'mx','my','mz'
    img_color_reverse=True              #bool,掉换配色方法。
    img_line_scale=1.7                 #float,为长度的放大倍数
    img_save=True                       #bool,是否保存图片
    
    # 其他，按需更改
    file_suffix='txt'#‘npz’or 'txt’.chose which kind of text
    #独立显卡可以设置成True,核心显卡可能会有问题。
    GOODGPU=False
    #打印参数
    print(u'''Currently used parameters are as follows:\n1,Ms:{}\n2,model_shape:{}\n3,clip_xyz:\n{}\n4,clip_ms:\n{}\n5,img_figsize:{}\n6,\
img_bgcolor:{}\n7,img_format:{}\n8,img_display:{}\n9,img_ratio:{}\n10,img_view:\n{}\n11,img_axis:{}\n12,img_show:{}\
\n13,img_color:{}\n14,color_reverse:{}\n15,img_line_scale:{}\n16,img_save:{}\n17file:{}
\n如果需要更改请在文件中更改！'''.format(Ms,model_shape,clip_xyz,clip_ms,img_figsize,img_bgcolor,img_format\
,img_display,img_ratio,img_view,img_axis,img_show,img_color,img_color_reverse,img_line_scale,img_save,file_suffix))
       
    ##########程序主体，不需要更改##################################
    #fpath=raw_input(u"请输入画图需要文档所在文件夹地址:")
    fpath=raw_input("Please enter the txt file folder address\n:")
    ffile=[i for i in os.listdir(fpath) if i.split('.')[-1]==file_suffix]#筛选后缀是txt的文件
    ffile=sorted(ffile,key=lambda x:int(re.search('[\d]+',x).group(0)))
    for i in ffile:
         ana(os.path.join(fpath,i))
         print '{} is done!'.format(i)
    if img_save:
        smove(img_format,fpath,img_format)
    #######################################################

