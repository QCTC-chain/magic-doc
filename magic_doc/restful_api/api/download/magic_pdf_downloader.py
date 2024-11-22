'''
Author: dbliu shaxunyeman@gmail.com
Date: 2024-11-21 20:42:20
LastEditors: shaxunyeman shaxunyeman@gmail.com
LastEditTime: 2024-11-22 18:36:37
FilePath: /magic-doc/magic_doc/restful_api/api/download/magic_pdf_downloader.py
Description: 
'''
import io
from flask import request, current_app, send_file
from flask_restful import Resource
from marshmallow import ValidationError
from loguru import logger
from .serialization import MagicPdfDownloadSchema
from magic_doc.restful_api.common.custom_response import generate_response
from magic_doc.restful_api.common.oss.oss import Oss

class MagicPdfDownloader(Resource):
    
    @logger.catch
    def post(self):
        
        magic_pdf_download_schema = MagicPdfDownloadSchema()
        try:
            params = magic_pdf_download_schema.load(request.get_json())
        except ValidationError as err:
            return generate_response(code=400, msg=err.messages)
        
        objectName = params.get('objectName')
        app_config = current_app.config

        oss_client = Oss(
            app_config["AccessKeyID"],
            app_config["AccessKeySecret"],
            app_config["BucketName"],
            app_config["Endpoint"],
            app_config["UrlExpires"]
        )

        try:
            response = oss_client.download_object(app_config["BucketName"], objectName)
            file_data = response.read(decode_content=True)

            # 将文件数据放入内存中的字节流
            file_stream = io.BytesIO(file_data)

            # 设置字节流的位置为起始位置，以便后续读取
            file_stream.seek(0)

            # 使用send_file发送文件给客户端，设置合适的参数
            return send_file(
                file_stream,
                download_name=objectName,
                mimetype='application/octet-stream'
            )
        except Exception as e:
            # 如果出现异常，返回错误信息
            return generate_response(code=400, msg=str(e))
        finally:
            response.close()
            response.release_conn()