from django.test import TestCase

import requests
# Create your tests here.

LOCAL = 'http://localhost:8989'

Remote = 'http://fs.foshanplus.com:8082'

#Remote_100 = 'http://172.16.17.100:8999'

def add_user(openid,name,phone):
    url = Remote + "/wxusers/"
    data = {
        'openid': openid,
        'name': name,
        'phone': phone
    }
    res = requests.post(url, data=data)

    print(res.headers)
    print(res.json())


def add_msg(user, content, pics):
    url = Remote + "/message/"
    data = {
        'user': user,
        'content': content,
        'pics': pics
    }
    res = requests.post(url, data=data)

    print(res.json())

def get_user():
    url = 'http://localhost:8000/wxusers/?format=json'
    res = requests.get(url)
    print(res.json())

if __name__ == '__main__':
    # add_user(
    #     openid='93c1232323e5f5e',
    #     name='33333hange',
    #     phone='00000712374'
    # )
    #
    add_msg(
        user='20181127164248-2030636938-2643',
        content='test content',
        pics=''
    )

    #get_user()