# -*- coding: utf-8 -*-
# @Time     : 2018/1/3 20:14
# @Author   : ELI
# @IDE      : PyCharm
# @PJ_NAME  : 12306
'''
12306刷票
'''
import requests,re,sys
import json,time,datetime
from cookie_12306 import load_cookie,check_new_cookie,find_seat    #用于登录的cookies和检测cookie变化的模块，用于查找座席中文名的模块
from cookie_12306 import station_dict,seat_dict,seat_type_dict   #站点对应代号的字典，坐席类型对应代号的字典,坐席类型对应订票代号的字典
from cookie_12306 import get_passager_id,month_dict,week_dict,ua
from cookie_12306 import proxies as Proxies
from urllib import quote,unquote
#print Cookies
'''
使用指南：
    请先用12306账号登录网站获取cookie，并填写到cookie12306.txt中，注意对号入座！
    然后在此代码文件的48-55行中修改相应信息
    
    最后运行此程序--

'''


class PAPAPA12306:
    '''
    初始化参数
    '''
    check_url = 'https://kyfw.12306.cn/otn/leftTicket/queryA?leftTicketDTO.train_date=' \
                '{date}&leftTicketDTO.from_station={Departure}&leftTicketDTO.to_station=' \
                '{Destination}&purpose_codes={Type}'
    session = requests.session()
    header = {'User-Agent':ua}
    session.headers=header
    # 从文件加载cookie
    cookie = load_cookie()
    session.cookies.update(cookie)
    session.verify = False
    #忽略ssl警告信息
    requests.packages.urllib3.disable_warnings()
    # train_date = raw_input('输入乘车日期（如2018-01-01）：')
    # __from_station = raw_input('输入起始站点：')
    # __to_station = raw_input('输入到达站点：')
    # __passager_name = raw_input('输入乘客姓名：')
    #__purpose_codes = raw_input('输入车票类型（成人-1，学生-2）：')
    train_date = '2018-01-16'
    __from_station = '南宁'
    __to_station = '重庆'
    __purpose_codes = '1'  #忽略
    __passager_name = '吉衣伍支莫'
##########################################################################################
    __seat_type = ['硬座']    #指定坐席类别，靠前优先                              #
    specific_train = ['K654']     #指定车次，靠前优先                                 #
