'''
Created on Feb 26, 2024

@author: ZZHU25
'''

import requests, bs4, os, json
from pypac import PACSession
from pypac.parser import PACFile
from pandas import DataFrame
import datetime
import time, random

headerinfo = {
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
'Accept-Language': 'en-US,en;q=0.9',
'Accept-Encoding': 'gzip, deflate, br, zstd',
'Referer': 'http://www.baidu.com',
'Connection': 'keep-alive',
'Cache-Control': 'max-age=0',
'Accept-Encoding': 'gzip',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
'Host': 'www.12365auto.com',
}

OEM_list = {"长安":"15","福特":"26","深蓝":"758"}
Page_number = "1"
print(OEM_list.keys())
OEM_name = input('Please input only One (1) OEM Name listed above: \n')
Vehicle_brand_list = \
    {"深蓝":{"深蓝SL03":"3375"},\
     "福特":{"EVOS":"3205"},\
        }
print('\n您选择的OEM有下列车型：\n')
print(Vehicle_brand_list[OEM_name].keys())
print('\n')
vehicle_brand = input('Please enter One (1) vehicle brand listed above: \n')
claim_url = "https://www.12365auto.com/zlts/{}-{}-0-0-0-0_0-0-0-0-0-0-0-{}.shtml".format\
    (OEM_list[OEM_name],\
    Vehicle_brand_list[OEM_name][vehicle_brand],\
    Page_number)

print('Warranty Claim Url: {}: '.format(claim_url) + '\n')
try:
    res = requests.get(claim_url,headers=headerinfo,verify=False,timeout=5) #download above page, send it to res.
except:
    with open(r'C:\Users\zzhu25\OneDrive - azureford\important-docs\00.PythonScripts\pacfile') as f:
        pac = PACFile(f.read())
    session = PACSession(pac)
    res = session.get(claim_url,headers=headerinfo,verify=False,timeout=5) #download above page, send it to res.
res.raise_for_status()
table_result = bs4.BeautifulSoup(res.content,'lxml').select('tr')
claim_number_this_page = len(table_result)

columnNames = [["投诉编号","投诉品牌","投诉车系","投诉车型","问题简述标题","问题简述链接","投诉时间","投诉状态"]]

table_output_page = []
for i in range(1,claim_number_this_page,1):
    table_output = []
    table_output.append(table_result[i].contents[0].getText()) #投诉编号
    table_output.append(table_result[i].contents[1].getText()) #投诉品牌
    table_output.append(table_result[i].contents[2].getText()) #投诉车系
    table_output.append(table_result[i].contents[3].getText()) #投诉车型
    table_output.append(table_result[i].contents[4].getText()) #问题简述标题
    table_output.append('=hyperlink("{}")'.format(table_result[i].contents[4].contents[0].attrs['href'].replace('//', 'https://'))) #问题简述链接
    table_output.append(table_result[i].contents[6].getText()) #投诉时间
    table_output.append(table_result[i].contents[7].getText()) #投诉状态
    table_output_page.append(table_output)

outp = DataFrame(table_output_page,columns=columnNames)
print(outp)
outp.to_csv('{}_{}.csv'.format(OEM_name,vehicle_brand),mode='a',header=1, index=0, encoding='utf_8_sig')
print('Complete Export Warranty Claim Url: {}: '.format(claim_url) + '\n')

if len(bs4.BeautifulSoup(res.content,'lxml').select('.p_page')) != 0:
    last_page_link = bs4.BeautifulSoup(res.content,'lxml').select('.p_page')[0].contents[-1].attrs['href']
    last_page_number = last_page_link.split('-')[-1].split('.')[0]

    for Page_number in range(2,int(last_page_number),1):
        print('Warranty Claim Url: {}: '.format(claim_url) + '\n')
        try:
            res = requests.get(claim_url,headers=headerinfo,verify=False,timeout=5) #download above page, send it to res.
        except:
            with open(r'C:\Users\zzhu25\OneDrive - azureford\important-docs\00.PythonScripts\pacfile') as f:
                pac = PACFile(f.read())
            session = PACSession(pac)
            res = session.get(claim_url,headers=headerinfo,verify=False,timeout=5) #download above page, send it to res.
        res.raise_for_status()
        table_result = bs4.BeautifulSoup(res.content,'lxml').select('tr')
        claim_number_this_page = len(table_result)

        table_output_page = []
        for i in range(1,claim_number_this_page,1):
            table_output = []
            table_output.append(table_result[i].contents[0].getText()) #投诉编号
            table_output.append(table_result[i].contents[1].getText()) #投诉品牌
            table_output.append(table_result[i].contents[2].getText()) #投诉车系
            table_output.append(table_result[i].contents[3].getText()) #投诉车型
            table_output.append(table_result[i].contents[4].getText()) #问题简述标题
            table_output.append('=hyperlink("{}")'.format(table_result[i].contents[4].contents[0].attrs['href'].replace('//', 'https://')))#问题简述链接
            table_output.append(table_result[i].contents[6].getText()) #投诉时间
            table_output.append(table_result[i].contents[7].getText()) #投诉状态
            table_output_page.append(table_output)

        columnNames = [["投诉编号","投诉品牌","投诉车系","投诉车型","问题简述标题","问题简述链接","投诉时间","投诉状态"]]
        outp = DataFrame(table_output_page,columns=columnNames)
        print(outp)
        outp.to_csv('{}_{}.csv'.format(OEM_name,vehicle_brand),mode='a',header=0, index=0, encoding='utf_8_sig')
        print('Complete Export Warranty Claim Url: {}: '.format(claim_url) + '\n')
else:
    print('Complete Export')