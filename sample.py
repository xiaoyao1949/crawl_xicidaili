"""
爬取西刺网免费IP，存储成txt后进行有效性验证
"""
from bs4 import BeautifulSoup
import requests
from urllib import request, error
import threading


def get_proxy(url):
    # 设置UA标识
    headers = {
        'User-Agent': 'Mozilla / 5.0(Windows NT 10.0;WOW64) AppleWebKit '
                      '/ 537.36(KHTML, likeGecko) Chrome / 63.0.3239.132Safari / 537.36'
    }
    proxies = {'http': '47.94.217.37:80'}
    # 打开创建的txt文件
    with open('proxy.txt', 'ab') as proxy_file:
        # page是我们需要获取多少页的ip，这里我们获取到第９页
        for page in range(1, 10):
            # 通过观察ＵＲＬ，我们发现原网址+页码就是我们需要的网址了，这里的page需要转换成str类型
            urls = url + str(page)
            # 通过requests来获取网页源码
            try:
                rsp = requests.get(urls, headers=headers, proxies=proxies)
                rsp.raise_for_status()
                rsp.encoding = rsp.apparent_encoding
            except Exception as e:
                print('网络连接错误：', urls)
                continue
            html = rsp.text
            # 通过BeautifulSoup，来解析html页面
            soup = BeautifulSoup(html, 'html.parser')
            # 通过分析我们发现数据在　id为ip_list的table标签中的tr标签中
            try:
                trs = soup.find('table', id='ip_list').find_all('tr')  # 这里获得的是一个list列表
            except:
                print('解析数据失败', rsp.request.url)
                continue

            for item in trs[1:]:
                tds = item.find_all('td')
                # 我们会发现有些img标签里面是空的，所以这里我们需要加一个判断
                if tds[0].find('img') is None:
                    nation = '未知'
                    locate = '未知'
                else:
                    nation = tds[0].find('img')['alt'].strip()
                    locate = tds[3].text.strip()
                # 通过td列表里面的数据，我们分别把它们提取出来
                ip = tds[1].text.strip()
                port = tds[2].text.strip()
                anony = tds[4].text.strip()
                protocol = tds[5].text.strip()
                speed = tds[6].find('div')['title'].strip()
                time = tds[8].text.strip()
                # 将获取到的数据按照规定格式写入txt文本中，这样方便我们获取
                content = '%s|%s|%s|%s|%s|%s|%s|%s\n' % (nation, ip, port, locate, anony, protocol, speed, time)
                print(content)
                proxy_file.write(content.encode('utf-8'))
                proxy_file.flush()


def verifyProxy(ip, type):
    """
    验证代理的有效性
    """
    request_header = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"
    }
    url = "http://www.baidu.com"
    # 填写代理地址
    proxy = {type: ip}
    # 创建proxyHandler
    proxy_handler = request.ProxyHandler(proxy)
    # 创建ｏｐｅｎｅｒ
    proxy_opener = request.build_opener(proxy_handler)
    # 安装opener
    request.install_opener(proxy_opener)

    try:
        req = request.Request(url, headers=request_header)
        rsq = request.urlopen(req, timeout=5.0)
        code = rsq.getcode()
        return code
    except error.URLError as e:
        return e


def verify_proxy_list():
    global lock
    with open('verified.txt', 'ab') as verifiedFile, open('proxy.txt', 'r', encoding='utf-8') as inFile:
        while True:
            lock.acquire()
            ll = inFile.readline().strip()
            lock.release()
            if len(ll) == 0:
                break
            line = ll.strip().split('|')
            ip = line[1]
            port = line[2]
            type = line[5]
            real_ip = ip + ':' + port
            code = verifyProxy(real_ip, type.lower())
            if code == 200:
                lock.acquire()
                print("---Success:" + ip + ":" + port)
                verifiedFile.write(ll + "\n")
                lock.release()
            else:
                print("---Failure:" + ip + ":" + port)


lock = threading.Lock()
if __name__ == '__main__':
    # 创建两个空白文件，分别存储爬取下来的代理和验证可用的代理
    tmp = open('proxy.txt', 'w')
    tmp.write("")
    tmp.close()
    tmp1 = open('verified.txt', 'w')
    tmp1.write("")
    tmp1.close()

    # fill proxy.txt
    for url in ['http://www.xicidaili.com/' + loc for loc in ('nn/', 'nt/', 'wn/', 'wt')]:
        get_proxy(url)
    print('代理IP获取完毕')
    print('开始验证。。。')

    all_thread = []
    # 30个线程
    for i in range(30):
        t = threading.Thread(target=verify_proxy_list)
        all_thread.append(t)
        t.start()

    for t in all_thread:
        t.join()

    print('Done!')
