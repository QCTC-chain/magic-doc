'''
Author: dbliu shaxunyeman@gmail.com
Date: 2024-11-21 20:41:50
LastEditors: shaxunyeman shaxunyeman@gmail.com
LastEditTime: 2024-11-21 20:49:40
FilePath: /magic-doc/magic_doc/restful_api/api/download/__init__.py
Description: 
'''
from flask import Blueprint
from .magic_pdf_downloader import *
from ..extentions import Api

download_blue = Blueprint('download', __name__, url_prefix='/download')

api = Api(download_blue)
api.add_resource(MagicPdfDownloader, '/pdf')