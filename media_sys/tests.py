from django.test import TestCase

import requests
# Create your tests here.

LOCAL = 'http://localhost:8000'

#Remote = 'http://fs.foshanplus.com:8082'

#Remote_100 = 'http://172.16.17.100:8999'

def add_user(openid,name,phone):
    url = LOCAL + "/wxusers/"
    data = {
        'openid': openid,
        'name': name,
        'phone': phone
    }
    res = requests.post(url, data=data)

    print(res)


def add_msg(user, content, pics):
    url = LOCAL + "/message/"
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
    #     openid='8b33a93xecec23e5f5af8231ze',
    #     name='change',
    #     phone='712374'
    # )

    add_msg(
        user='8987987987987',
        content='Mer0000y',
        pics='1nnnnnnnnnnnnnnnnnnnnnnn74'
    )

    #get_user()