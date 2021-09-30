#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import time
import requests
import datetime
import dingtalkchatbot.chatbot as cb


def mail(text, msg):
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.utils import formataddr
        my_sender = 'xxxxxx@xxx.com'  # 发件人邮箱账号
        my_pass = 'xxxxxx'  # 发件人邮箱授权码 / 腾讯企业邮箱请使用登陆密码
        recipients = 'xxxxxx@xxx.com'  # 收件人邮箱账号
        # 内容
        msg = MIMEText('{}\r\n{}'.format(text, msg), 'plain', 'utf-8')
        # [发件人邮箱昵称、发件人邮箱账号], 昵称随便
        msg['From'] = formataddr([text, my_sender])
        # [收件人邮箱昵称、收件人邮箱账号], 昵称随便
        msg['To'] = formataddr(["推送目标", recipients])

        # 邮件的主题、标题
        msg['Subject'] = "漏洞武器库该更新啦！！！"

        # 用的腾讯企业邮箱做的测试   如果要用其他邮箱的话
        # 用其他邮箱作为发件人的话,请将"smtp.exmail.qq.com" 修改为 "xxxxxxxxxx.xxxx.com"
        # 发件人邮箱中的SMTP服务器端口  我这里是腾讯企业邮箱465  请查看自己的SMTP服务器端口号
        server = smtplib.SMTP_SSL("smtp.exmail.qq.com", 465)
        server.login(my_sender, my_pass)
        server.sendmail(my_sender, recipients, msg.as_string())
        server.quit()  # 关闭连接
        print("邮件发送成功")
    except Exception as e:
        print("邮件发送失败: ", e)


def reque(api, receive):
    req = requests.get(api).text
    time.sleep(5)
    return append(receive, req)


def append(receive, req):
    s = re.findall('"total_count":*.{1,10}"incomplete_results"', req)
    print(s)
    s1 = str(s).replace(',"incomplete_results"\']', "").replace('[\'"total_count":', "")
    return receive.append(s1)


def new_reque(api, new_receive, url_list, description_list):
    req = requests.get(api).text
    time.sleep(5)

    return new_append(new_receive, req, url_list, description_list)


def new_append(new_receive, req, url_list, description_list):
    s = re.findall('"total_count":*.{1,10}"incomplete_results"', req)
    print(s)
    s1 = str(s).replace(',"incomplete_results"\']', "").replace('[\'"total_count":', "")
    
    description = re.findall('"description":*.{1,200}"fork"', req)[0].replace("\",\"fork\"", '').replace(
        "\"description\":\"", '')
    url = re.findall('"svn_url":*.{1,200}"homepage"', req)[0].replace("\",\"homepage\"", '').replace(
        "\"svn_url\":\"", '')
    
    return new_receive.append(s1), url_list.append(url), description_list.append(description)


def getNews(keyword_list, new_receive, url_list, description_list):
    try:
        for i in keyword_list:
            # print(i)
            if i == "cve":
                year = datetime.datetime.now().year
                api = "https://api.github.com/search/repositories?q=CVE-{}&sort=updated".format(year)
                new_reque(api, new_receive, url_list, description_list)
            else:
                api = "https://api.github.com/search/repositories?q={}&sort=updated".format(i)
                new_reque(api, new_receive, url_list, description_list)

    except Exception as e:
        print(e, "github链接不通")

# pushplus推送
def pushplus(text, msg):
    url = "https://pushplus.hxtrip.com/send"
    data = {"token": "xxxxxxxxxxxx",#这里放pushplus的token
            "title": text,
            "content": msg,
            "template": "html",
            # 一对多推送的时候把下面一行注释去掉，填写好群组编码就可以了
            # "topic": "xxxxxxx" # 这里放群组编码
            }
    requests.post(url=url, data=data)
        
# 钉钉
def dingding(text, msg):
    # 将此处换为钉钉机器人的api
    webhook = 'xxxxx'
    ding = cb.DingtalkChatbot(webhook)
    ding.send_text(msg='{}\r\n{}'.format(text, msg), is_at_all=False)


# server酱  http://sc.ftqq.com/?c=code
def server(text, msg):
    # 将 xxxx 换成自己的server SCKEY
    uri = 'https://sc.ftqq.com/xxxx.send?text={}&desp={}'.format(text, msg)
    requests.get(uri)


# 添加Telegram Bot推送支持
def tgbot(text, msg):
    import telegram
    # Your Telegram Bot Token
    bot = telegram.Bot(token='123456:aaa-sdasdsa')
    group_id = 'Your Group ID'
    bot.send_message(chat_id=group_id, text='{}\r\n{}'.format(text, msg))


# 通过检查name 和 description 中是否存在test字样，排除test
def regular(req_list):
    for req in req_list:
        name = re.findall('"name":*.{1,200}"full_name"', req)[0].replace("\"name\":\"", '').replace("\",\"full_name\"",
                                                                                                        '')
        description = re.findall('"description":*.{1,200}"fork"', req)[0].replace("\",\"fork\"", '').replace(
            "\"description\":\"", '')

        if name.lower().find('test') == -1 and description.lower().find('test') == -1:
            return req_list.append("True")
        return req_list.append("False")


def sendNews(keyword_list, black_list):

    print("初始化数据中！！！")
    receive = []

    print("GitHub实时监控中 ...")
    for i in keyword_list:
        if i == "cve":
            year = datetime.datetime.now().year
            api = "https://api.github.com/search/repositories?q=CVE-{}&sort=updated".format(year)
            reque(api, receive)
        else:
            api = "https://api.github.com/search/repositories?q={}&sort=updated".format(i)
            reque(api, receive)

    print(receive)
    receive1 = receive
    while receive1:
        try:
            new_receive = []
            url_list = []
            description_list = []
            time.sleep(180)

            # 推送正文内容
            str(getNews(keyword_list, new_receive, url_list, description_list))
            # 推送标题
            text = r'GitHub监控消息提醒！！！'
            print(text)
            for i in receive1:
                for index, j in enumerate(new_receive):
                    if i != j:
                        if str(url_list[index]) in black_list:
                            print(str(url_list[index]) + " 已经存在于黑名单中")
                        else:
                            msg ='\n更新了：' + str(keyword_list[index]) + '\n描述：' + str(description_list[index]) + '\nURL：' + str(url_list[index])
                            # 三选一即可，没配置的 注释或者删掉
                            # server(text, msg)
                            # dingding(text, msg)
                            # tgbot(text,msg)
                            # print(msg)
                            mail(text, msg)
                            # pushplus(text, msg)

                            print("正在添加到黑名单：" + str(url_list[index]))
                            black_list.append(str(url_list[index]))
                            print("添加成功！！！")
                    else:
                        print(keyword_list[index] + "数据无更新！！！")

            print(new_receive)
            receive1 = new_receive

        except Exception as e:
            raise e


if __name__ == '__main__':
    keyword_list = ["免杀", "poc", "cve", "payload", "漏洞利用", "红队", "蓝队", "redteam", "取证", "应急", "后渗透", "内网", "攻防", "网络安全",
                    "主机安全", "信息收集", "溯源"]
    black_list = []
    sendNews(keyword_list, black_list)

