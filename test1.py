# encoding: utf-8
"""
@author: peng_an
@time: 2016/7/19 13:09
"""
a=[]
a.append({"name":"allan"})
print a[0]
a[0]["age"]=11
print a[0]

for pair in a:
    print pair