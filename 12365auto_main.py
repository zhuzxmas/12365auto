# -*- coding: UTF-8 -*-

'''
Created on Feb 26, 2024

@author: ZZHU25
'''

import requests, bs4, random, time, json, pprint
from pypac import PACSession
from pypac.parser import PACFile
from pandas import DataFrame

print('###=========================================### \n')
print('### 12365auto Version 0.04   last updated: 2024-04-26 ### \n')
print('###=========================================### \n')

# This is the header infomation.
headerinfo = {
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
'Accept-Language': 'en-US,en;q=0.9',
'Accept-Encoding': 'gzip, deflate, br, zstd',
'Referer': 'http://www.baidu.com',
'Connection': 'keep-alive',
'Cache-Control': 'max-age=0',
'Accept-Encoding': 'gzip',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
'Host': 'www.12365auto.com',
}

OEM_name = input('Please input only One (1) OEM Name, or input the OEM you want: \nThis is only for the output file name, no other usage.\n\n')
print('\n')
print('Here is a sample for the configuration of 12365auto Warranty Claim URL: ')
print("https://www.12365auto.com/zlts/{}-{}-0-0-{}-0_0-0-0-0-0-0-0-{}.shtml ")
print('1. the 1st {} is the OEM ID, !!! THIS IS A MUST !!! ')
print('2. the 2nd {} is the vehicle brand ID, THIS IS NOT ALWAYS NEEDED, AND THE Default Value is 0 for All Vehicle Brand. ')
print('3. the 3rd {} is the service time when issue is claimed. ')
print('4. the 4th {} is the page number. ')
print('So, Please go to 12365auto website to check the URL first. This is only required once per vehicle brand or per OEM.\n')

with open(r'./_internal/category_list.json',encoding= 'utf-8') as ff: #for this line, it is used for python normal usage.
# with open(r'./category_list.json',encoding= 'utf-8') as ff: #for this line, it is used for python normal usage.
        category_list = json.load(ff)
category_list_new = {}
for cate_i in range(0,len(category_list)):
    cate_keyA = category_list[cate_i]['value']
    for cate_j in range(0,len(category_list[cate_i]['items'])):
        cate_keyB = category_list[cate_i]['items'][cate_j]['id']
        cate_keyAB = str(cate_keyA) + str(cate_keyB)
        cate_value = category_list[cate_i]['name'] + '-' + category_list[cate_i]['items'][cate_j]['title'] + ';'
        category_list_new[cate_keyAB] = cate_value

### 1st OEM Name ###
OEM_name_id = input('Enter the OEM ID ====ID ID ID==== from URL  == The 1st {} == : \n')
print('\n')

### 2nd Vehicle Brand code ###
vehicle_brand_name = input('Please enter One (1) vehicle brand ==Name==:    \nIf you want to select All vehicle brand, please hit Enter directly: \n') or 'All'
if vehicle_brand_name == 'All':
    vehicle_brand_id = '0'
else:
    vehicle_brand_id = input('Please input vehicle brand ID  ====ID ID ID====  The 2nd {} === from 12365auto URL: \n')

### 3rd YIS duration ###
YIS_duration = {1:'1month', 2:'1-3months', 3:'3-6months', 4:'6-12months', 5:'1-3years', 6:'>3years', 0:'All'}
pprint.pprint(YIS_duration)
print('\n')

yis_number = input('Please enter a YIS number, default = 0, All : \n' )  or '0'
Page_number = input('Please enter a page number, default = 1 : \n' )  or '1'

