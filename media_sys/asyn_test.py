import asyncio
import aiohttp
import json

def consumer():
    r = ''
    while True:
        n = yield r
        if not n:
            return
        print('[CONSUMER] Consuming %s...' % n)
        r = '200 OK'

def produce(c):
    c.send(None)
    n = 0
    while n < 5:
        n = n + 1
        print('[PRODUCER] Producing %s...' % n)
        r = c.send(n)
        print('[PRODUCER] Consumer return: %s' % r)
    c.close()


@asyncio.coroutine
def hello():
    print("Hello world!")
    # 异步调用asyncio.sleep(1):
    r = yield from asyncio.sleep(1)
    print("Hello again!")


@asyncio.coroutine
def wget(host):
    print('wget %s...' % host)
    connect = asyncio.open_connection(host, 80)
    reader, writer = yield from connect
    header = 'GET / HTTP/1.0\r\nHost: %s\r\n\r\n' % host
    writer.write(header.encode('utf-8'))
    yield from writer.drain()
    while True:
        line = yield from reader.readline()
        if line == b'\r\n':
            break
        print('%s header > %s' % (host, line.decode('utf-8').rstrip()))
    # Ignore the body, close the socket
    writer.close()



# 代码在上面
sema = asyncio.Semaphore(3)

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
           "X-Requested-With": "XMLHttpRequest",
           "Accept": "*/*"}


async def get_source(url, session):
    print("正在操作:{}".format(url))

    imgs_urls = []
    async with session.get(url, headers=headers, timeout=10) as response:  # 获得网络请求
        print(response.status)
        if response.status == 200:  # 判断返回的请求码
            source = await response.text()  # 使用await关键字获取返回结果
            ############################################################
            data = json.loads(source)
            photos = data["photos"]["photo"]
            for p in photos:
                img = p["src"].split('?')[0]
                imgs_urls.append(img)

            ############################################################
        else:
            print("网页访问失败")

        return imgs_urls

async def save_img(url, session):
    try:
        async with session.get(url, headers=headers) as img_res:
            print(url)
            imgcode = await img_res.read()
            with open("photos/{}".format(url.split('/')[-1]), 'wb') as f:
                f.write(imgcode)
                f.close()
    except Exception as e:
        print(e)

# 为避免爬虫一次性请求次数太多，控制一下
async def x_get_source(sem, url, session):
    async with sem:
        urls = await get_source(url, session)
        for url in urls:
            await save_img(url, session)


async def run(r):
    url_format = "https://tu.fengniao.com/ajax/ajaxTuPicList.php?page={}&tagsId=13&action=getPicLists"

    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(3)

    # Create client session that will ensure we dont open new connection
    # per each request.
    conn = aiohttp.TCPConnector(verify_ssl=False)  # 防止ssl报错,其中一种写法
    async with aiohttp.ClientSession(connector=conn) as session:
        for i in range(2, r):
            # pass Semaphore and session to every GET request
            task = x_get_source(sem, url_format.format(i), session)
            tasks.append(task)

        responses = asyncio.wait(tasks)
        await responses

if __name__ == '__main__':
    # c = consumer()
    # produce(c)
    # 获取EventLoop:

    event_loop = asyncio.get_event_loop()  # 创建事件循环
    # future = asyncio.ensure_future(run(10))
    results = event_loop.run_until_complete(run(5))


