# -*- coding: utf-8 -*-
#python3.x
'''
10/11/2017
如果有'Mx32.txt'这样连续的文件，需要把数字加n,可以用这个办法。
方法是：先找到数字，把数字替换成其他固定字符加上需要的数字，然后再把固定字符替换成空。
'''
print(__doc__)

import re
import os
fdir=input(r'需要操作的文件家地址：')
fnum=int(input('被加或者减去的数：'))
os.chdir(fdir)
qb='abzqb'

#用qb替换了数字,
for i in os.listdir(os.getcwd()):
    num_origin=int(re.search('[\d]+',i).group(0))
    assert num_origin!=None,'%s里没有数字'%i
    num_new=str(num_origin+fnum) #得到其中的数字+fnum
    os.rename(i,i.replace(str(num_origin),qb+num_new))
#去掉qb
for i in os.listdir(os.getcwd()):
    os.rename(i,i.replace(qb,''))
print('Rename has done!')