##########################################################################################


    #定义列表1存放坐席类型对应的第一种代号类型，如'商务座':'business_class'，用于后续判断该坐席是否有票
    seat_type = []
    for i in __seat_type:
        seat_type.append(seat_dict[i])

    times = 1
    __NOW_HOUR = int(time.strftime('%H'))
    __NOW_MIN = int(time.strftime('%M'))
    __NOW_SEC = int(time.strftime('%S'))

    def write_data(self):
        '''
        构造查票参数
        :return:
        '''

        train_date = self.train_date
        __from_station = self.__from_station
        __to_station = self.__to_station
        __purpose_codes = self.__purpose_codes
        if __purpose_codes == '1':
            purpose_codes = 'ADULT'
        elif __purpose_codes == '2':
            purpose_codes = '0X00'
        try:
            #print station_dict[u'北京'.encode('gbk')],'111'
            check_url = self.check_url.format(date=train_date,
                                              Departure=station_dict[unicode(__from_station).encode('gbk')],
                                              Destination=station_dict[unicode(__to_station).encode('gbk')],
                                              Type=purpose_codes)
            #print check_url
            self.check_ticket_exist(check_url)

        except KeyError:
            print '#####站点不存在！#####'
        except requests.exceptions.SSLError:
            print '无法访问，请关闭SSL验证！'
        # except Exception,e:
        #     print '[write_data.error]-->','查票页面出错，请用浏览器测试！'

    def check_ticket_exist(self,check_url,times=times,proxies=None):
        '''
        查询是否有票
        :param check_url:
        :return:
        '''

        print '******************************正在查询是否有票'

        response = self.session.get(check_url,proxies=proxies)

        #检测cookie是否变化，如果有则更新cookie文件,无则不变
        dict_cookies = dict(self.cookie)
        check_new_cookie(response.headers,dict_cookies)

        #把字典类型的cookie传递给下一个函数

        html = response.content
        try:

            json_data = json.loads(response.text)

        except ValueError:
            #print '>>>>>切换代理中<<<<<'
            times+=1
            self.check_ticket_exist(check_url,times,proxies=Proxies)


        if json_data['status'] is True:
            print '>>>>>查询状态：成功!<<<<<'
        else:
            if re.search('status":false',html):
                if re.search('queryA',check_url):
                    self.check_url = re.sub('queryA','queryZ',check_url)
                    self.write_data()
                elif re.search('queryZ', check_url):
                    self.check_url = re.sub('queryZ', 'queryA', check_url)
                    self.write_data()
                else:
                    print '查票url有误，请检查！'
                    sys.exit()
            else:
                print '#####查询状态：失败!#####'
                print response.text
                sys.exit()
        print '>>>>>自动分析站点<<<<<'
        # for i in json_data['data']['map'].values():
        #     print i
        secret_str_list = re.findall('"([\w%]+)[|]',html)
        #print secret_str_list,len(secret_str_list)
        result_list = re.findall('[^"].预订[|]\w+[|](.*?)"',html,re.M)

        if len(result_list)==0:
            print '#####没有搜索到有效车次结果，当前可能为系统维护时间#####'
            sys.exit()
        else:

            #print '搜索到%s个车次' % len(result_list)
            pass
        Specific_train = self.specific_train

        from cookie_12306 import Rule   #导入预先定义好的规则库
        rule = Rule()   #实例化规则库
        try:
            for t in Specific_train:   #遍历之前指定的车次

                for result in result_list:   #遍历查询到的所有车次
                    if re.search(t,result):       #在查询结果中找到指定车次
                        #print result
                        index = result_list.index(result)
                        secret_str = secret_str_list[index]  #找到对应车次的secret_str字符串值，后面要用

                        list = result.split('|')
                        if list[0].startswith('G'):
                            __dict = rule.check_G_train(list)
                            for seat in self.seat_type:
                                if __dict[seat] and __dict[seat] != '无':
                                    #下单
                                    print '^_^有票！ 车次：%s 座席：%s，正在订票！' % (t,seat)
                                    seat_code = seat_type_dict[seat]
                                    self.step_1_submit_train(self.train_date,self.__from_station,self.__to_station,secret_str\
                                                             ,seat_code)

                        elif list[0].startswith('D'):
                            __dict = rule.check_D_train(list)
                            for seat in self.seat_type:
                                if __dict[seat] and __dict[seat] != '无':
                                    #下单
                                    print '^_^有票！ 车次：%s 座席：%s，正在订票！' % (t,seat)
                                    seat_code = seat_type_dict[seat]
                                    self.step_1_submit_train(self.train_date, self.__from_station, self.__to_station,secret_str\
                                                             ,seat_code)

                        elif list[0].startswith('K'):
                            __dict = rule.check_K_train(list)
                            for seat in self.seat_type:
                                if __dict[seat] and __dict[seat] != '无':
                                    #下单
                                    print '^_^有票！ 车次：%s 座席：%s，正在订票！'%(t,seat)
                                    seat_code = seat_type_dict[seat]
                                    self.step_1_submit_train(self.train_date, self.__from_station, self.__to_station,secret_str\
                                                             ,seat_code)


                        elif list[0].startswith('T'):
                            __dict = rule.check_T_train(list)
                            for seat in self.seat_type:
                                if __dict[seat] and __dict[seat] != '无':
                                    #下单
                                    print '^_^有票！ 车次：%s 座席：%s，正在订票！' % (t,seat)
                                    seat_code = seat_type_dict[seat]
                                    self.step_1_submit_train(self.train_date, self.__from_station, self.__to_station,secret_str\
                                                             ,seat_code)
                else:
                    print "(︶︿︶) %s无票！"% t

            else:

                NOW_HOUR = int(time.strftime('%H'))
                NOW_MIN = int(time.strftime('%M'))
                NOW_SEC = int(time.strftime('%S'))
                HOUR = NOW_HOUR - self.__NOW_HOUR
                MIN = NOW_MIN - self.__NOW_MIN
                SEC = NOW_SEC - self.__NOW_SEC
                print '#####已查票%d次,用时%d时%d分%d秒#####' % (times, HOUR, MIN, SEC)
                times += 1
                self.check_ticket_exist(check_url, times)



        except KeyError:
            print '该车次没有这种座席！（若误判，请更新程序）'
            pass

    def step_1_submit_train(self,fromDate,fromStation,toStation,scret_str,seat_code):
        '''
        在查询页点击“预订”之后的直到下单一共有以下几个步骤，第一个步骤使用当前方法来实现
        提交订单请求->确认乘客信息->检查订单信息->获得队列信息->确认队列信息->提交订单成功
        :return:
        '''

        submit_order_url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        check_user_url = 'https://kyfw.12306.cn/otn/login/checkUser'
        self.header['Origin'] = 'https://kyfw.12306.cn'
        self.header['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        self.header['Content-Length'] = '0'
        #print self.header

        #从文件加载cookie
        cookie = load_cookie()
        self.session.cookies.update(cookie)

        print '检查登录状态'
        response = self.session.post(check_user_url,headers = self.header)

        # 检测cookie是否变化，如果有则更新cookie文件,无则不变
        dict_cookie = dict(cookie)
        check_new_cookie(response.headers, dict_cookie)


        if re.search('flag..(.*?)}', response.text).group(1) == 'false':
            print '未登录！'
            sys.exit()
        #更新cookies（将始到站和出发日期写入cookie）  /otn/confirmPassenger/checkOrderInfo

        dict_cookie['_jc_save_fromDate'] = fromDate
        dict_cookie['_jc_save_fromStation'] = quote(fromStation)
        dict_cookie['_jc_save_toStation'] = quote(toStation)
        #将修改后cookie写入文件
        with open('cookie12306.txt','wb') as f:
            json.dump(dict_cookie,f)

        submit_cookie = requests.utils.cookiejar_from_dict(dict_cookie)
        self.session.cookies=submit_cookie

        #构造submit_order 表单参数
        submit_data = {
            'secretStr':unquote(scret_str),
            'train_date' : fromDate,    #开车日期
            'back_train_date' : '2018-1-20',  #回程日期，随意定义，不购买往返票，所以这个参数不起作用，程序暂不实现此功能
            'tour_flag' : 'dc',
            'purpose_codes' : 'ADULT',
            'query_from_station_name' : fromStation,
            'query_to_station_name': toStation,
            'undefined':''
        }
        print '******************************正在提交订单请求NO.1'
        # 从文件加载cookie
        cookie = load_cookie()
        self.session.cookies.update(cookie)

        response = self.session.post(submit_order_url,data=submit_data)
        # 检测cookie是否变化，如果有则更新，无则不变
        dict_cookie = dict(cookie)
        check_new_cookie(response.headers, dict_cookie)

        try:
            _dict = json.loads(response.text)
            #判断提交订单信息是否成功，这里只是下单步骤中的第一步
            if _dict['status'] == True and _dict['messages'] == [] :
                #print '>>>>>状态：OK！<<<<<'

                #调用执行第二个步骤的函数
                self.step_2_confirm_passager(seat_code)

            else:
                if re.search(u'未处理',_dict['messages'][0]):
                    print '#####提示：账号有未处理的订单！#####'
                    sys.exit()
                else:
                    #打印未能成功提交订单请求的提示信息
                    for i in _dict['messages']:
                        print i
        except ValueError:
            #判断是否被重定向
            if re.search(u'登录', response.text):
                print '#####cookie失效，被重定向到登录页，请重新填充cookie！#####'
                sys.exit()
            else:
                #如果是其他错误，打印得到的页面
                print response.text



    def step_2_confirm_passager(self,seat_code):
        '''
        在查询页点击“预订”之后的直到下单一共有以下几个步骤，第二个步骤使用当前方法来实现
        提交订单请求->确认乘客信息->检查订单信息->获得队列信息->确认队列信息->提交订单成功
        :param dict_cookie:
        :return:
        '''
        print '******************************正在确认旅客信息NO.2'

        confirm_url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        #从文件加载cookie
        cookie = load_cookie()
        self.session.cookies.update(cookie)

        response = self.session.post(confirm_url)

        # 检测cookie是否变化，如果有则更新，无则不变
        dict_cookie = dict(cookie)
        check_new_cookie(response.headers, dict_cookie)

        if re.search('退出',response.content):                                                                                   #李磊

            #print '>>>>>状态：OK！<<<<<'


            #通过开车日期计算出星期几并换算为英文的星期，传递到step_4_data字典中
            date = self.train_date.split('-')

            week = datetime.datetime(int(date[0]),int(date[1]),int(date[2])).strftime("%w")

            # 定义一个字典存放一些参数，参数将被传递到执行第4个操作的方法中
            step_4_data ={}
            step_4_data['train_date'] = '%s %s %s %s 00:00:00 GMT+0800 (中国标准时间)'%(week_dict[week],\
                                                                                  month_dict[date[1]],date[2],date[0])
            step_4_data['train_no'] = re.search("train_no...(\w+)",response.text).group(1)
            step_4_data['stationTrainCode'] = re.search("station_train_code...(\w+)",response.text).group(1)
            step_4_data['seatType'] = seat_code
            step_4_data['fromStationTelecode'] = re.search("from_station_telecode...(\w+)",response.text).group(1)
            step_4_data['toStationTelecode'] = re.search("to_station_telecode...(\w+)",response.text).group(1)
            step_4_data['leftTicket'] = re.search("leftTicketStr...(.*?)'",response.text).group(1)
            step_4_data['purpose_codes'] = re.search("purpose_codes...(\w+)",response.text).group(1)
            step_4_data['train_location'] = re.search("dc...train_location...(\w+)",response.text).group(1)
            step_4_data['REPEAT_SUBMIT_TOKEN'] = re.search("RepeatSubmitToken....(\w+)",response.text).group(1)

            #定义一个字典存放一些参数，参数将被传递到执行第5个操作的方法中
            step_5_data = {}
            #找到乘客的身份证号和手机号
            session = self.session
            ID,CELL_NO = get_passager_id(session,self.__passager_name,step_4_data['REPEAT_SUBMIT_TOKEN'])
            step_5_data['passengerTicketStr'] = '%s,0,1,%s,1,%s,%s,N'% (seat_code,self.__passager_name,\
                                                                                       ID,CELL_NO)  ######
            step_5_data['oldPassengerStr'] = '%s,1,%s,1_'%(self.__passager_name,ID)
            step_5_data['randCode'] = ''
            step_5_data['purpose_codes'] = step_4_data['purpose_codes']
            step_5_data['key_check_isChange'] = re.search('key_check_isChange...(.*?).,',response.text).group(1)
            step_5_data['leftTicketStr'] = re.search('leftTicketStr...(.*?).,',response.text).group(1)
            step_5_data['train_location'] = step_4_data['train_location']
            step_5_data['choose_seats'] = ''
            step_5_data['seatDetailType'] = '000'
            step_5_data['whatsSelect'] = '1'
            step_5_data['roomType'] = '00'
            step_5_data['dwAll'] = 'N'
            step_5_data['_json_att'] = ''
            step_5_data['REPEAT_SUBMIT_TOKEN'] = step_4_data['REPEAT_SUBMIT_TOKEN']


            #print 'step_4_data--->',step_4_data,'\n','step_5_data--->',step_5_data
            # print '模块：step_2,正在调试！，确认无误，可删掉此处断点'
            # sys.exit()

            # 调用执行第三个步骤的函数
            self.step_3_check_order(step_4_data,step_5_data)



        else:
            if re.search('登录',response.content):
                print '#####Cookie失效，被重定向到登录页面！#####'
            else:
                print '#####未知页面！#####',response.text

    def step_3_check_order(self,step_4_data,step_5_data):
        '''
        在查询页点击“预订”之后的直到下单一共有以下几个步骤，第三个步骤使用当前方法来实现
        提交订单请求->确认乘客信息->检查订单信息->获得队列信息->确认队列信息->提交订单成功
        :return:
        '''
        print '******************************正在检查订单信息NO.3'
        check_order_url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'

        order_data = {
            'oldPassengerStr':step_5_data['oldPassengerStr'],
            'passengerTicketStr':step_5_data['passengerTicketStr'],
            'tour_flag':'dc',
            'whatsSelect':'1',
            'cancel_flag':'2',
            'randCode':'',
            '_json_att':'',
            'bed_level_order_num':'000000000000000000000000000000',
            'REPEAT_SUBMIT_TOKEN':step_4_data['REPEAT_SUBMIT_TOKEN']
        }

        # 从文件加载cookie
        cookie = load_cookie()
        self.session.cookies.update(cookie)

        response = self.session.post(check_order_url,data=order_data)

        # 检测cookie是否变化，如果有则更新，无则不变
        dict_cookie = dict(cookie)
        check_new_cookie(response.headers, dict_cookie)

        if re.search('submitStatus..(.*?),',response.text).group(1)=='true':
            #print '>>>>>状态：OK！<<<<<'
            #print '模块：step_3,正在调试！，确认无误，可删掉此处断点',sys.exit()
            # 调用执行第四个步骤的方法
            self.step_4_get_queue_count(step_4_data,step_5_data)
        else:
            print '#####订票信息检查失败#####\n',response.text

    def step_4_get_queue_count(self,step_4_data,step_5_data):
        '''
        在查询页点击“预订”之后的直到下单一共有以下几个步骤，第四个步骤使用当前方法来实现
        提交订单请求->确认乘客信息->检查订单信息->获得队列信息->确认队列信息->提交订单成功
        :return:
        '''
        print '******************************正在获取队列信息NO.4'

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'

        # 从文件加载cookie
        cookie = load_cookie()
        self.session.cookies.update(cookie)

        response = self.session.post(url,step_4_data)
        #print response.text

        # 检测cookie是否变化，如果有则更新，无则不变
        dict_cookie = dict(cookie)
        check_new_cookie(response.headers, dict_cookie)

        if re.search("status..true.*?messages....,",response.text):
            #print '>>>>>状态：OK！<<<<<'
            #print '模块：step_4,正在调试！，确认无误，可删掉此处断点', sys.exit()
            #调用执行第五个步骤的方法
            #print step_5_data
            self.step_5_confirm_queue(step_5_data)
        else:
            msg = re.search("messages...(.*?).,",response.text).group(1)
            print msg

    def step_5_confirm_queue(self,step_5_data):
        '''
        在查询页点击“预订”之后的直到下单一共有以下几个步骤，第五个步骤使用当前方法来实现
        提交订单请求->确认乘客信息->检查订单信息->获得队列信息->确认队列信息->打印票价
        :return:
        '''
        print '******************************正在确认队列信息NO.5'

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'

        # 从文件加载cookie
        cookie = load_cookie()
        self.session.cookies.update(cookie)

        response = self.session.post(url,data=step_5_data)

        # 检测cookie是否变化，如果有则更新，无则不变
        dict_cookie = dict(cookie)
        check_new_cookie(response.headers, dict_cookie)

        if re.search("data....submitStatus..true",response.text):
            #print '>>>>>状态：OK！<<<<<'
            #print '模块：step_5,正在调试！，确认无误，可删掉此处断点', sys.exit()
            # 调用执行第六个步骤即查询票价的方法
            self.step_6_check_ticket_price()

        else:
            msg = re.search("messages...(.*?).,", response.text).group(1)
            print msg,response.text,sys.exit()


    def step_6_check_ticket_price(self):
        '''
        在查询页点击“预订”之后的直到下单一共有以下几个步骤，第六个步骤使用当前方法来实现
        提交订单请求->确认乘客信息->检查订单信息->获得队列信息->确认队列信息->打印票价
        :return:
        '''
        print '******************************正在查询订票结果NO.6'
        post_data = {
            '_json_att':''
        }
        url = 'https://kyfw.12306.cn/otn/queryOrder/queryMyOrderNoComplete'

        # 从文件加载cookie
        cookie = load_cookie()
        self.session.cookies.update(cookie)

        response = self.session.post(url,data=post_data)
        html = response.content

        # 检测cookie是否变化，如果有则更新，无则不变
        dict_cookie = dict(cookie)
        check_new_cookie(response.headers, dict_cookie)


        check_false_url = 'https://kyfw.12306.cn/otn/queryOrder/initNoCompleteQueue'
        check_true = re.search(self.__passager_name,html)

        false_msg = self.session.get(check_false_url).content
        check_false = re.search('出票失败',false_msg)
        if check_false:
            print '(︶︿︶) 出票失败了，账号可能单日撤单次数超过3次，请通过浏览器检查！'
            sys.exit()
        elif check_true:
            modify_time = re.search('modifyTime...(.*?).,',html).group(1)
            fromStation = re.search('fromStationName...(.*?).,',html).group(1)
            toStation = re.search('toStationName...(.*?).,',html).group(1)
            startTime = re.search('startTimeString...(.*?).,',html).group(1)
            passengerName = re.search('passengerName...(.*?).,',html).group(1)

            print '^_^订票成功！下单时间：%s ，票面信息：\n乘客：%s  出发站：%s  到达站：%s  开车时间：%s'% (modify_time,\
                                                                          passengerName,fromStation,toStation,startTime)
            print '请在30分钟内付款，否则订单将失效！',response.content
            sys.exit()
        else:
            print '12306系统忙或维护时间！请手动检查\n'
            sys.exit()



a = PAPAPA12306()
a.write_data()

#a.step_6_check_ticket_price()