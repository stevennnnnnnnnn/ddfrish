from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client, get_tracker_conf
from django.conf import settings


class FdfsStorage(Storage):
    """自定义的fastdfs存储类"""

    def __init__(self, tracker_conf=None, domain=None):
        """
        :param tracker_conf: fdfs配置文件地址
        :param domain: 服务器ip:port
        """
        if tracker_conf is None:
            self.tracker_conf = settings.FDFS_CLIENT_CONF
        else:
            self.tracker_conf = tracker_conf

        if domain is None:
            self.domain = settings.FDFS_STORAGE_URL
        else:
            self.domain = domain

    def open(self, name, mode='rb'):
        """打开文件文件时使用"""
        pass

    def save(self, name, content, max_length=None):
        """保存文件时使用
        :param name: 上传文件的名字
        :param content: 包含上传文件内容的File对象
        :param max_length:
        """
        # trackers = get_tracker_conf(self.tracker_conf)
        client = Fdfs_client(self.tracker_conf)
        # res = client.upload_by_buffer(content.read())
        res = client.upload_appender_by_buffer(content.read())
        if res.get('Status') != 'Upload successed.':
            # 上传失败
            raise Exception('上传失败')
        filename = res.get('Remote file_id').split('/', 1)[1]
        return '/' + filename

    def exists(self, name):
        return False

    def url(self, name):
        return self.domain + name