if yis_number == '0':
    yis_i = int(yis_number)
    print('==================================\n\n')
    print('We will get the info for YIS {} data.\n'.format(YIS_duration[yis_i]))
    ### 4th Page Number ###
    claim_url = "https://www.12365auto.com/zlts/{}-{}-0-0-{}-0_0-0-0-0-0-0-0-{}.shtml".format\
        (OEM_name_id,\
        vehicle_brand_id,\
        yis_i, \
        Page_number)

    print('YIS {}, Page Number: {},  Warranty Claim Url: {}: '.format(YIS_duration[yis_i],Page_number,claim_url) + '\n')
    try:
        res = requests.get(claim_url,headers=headerinfo,verify=False,timeout=10) #download above page, send it to res..
    except:
        with open(r'./_internal/pacfile') as f: #for this line, it is used for pyinstaller to compile an .exe file.
        # with open(r'./pacfile') as f: #for this line, it is used for python normal usage.
            pac = PACFile(f.read())
        session = PACSession(pac)
        res = session.get(claim_url,headers=headerinfo,verify=False,timeout=10) #download above page, send it to res.
    res.raise_for_status()
    time.sleep(random.uniform(7, 13))
    table_result = bs4.BeautifulSoup(res.content,'lxml').select('tr')
    claim_number_this_page = len(table_result)
    if claim_number_this_page > 0:
        columnNames = [["Page Number","投诉编号","投诉品牌","投诉车系","投诉车型","问题简述标题","问题简述链接","问题出现时间","问题类型","投诉时间","投诉状态"]]

        table_output_page = []
        for i in range(1,claim_number_this_page,1):

            issue_cate = table_result[i].contents[5].getText().split(',')
            for issue_cate_i in range(0,len(issue_cate)):
                issue_cate_value = category_list_new[issue_cate[issue_cate_i]]

                table_output = []
                table_output.append(Page_number) # page number
                table_output.append(table_result[i].contents[0].getText()) #投诉编号
                table_output.append(table_result[i].contents[1].getText()) #投诉品牌
                table_output.append(table_result[i].contents[2].getText()) #投诉车系
                table_output.append(table_result[i].contents[3].getText()) #投诉车型
                table_output.append(table_result[i].contents[4].getText()) #问题简述标题
                table_output.append('=hyperlink("{}")'.format(table_result[i].contents[4].contents[0].attrs['href'].replace('//', 'https://'))) #问题简述链接
                table_output.append(YIS_duration[yis_i]) #问题出现时间

                table_output.append(issue_cate_value) #问题类型
                table_output.append(table_result[i].contents[6].getText()) #投诉时间
                table_output.append(table_result[i].contents[7].getText()) #投诉状态
                table_output_page.append(table_output)

        outp = DataFrame(table_output_page,columns=columnNames)
        print(outp)
        outp.to_csv('{}_{}.csv'.format(OEM_name,vehicle_brand_name),mode='a',header=1, index=0, encoding='utf_8_sig')
        print('Complete Export YIS {}, Page {},  Warranty Claim Url: {}: '.format(YIS_duration[yis_i],Page_number,claim_url) + '\n')

        if len(bs4.BeautifulSoup(res.content,'lxml').select('.p_page')) != 0:
            last_page_link = bs4.BeautifulSoup(res.content,'lxml').select('.p_page')[0].contents[-1].attrs['href']
            last_page_number = last_page_link.split('-')[-1].split('.')[0]

            for Page_number in range(int(Page_number)+1,int(last_page_number),1):
                claim_url = "https://www.12365auto.com/zlts/{}-{}-0-0-{}-0_0-0-0-0-0-0-0-{}.shtml".format\
                    (OEM_name_id,\
                    vehicle_brand_id,\
                    yis_i,\
                    str(Page_number))
                print('YIS {}, Page Number: {},  Warranty Claim Url: {}: '.format(YIS_duration[yis_i],str(Page_number),claim_url) + '\n')
                try:
                    res = requests.get(claim_url,headers=headerinfo,verify=False,timeout=10) #download above page, send it to res.
                except:
                    with open(r'./_internal/pacfile') as f: #for this line, it is used for pyinstaller to compile an .exe file.
                    # with open(r'./pacfile') as f: #for this line, it is used for python normal usage.
                        pac = PACFile(f.read())
                    session = PACSession(pac)
                    res = session.get(claim_url,headers=headerinfo,verify=False,timeout=10) #download above page, send it to res.
                res.raise_for_status()
                time.sleep(random.uniform(7, 13))
                table_result = bs4.BeautifulSoup(res.content,'lxml').select('tr')
                claim_number_this_page = len(table_result)
                if claim_number_this_page > 0:

                    table_output_page = []
                    for i in range(1,claim_number_this_page,1):
                        issue_cate = table_result[i].contents[5].getText().split(',')
                        for issue_cate_i in range(0,len(issue_cate)):
                            issue_cate_value = category_list_new[issue_cate[issue_cate_i]]

                            table_output = []
                            table_output.append(Page_number) # page number
                            table_output.append(table_result[i].contents[0].getText()) #投诉编号
                            table_output.append(table_result[i].contents[1].getText()) #投诉品牌
                            table_output.append(table_result[i].contents[2].getText()) #投诉车系
                            table_output.append(table_result[i].contents[3].getText()) #投诉车型
                            table_output.append(table_result[i].contents[4].getText()) #问题简述标题
                            table_output.append('=hyperlink("{}")'.format(table_result[i].contents[4].contents[0].attrs['href'].replace('//', 'https://')))#问题简述链接
                            table_output.append(YIS_duration[yis_i]) #问题出现时间

                            table_output.append(issue_cate_value) #问题类型
                            table_output.append(table_result[i].contents[6].getText()) #投诉时间
                            table_output.append(table_result[i].contents[7].getText()) #投诉状态
                            table_output_page.append(table_output)

                    outp = DataFrame(table_output_page,columns=columnNames)
                    print(outp)
                    outp.to_csv('{}_{}.csv'.format(OEM_name,vehicle_brand_name),mode='a',header=0, index=0, encoding='utf_8_sig')
                    print('Complete Export YIS {}, Page {}/{},  Warranty Claim Url: {}: '.format(YIS_duration[yis_i], str(Page_number),last_page_number,claim_url) + '\n')
            print('Export File is in the same directory as this exe file. \n')
        else:
            print('Complete Export for {} data.'.format(YIS_duration[yis_i]))
            print('Export File is in the same directory as this exe file. \n')
    else:
        print('Complete Export for {} data.'.format(YIS_duration[yis_i]))
        print('Export File is in the same directory as this exe file. \n')
