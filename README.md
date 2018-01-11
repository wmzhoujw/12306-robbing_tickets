# 12306-robbing_tickets

前言
----
由于源码内容较多,所以在此不进行源码解释，只介绍使用方法

程序说明 
-------
解释器：Python2.7。本程序未进行封装，程序的运行需要用到python编辑器。  

功能实现
-------
根据提供已登录的12306账号的cookie进行抢票。也就是说，本程序未实现模拟登录的功能，需要手动将cookie填入文件，然后程序才能正常运行。 

使用介绍
-------
程序由3个文件组成：  
&emsp;12306.py 核心程序  
&emsp;cookie_12306.py  模块、字典定义  
&emsp;cookie12306.txt  存放cookie的文本文件  
&emsp;station_code.txt 存放所有的车站名及其对应代号

### 第一步：登录12306网站获取cookie  
&emsp;先把所有的文件下载到本地，并存放于一个文件夹内，然后使用编辑器打开*12306.py*和*cookie12306.txt*。  
&emsp;使用12306账号登录该网站，登录后，F12打开浏览器审查元素，刷新页面，找到对应请求的请求头中的cookie值，如下图所示，将cookie中每个字段的值对应复制到*cookie12306.txt*文件中。  ![](https://github.com/chaseSpace/Pictures/blob/master/robbing_tickets/cookie.png)  
&emsp;注意：是对应字段copy，不是整个copy，因为文件中的值是类似字典的数据类型，而浏览器中的整个cookie值是字符串。图中还列出了一个特殊情况（也不算特殊，刷新几次后就会有），即访问网站时，服务器可能会返回cookie中的一个新的字段值，字段“tk”，根据调试，可能返回的还有一个字段是“JSESSIONID”,如果有返回，则需要填入文本文件的cookie的对应字段值就是这些返回的值，其他字段不变。

### 第二步：修改12306.py
&emsp;修改代码的51-57行的内容，如下图，相信你可以看懂具体修改哪个位置。  ![](https://github.com/chaseSpace/Pictures/blob/master/robbing_tickets/input.png)  
&emsp;注意：  
&emsp;&emsp;字符串内不要有空格；  
&emsp;&emsp;旅客姓名必须在12306账号的常用联系人中；
&emsp;&emsp;出发日期按格式修改：2018-xx-xx，列车名称首字母大写
&emsp;&emsp;确认你填入的站点间有你填入的列车在运行

### 第三步：运行12306.py
emsp;
