from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings


class FDFSStorage(Storage):

    def __init__(self, client_conf=None, tracker_server=None):
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf
        if tracker_server is None:
            tracker_server = settings.FDFS_URL
        self.tracker_server = tracker_server

    # 打开文件时使用
    def _open(self, name, mode='rb'):
        pass

    # 保存文件时使用 name 文件名　content 包含文件上传内容的File类的对象
    def _save(self, name, content):
        client = Fdfs_client(self.client_conf)
        res = client.upload_appender_by_buffer(content.read())
        if res.get('Status') != 'Upload successed':
            # 上传失败
            raise Exception('upload file to fastdfs failed')
        # 获取返回的文件ID
        filename = res.get('Remote file_id')
        return filename

    # django判断文件名是否可用
    def exists(self, name):
        return False

    # 返回访问文件的路径
    def url(self, name):
        return self.tracker_server + name

