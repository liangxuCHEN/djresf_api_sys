from qiniu import Auth, put_file, etag, urlsafe_base64_encode
from qiniu import BucketManager
import os
import zipfile



def un_zip(file_name):
    """unzip zip file"""
    file_paths = []
    zip_file = zipfile.ZipFile(file_name)
    if os.path.isdir(file_name + "_files"):
        pass
    else:
        os.mkdir(file_name + "_files")
    for name in zip_file.namelist():
        zip_file.extract(name, file_name + "_files/")
        file_paths.append({"path":"%s_files/%s" % (file_name, name), "name":name})
    zip_file.close()

    return file_paths


def handle_uploaded_file(f, file_name):
    with open(file_name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return un_zip(file_name)

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

    def get_token(self, bucket_name):
        return self.q.upload_token(bucket_name),

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

    def list_files(self, bucket_name, limit=500, prefix=None, delimiter=None, marker=None):
        ret, eof, info = self.bucket.list(bucket_name, prefix, marker, limit, delimiter)
        return ret

    def list_buckets(self):
        ret, info = self.bucket.buckets()
        print(info)
        return ret


