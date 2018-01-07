# -*- coding: utf-8 -*-
# @Time     : 2018/1/3 20:40
# @Author   : ELI
# @IDE      : PyCharm
# @PJ_NAME  : cookie_12306
import requests,re
from fake_useragent import UserAgent
import time,sys,json

ua = UserAgent().random

#字典存放坐席类型对应的代号

seat_dict = {'商务座':'business_class','一等座':'first_class','二等座':'second_class','高级软卧':'super_soft','软卧':'soft_sleeper','软座':'soft_seats','动卧':'dongwo','硬卧':'hard_sleeper','硬座':'hard_seats','无座':'seatless'}

seat_type_dict = {'hard_sleeper':'3','hard_seats':'1','soft_seats':'2','soft_sleeper':'4', 'dongwo':'F','super_soft':'6','first_class':'M', 'second_class':'O','seatless':'O','business_class':'P' }

month_dict = {'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun','07':'Jul','08':'Aug','09':'Sep','10':'Oct','11':'Nov','12':'Dec'}

week_dict = {'1':'Mon','2':'Tue','3':'Wed','4':'Thu','5':'Fri','6':'Sat','0':'Sun'}
proxies = {'https': 'https://118.114.77.47:8080',
           'https': 'https://125.210.121.113:3128',
           }
def find_seat(seat_code):
    '''
    根据坐席订票代号返回对应的坐席类型中文名称
    :param seat_code:
    :return:
    '''
    key1 = seat_type_dict.keys()
    value1 = seat_type_dict.values()

    key2 = seat_dict.keys()
    value2 = seat_dict.values()
    for i in value1:
        if seat_code == i:
            index1 = value1.index(seat_code)
            Eng_code = key1[index1]

            index2 = value2.index(Eng_code)
            seat_chinese_name = key2[index2]
            return seat_chinese_name
    else:
        print '#####坐席订票代号未找到！#####',seat_code
        sys.exit()
with open('station_code.txt','rb')as f:
    #2706个站点
    station = f.read()
    station_dict = {}   #包含全国所有站点及其代号的字典{站点：代号}
    tmp_list = re.findall('(\d+@\w+[|].*?[|]\w+)',station)

    for i in tmp_list:
        key = re.search('[|](.*?)[|]',i).group(1)
        value = re.search('[|](\w+)',i).group(1)
        station_dict[key] = value

    #print station_dict
def load_cookie():
    '''
    每次访问url前，使用此方法加载文件的cookie
    :return:
    '''
    dir = 'cookie12306.txt'
    with open(dir) as f:
        cookie = json.load(f)
        return cookie

def get_passager_id(session,passager_name,submit_token):
    '''
    根据人名在“常用联系人”中查找并返回它的身份证号和手机号
    :param passager_name:
    :param submit_token:
    :return:
    '''
    print '正在从“常用联系人”中查找用户身份证号和手机号'
    url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
    data = {
        '_json_att':'',
        'REPEAT_SUBMIT_TOKEN':submit_token
    }
    # 从文件加载cookie
    try:
        cookie = load_cookie()
        session.cookies.update(cookie)

        resp = session.post(url,data=data)

        # 检测cookie是否变化，如果有则更新cookie文件,无则不变
        dict_cookie = dict(cookie)
        check_new_cookie(resp.headers, dict_cookie)

        json_data = json.loads(resp.text)
        for passager in json_data['data']['normal_passengers']:
            if passager['passenger_name'] == passager_name:
                print '已找到乘客信息！'
                ID = passager['passenger_id_no']
                cell_no = passager['mobile_no']
                return ID,cell_no
            else:

                #print passager['passenger_name']
                pass
        print '该乘客不在“常用联系人”中！'

    except Exception, e:
        print '[get_passager_id.error]->', e
        sys.exit()

def check_new_cookie(response_headers,dict_cookies):
    '''
    检测给出的响应headers中有没有新的jSESSIONID和tk值，有就更新cookies文件并返回字典类型的cookie，没有就返回传入时的cookie
    :return:
    '''
    cookie_dir = 'cookie12306.txt'
    __new_tk = re.search('tk=(.*?);', str(response_headers.values()))
    __new_JSESSIONID = re.search('JSESSIONID=(.*?);',str(response_headers.values()))

    if __new_JSESSIONID and __new_tk:
        new_tk = __new_tk.group(1)
        new_JSESSIONID = __new_JSESSIONID.group(1)

        print '>>>>>本次操作检测到新的JSESSIONID和tk值，已更新cookie文件！<<<<<'
        dict_cookies['JSESSIONID'] = new_JSESSIONID
        dict_cookies['tk'] = new_tk
        # 更新cookie文件
        with open(cookie_dir,'wb') as f:
            json.dump(dict_cookies, f)

        print 'JSESSIONID: %s,tk: %s'%(dict_cookies['JSESSIONID'],dict_cookies['tk'])


    elif __new_JSESSIONID:
        new_JSESSIONID = __new_JSESSIONID.group(1)
        print '>>>>>本次操作检测到新的JSESSIONID值，已更新cookie文件！<<<<<'
        dict_cookies['JSESSIONID'] = new_JSESSIONID
        #更新cookie文件
        with open(cookie_dir,'wb') as f:
            json.dump(dict_cookies, f)

        print 'JSESSIONID: %s' % (dict_cookies['JSESSIONID'])


    elif __new_tk:
        new_tk = __new_tk.group(1)
        print '>>>>>本次操作检测到新的tk值，已更新cookie文件！<<<<<'
        dict_cookies['tk'] = new_tk
        # 更新cookie文件
        with open(cookie_dir,'wb') as f:
            json.dump(dict_cookies, f)
        print 'tk: %s' % (dict_cookies['tk'])


    else:
        pass
        #print '>>>>>本次操作没有检测到新cookie值！<<<<<'


class Rule:
    '''
    定义G开头、D开头、K开头、T开头列车的坐席排列规则，因为12306网站对应不同字号开头列车的坐席排列规则不同
    其他还有Z开头等，待添加
    '''

    def check_G_train(self,list):
        '''
        G开头列车的规则，包含商务座、一等座、二等座
        :return:
        '''
        dict_G = {}
        dict_G['train_code'] = list[0]
        dict_G['business_class'] = list[29]
        dict_G['first_class'] = list[28]
        dict_G['second_class'] = list[27]

        return dict_G

    def check_D_train(self,list):
        '''
        D开头列车的规则，包含软卧、动卧、一等座、二等座、无座
        :return:
        '''
        dict_D = {}
        dict_D['train_code'] = list[0]
        dict_D['soft_sleeper'] = list[20]
        dict_D['dongwo'] = list[30]
        dict_D['first_class'] = list[28]
        dict_D['second_class'] = list[27]
        dict_D['seatless'] = list[23]

        return dict_D

    def check_K_train(self,list):
        '''
        K开头列车的规则，包含软卧、硬卧、硬座、无座
        :return:
        '''
        dict_K = {}
        dict_K['soft_sleeper'] = list[20]
        dict_K['hard_sleeper'] = list[25]
        dict_K['hard_seats'] = list[26]
        dict_K['seatless'] = list[23]

        return dict_K

    def check_T_train(self,list):
        '''
        T开头列车的规则，包含软卧、硬卧、硬座、无座
        :return:
        '''
        dict_T = {}
        dict_T['soft_sleeper'] = list[20]
        dict_T['hard_sleeper'] = list[25]
        dict_T['hard_seats'] = list[26]
        dict_T['seatless'] = list[23]

        return dict_T



if __name__ == '__main__':

    print find_seat('1')