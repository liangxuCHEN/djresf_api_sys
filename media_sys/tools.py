from qiniu import Auth, put_file, etag, urlsafe_base64_encode
from qiniu import BucketManager


class Qiqiu(object):

    def __init__(self, ak, sk):
        self.ak = ak
        self.sk = sk
        self.q = Auth(ak, sk)
        self.bucket = BucketManager(self.q)


    def create_bucket(self, bucket_name, region='z2'):
        # "填写存储区域代号  z0:华东, z1:华北, z2:华南, na0:北美"
        ret, info = self.bucket.mkbucketv2(bucket_name, region)
        print(info)
        print(ret)
        return info.status_code == 200

    def bucket_key_exist(self, bucket_name, key):
        ret, info = self.bucket.stat(bucket_name, key)
        if 'error' in ret:
            return False
        else:
            return ret['hash']


    def upload(self, bucket_name, key, file_path):
        """
        :param key: 上传到七牛后保存的文件名
        :file_path: 要上传文件的本地路径
        :return: 
        """
        # 生成上传 Token，可以指定过期时间等
        token = self.q.upload_token(bucket_name, key, 3600)
        ret, info = put_file(token, key, file_path)
        #print(ret)
        #print(info)
        return ret['hash'] == etag(file_path)

    def fetch(self, bucket_name, key, url):
        """
        把网络照片保存起来
        :param bucket_name: 
        :param key: 
        :param url: 
        :return: 
        """
        ret, info = self.bucket.fetch(url, bucket_name, key)
        print(info)
        return ret['key'] == key

    def list_files(self, limit=10, prefix=None, delimiter=None, marker=None):
        ret, eof, info = self.bucket.list(bucket_name, prefix, marker, limit, delimiter)
        print(info)
        print(ret)
        return ret['items']

    def list_buckets(self):
        ret, info = self.bucket.buckets()
        print(info)
        return ret


