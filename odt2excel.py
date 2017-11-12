#!env/usr/bin/python3
#encoding=utf-8
'''
10/11/2017
odt2excel(path,usecols=[0,5,9,10,11,19],columns=['Total','Exc','DM','Demag','fix','Time'],step=1)
path，文件夹的地址，该文件夹下可包含一个或多个以‘.odt’结尾的文件。
'''
print(__doc__)
import os
import numpy as np
import pandas as pd
def odt2excel(path,usecols,columns,step=1): 
    assert len(usecols)==len(columns),'usecols和columns长度不一样'
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path,file)):
            if os.path.splitext(file)[-1]=='.odt':
                pathfile=os.path.join(path,file)
                data=np.loadtxt(pathfile)[::step,usecols]#usecols
                data=pd.DataFrame(data,columns=columns)
                os.chdir(path)
                data.to_excel(r'%sodt2excel.xlsx'%os.path.splitext(pathfile)[0])
                print('%s is done!'%file)
                
if __name__=='__main__':
    #如果需要更改请在这里更改
    #usecols=[0,5,9,10,11,19]
    #columns=['Total','Exc','DM','Demag','fix','Time']
    usecols=[0,5,9,10,11,12,13,15]#用哪些列
    columns=['Total','Exc','DMI','Demag','Uzzem','B','Bx','Bz']#列的名字是什么？
    step=1#step,是想要保存的间隔
    print('''当前使用的参数是：\n1，usecols:{}\n2,columns:{}\n3,step:{}'''.format(usecols,columns,step))
    path=input(r'请输入odt文件所在的文件夹地址:')
    odt2excel(path,usecols,columns,step)
