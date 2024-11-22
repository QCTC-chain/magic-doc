'''
Author: dbliu shaxunyeman@gmail.com
Date: 2024-11-19 15:38:18
LastEditors: shaxunyeman shaxunyeman@gmail.com
LastEditTime: 2024-11-21 17:53:07
FilePath: /magic-doc/magic_doc/restful_api/api/analysis/ext.py
Description: 
'''
import time
from pathlib import Path
from loguru import logger


def upload_image_to_oss(oss_client, file_name, img_path, NULL_IMG_DIR, bucket_name):
    img_object_name = f"pdf/{file_name}/{Path(img_path).name}"
    local_img_path = f"{NULL_IMG_DIR}/images/{Path(img_path).name}"
    t3 = time.time()
    oss_rep = oss_client.put_file(bucket_name, img_object_name, local_img_path)
    t4 = time.time()
    logger.info(f"upload img:{t4 - t3}")
    file_link = oss_rep.object_name
    return str(img_path), file_link


def upload_md_to_oss(oss_client, bucket_name, md_object_name, md_content):
    t3 = time.time()
    oss_rep = oss_client.pub_object(bucket_name, md_object_name, md_content)
    t4 = time.time()
    logger.info(f"upload md:{t4 - t3}")
    md_link = oss_rep.object_name
    return md_link

