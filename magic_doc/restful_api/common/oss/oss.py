import io
import oss2
from minio import Minio
from magic_doc.restful_api.common.ext import singleton_func
from loguru import logger


@singleton_func
class Oss(object):
    def __init__(self, access_key_id, access_secret_key, bucket_name, endpoint, expires=60):
        self.minio_client = Minio(
            endpoint,
            access_key=access_key_id,
            secret_key=access_secret_key,
            secure=False 
        )

        if not self.minio_client.bucket_exists(bucket_name=bucket_name):
            self.create_bucket(bucket_name=bucket_name)

    def create_bucket(self, bucket_name=None):
        """
        创建存储空间
        :param bucket_name:  bucket名称
        :return:
        """
        self.minio_client.make_bucket(bucket_name=bucket_name)
        return True

    def delete_bucket(self, bucket_name=None):
        """
        删除存储空间
        :param bucket_name:  bucket名称
        :return:
        """
        self.minio_client.remove_bucket(bucket_name=bucket_name)
        

    def pub_object(self, bucket_name=None, object_name=None, object_data=None):
        """
        上传文件
            Str
            Bytes
            Unicode
            Stream
        :param bucket_name:  bucket名称
        :param object_name:  不包含Bucket名称组成的Object完整路径
        :param object_data:
        :return:
        """
        if isinstance(object_data, str):
            bytes = object_data.encode('utf-8')

        return self.minio_client.put_object(
            bucket_name, 
            object_name,
            data=io.BytesIO(bytes), 
            length=len(object_data))

    def put_file(self, bucket_name=None, object_name=None, file_path=None):
        """
        上传文件
            file
        :param bucket_name:  bucket名称
        :param object_name:  不包含Bucket名称组成的Object完整路径
        :param file_path:   文件路径
        :return:
        """
        return self.minio_client.fput_object(
            bucket_name=bucket_name, 
            object_name=object_name, 
            file_path=file_path)

    def delete_objects(self, bucket_name=None, object_name=None):
        """
        批量删除文件
        :param bucket_name:  bucket名称
        :param object_name:  不包含Bucket名称组成的Object完整路径列表
        :return:
        """
        from minio.deleteobjects import DeleteObject
        delete_object_list = map(
            lambda x: DeleteObject(x.object_name),
            self.minio_client.list_objects(bucket_name=bucket_name, recursive=True),
        )
        self.minio_client.remove_objects(bucket_name, delete_object_list)

    def download_object(self, bucket_name=None, object_name=None):
        """
        下载文件到本地
        :param bucket_name:  bucket名称
        :param object_name:  不包含Bucket名称组成的Object完整路径
        :return:
        """
        return self.minio_client.get_object(bucket_name=bucket_name, object_name=object_name)

    def download_file(self, bucket_name=None, object_name=None, save_path=None):
        """
        下载文件到本地
        :param bucket_name:  bucket名称
        :param object_name:  不包含Bucket名称组成的Object完整路径
        :param save_path:  保存路径
        :return:
        """
        self.minio_client.fget_object(
            bucket_name=bucket_name, 
            object_name=object_name, 
            file_path=save_path)

if __name__ == '__main__':
    bucket_name = 'magic-doc'
    oss_client = Oss(
        '6b6C5NCmgq4F0kqoYVvA', 
        'C0QJJ2QH5FkzowndWDn5Vu2mxQ3Qi7mfrI2BwMLm', 
        bucket_name,
        '127.0.0.1:9000')

    result = oss_client.pub_object(
        bucket_name=bucket_name,
        object_name="pdf/报销/0.md",
        object_data="shatian is a nice town."
    )

    print(f'object_name: {result.object_name}')
    
    result = oss_client.put_file(
        bucket_name, 
        '莱芜孟家储能电站01月月报.docx',
        '/Users/dbliu/Desktop/储能日报每日上报/莱芜孟家储能电站01月月报.docx'
    )

    print(f'object name: {result.object_name}')

    oss_client.download_file(
        bucket_name=bucket_name, 
        object_name='pdf/结账单20241104_1/0.md',
        save_path='/Users/dbliu/Desktop/0.md'
    )