else:
    print('Since you choose YIS time, you will get the data since this YIS duration and longer.\nBe Patient for 5 seconds.\nIt will begin automatically.\n\n')
    time.sleep(5)
    for yis_i in range(int(yis_number),6,1):
        print('==================================\n\n')
        print('We will get the info for YIS {} data.\n'.format(YIS_duration[yis_i]))
        ### 4th Page Number ###
        claim_url = "https://www.12365auto.com/zlts/{}-{}-0-0-{}-0_0-0-0-0-0-0-0-{}.shtml".format\
            (OEM_name_id,\
            vehicle_brand_id,\
            yis_i, \
            Page_number)

        print('YIS {}, Page Number: {},  Warranty Claim Url: {}: '.format(YIS_duration[yis_i],Page_number,claim_url) + '\n')
        try:
            res = requests.get(claim_url,headers=headerinfo,verify=False,timeout=10) #download above page, send it to res..
        except:
            with open(r'./_internal/pacfile') as f: #for this line, it is used for pyinstaller to compile an .exe file.
            # with open(r'./pacfile') as f: #for this line, it is used for python normal usage.
                pac = PACFile(f.read())
            session = PACSession(pac)
            res = session.get(claim_url,headers=headerinfo,verify=False,timeout=10) #download above page, send it to res.
        res.raise_for_status()
        time.sleep(random.uniform(7, 13))
        table_result = bs4.BeautifulSoup(res.content,'lxml').select('tr')
        claim_number_this_page = len(table_result)
        if claim_number_this_page > 0:
            columnNames = [["Page Number","投诉编号","投诉品牌","投诉车系","投诉车型","问题简述标题","问题简述链接","问题出现时间","问题类型","投诉时间","投诉状态"]]

            table_output_page = []
            for i in range(1,claim_number_this_page,1):
                issue_cate = table_result[i].contents[5].getText().split(',')
                for issue_cate_i in range(0,len(issue_cate)):
                    issue_cate_value = category_list_new[issue_cate[issue_cate_i]]

                    table_output = []
                    table_output.append(Page_number) # page number
                    table_output.append(table_result[i].contents[0].getText()) #投诉编号
                    table_output.append(table_result[i].contents[1].getText()) #投诉品牌
                    table_output.append(table_result[i].contents[2].getText()) #投诉车系
                    table_output.append(table_result[i].contents[3].getText()) #投诉车型
                    table_output.append(table_result[i].contents[4].getText()) #问题简述标题
                    table_output.append('=hyperlink("{}")'.format(table_result[i].contents[4].contents[0].attrs['href'].replace('//', 'https://'))) #问题简述链接
                    table_output.append(YIS_duration[yis_i]) #问题出现时间

                    table_output.append(issue_cate_value) #问题类型
                    table_output.append(table_result[i].contents[6].getText()) #投诉时间
                    table_output.append(table_result[i].contents[7].getText()) #投诉状态
                    table_output_page.append(table_output)

            outp = DataFrame(table_output_page,columns=columnNames)
            print(outp)
            outp.to_csv('{}_{}.csv'.format(OEM_name,vehicle_brand_name),mode='a',header=1, index=0, encoding='utf_8_sig')
            print('Complete Export YIS {}, Page {},  Warranty Claim Url: {}: '.format(YIS_duration[yis_i],Page_number,claim_url) + '\n')

            if len(bs4.BeautifulSoup(res.content,'lxml').select('.p_page')) != 0:
                last_page_link = bs4.BeautifulSoup(res.content,'lxml').select('.p_page')[0].contents[-1].attrs['href']
                last_page_number = last_page_link.split('-')[-1].split('.')[0]

                for Page_number in range(int(Page_number)+1,int(last_page_number),1):
                    claim_url = "https://www.12365auto.com/zlts/{}-{}-0-0-{}-0_0-0-0-0-0-0-0-{}.shtml".format\
                        (OEM_name_id,\
                        vehicle_brand_id,\
                        yis_i,\
                        str(Page_number))
                    print('YIS {}, Page Number: {},  Warranty Claim Url: {}: '.format(YIS_duration[yis_i],str(Page_number),claim_url) + '\n')
                    try:
                        res = requests.get(claim_url,headers=headerinfo,verify=False,timeout=10) #download above page, send it to res.
                    except:
                        with open(r'./_internal/pacfile') as f: #for this line, it is used for pyinstaller to compile an .exe file.
                        # with open(r'./pacfile') as f: #for this line, it is used for python normal usage.
                            pac = PACFile(f.read())
                        session = PACSession(pac)
                        res = session.get(claim_url,headers=headerinfo,verify=False,timeout=10) #download above page, send it to res.
                    res.raise_for_status()
                    time.sleep(random.uniform(7, 13))
                    table_result = bs4.BeautifulSoup(res.content,'lxml').select('tr')
                    claim_number_this_page = len(table_result)
                    if claim_number_this_page > 0:

                        table_output_page = []
                        for i in range(1,claim_number_this_page,1):
                            issue_cate = table_result[i].contents[5].getText().split(',')
                            for issue_cate_i in range(0,len(issue_cate)):
                                issue_cate_value = category_list_new[issue_cate[issue_cate_i]]

                                table_output = []
                                table_output.append(Page_number) # page number
                                table_output.append(table_result[i].contents[0].getText()) #投诉编号
                                table_output.append(table_result[i].contents[1].getText()) #投诉品牌
                                table_output.append(table_result[i].contents[2].getText()) #投诉车系
                                table_output.append(table_result[i].contents[3].getText()) #投诉车型
                                table_output.append(table_result[i].contents[4].getText()) #问题简述标题
                                table_output.append('=hyperlink("{}")'.format(table_result[i].contents[4].contents[0].attrs['href'].replace('//', 'https://')))#问题简述链接
                                table_output.append(YIS_duration[yis_i]) #问题出现时间

                                table_output.append(issue_cate_value) #问题类型
                                table_output.append(table_result[i].contents[6].getText()) #投诉时间
                                table_output.append(table_result[i].contents[7].getText()) #投诉状态
                                table_output_page.append(table_output)

                        outp = DataFrame(table_output_page,columns=columnNames)
                        print(outp)
                        outp.to_csv('{}_{}.csv'.format(OEM_name,vehicle_brand_name),mode='a',header=0, index=0, encoding='utf_8_sig')
                        print('Complete Export YIS {}, Page {}/{},  Warranty Claim Url: {}: '.format(YIS_duration[yis_i], str(Page_number),last_page_number,claim_url) + '\n')
                print('Export File is in the same directory as this exe file. \n')
            else:
                print('Complete Export for {} data.'.format(YIS_duration[yis_i]))
                print('Export File is in the same directory as this exe file. \n')
                continue
        else:
            print('Complete Export for {} data.'.format(YIS_duration[yis_i]))
            print('Export File is in the same directory as this exe file. \n')
            continue