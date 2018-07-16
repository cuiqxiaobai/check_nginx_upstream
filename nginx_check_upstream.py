
#! /usr/bin/env python3
# -*-:utf-8-*-
"""检测多个目录下的NGINX配置文件，检测配置文件中大于1的upstream，如有不在用的upstream，发出来{filename:upstream_name}"""
"""检测逻辑，检测出每个upstream中的所有"""
import re,os,sys,json

upstream_regex = re.compile(r'\supstream.*?}',re.DOTALL)    #匹配upstream server {****}内容，upstream前面必须紧邻空格
zhushi_regex = re.compile(r'#+.*}')     #匹配注释掉的upstream模块，只需要匹配  } 前面有 # 就能说明这个模块都配注释了
pp_regex = re.compile(r'location\s+/\s+{.*?}',re.DOTALL)    #匹配location /{ }
ip_regex = re.compile(r'\d+\.\d+\.\d+\.\d+')        #匹配IP地址
ppname_regex = re.compile(r'http.*;')       #匹配http://test_server_D; 也就是proxy_pass

dir = ['/srv/nginx/admin/conf.d','/srv/nginx/api/conf.d','/srv/nginx/online/conf.d','/srv/nginx/admindocker/conf.d']
n = 0   #计数，看看有多少个NGINX配置文件，我们有上千个，怕遗漏，测试时心里有底

zhushi_dict = {}    #注释的存在这里面
nused_dict = {}     #未使用的存在这里
for d in dir:
    os.chdir(d)             #切换到给定的目录中
    files = os.listdir(d)      #目录里的所有文件存在列表中
    for site in files:
        n += 1
        if site[-5:] == '.conf':    #如果文件名后五位不是.conf，排除
            with open(site, 'r') as f:
                a = f.read()        #全文读取文件
            if a.count('upstream') > 1: #如果全文只存在1个upstream单词，就不再做深入排查了，这个其实有问题，因为有些地方也会出现这个词，但是基本能排除绝大多数文件了
                upstream_com = upstream_regex.findall(a)    #匹配出所有的upstream模块
                pp_com = pp_regex.findall(a)    #匹配出location /{}    正常的文件有且只有一个
                pp_name = ppname_regex.findall(pp_com[0])[0][7:-1].strip()  #匹配出test_server_D
                # print(pp_name)

                up_list = []    #存储被注释的upstream的
                up_dict = {}  # upstream的名字与它下面的未被注释的ip存在这,{upstreamname1:[ip],up2:[ip],up3:[ip]}
                for i in upstream_com:
                    # print(i)
                    ####upstream都注释##########

                    zhushi_com = zhushi_regex.findall(i)    #匹配upstream模块是否存在注释的}
                    if len(zhushi_com) > 0:     #如果有的话,打印出文件名和upstream的模块名字
                        #print(site, i.split()[1])
                        up_list.append(site + '\t' + i.split()[1])
                        zhushi_dict[site] = up_list         #注释的都存在这里

                    #########upstream对应的ip都出来#########

                    up_name = i.split('{')[0].split()[1]
                    ip_com = ip_regex.findall(i)
                    up_dict[up_name] = ip_com   #对应关系存到字典里
                #print(up_dict)
                up_list2 = []
                for k,v in up_dict.items():
                    if len(set(v) & set(up_dict[pp_name])) == 0:    #每个upstream里的IP与使用的IP在比较，如果不存在交集，说明不在用
                        # print({site:k})
                        up_list2.append(k)
                if len(up_list2) > 0:   #存在异常的upsteam
                    nused_dict[site] = up_list2

print(n)

out_list = ['test1.com']
for o in out_list:
    if o in list(nused_dict.keys()):
        nused_dict.pop(o)
    if o in list(zhushi_dict.keys()):
        zhushi_dict.pop(o)

print('zhushi',zhushi_dict)
print('nouserd',nused_dict)
