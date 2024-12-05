'''
Author: dbliu shaxunyeman@gmail.com
Date: 2024-11-19 15:38:18
LastEditors: shaxunyeman shaxunyeman@gmail.com
LastEditTime: 2024-11-28 10:26:50
FilePath: /magic-doc/magic_doc/restful_api/api/analysis/magic_pdf_view.py
Description: 
'''
import os
import json
import re
import time
import requests
from flask import request, current_app
from flask_restful import Resource
from marshmallow import ValidationError
from pathlib import Path
from magic_doc.pdf_transform import DocConverter, S3Config
from magic_pdf.dict2md.ocr_mkcontent import ocr_mk_mm_markdown_with_para_and_pagination
from magic_doc.restful_api.common.oss.oss import Oss
from .ext import upload_image_to_oss, upload_md_to_oss
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from magic_doc.restful_api.common.custom_response import generate_response
from loguru import logger

executor = ThreadPoolExecutor()

CONVERT_TIME_OUT = 1800

class MagicPdfView(Resource):

    def _save_uploaded_file(self):
        # 检查请求中是否包含文件数据
        if 'doc_file' not in request.files:
            raise Exception("No file part in the request")

        file = request.files['doc_file']
        if file.filename == '':
            raise Exception("No selected file")

        doc_name = request.form.get('doc_name')
        if not doc_name:
            doc_name = file.filename

        doc_type = request.form.get('doc_type')
        if not doc_type:
            doc_type = str(Path(doc_name).suffix).strip('.')

        file_name = str(Path(doc_name).stem)
        upload_dir = f"{current_app.static_folder}/{doc_type}/{file_name}"
        file_path = os.path.join(upload_dir, doc_name)
        if not Path(upload_dir).exists():
            Path(upload_dir).mkdir(parents=True, exist_ok=True)
        file.save(file_path)

        return file_name, doc_type, file_path
    
    def _analysis_pdf(
            self, 
            file_name: str,
            file_type: str,
            pdf_path: str,
            pf_path: str,
            image_path: str,
            doc_conv: DocConverter, 
            oss_client: Oss):
        app_config = current_app.config
        t1 = time.time()
        result = doc_conv.convert_to_mid_result(pdf_path, pf_path, CONVERT_TIME_OUT, image_path=image_path)
        t2 = time.time()
        logger.info(f"pdf doc_conv cost_time:{t2 - t1}")
        md_content = json.dumps(ocr_mk_mm_markdown_with_para_and_pagination(result[0], image_path), ensure_ascii=False)
        t3 = time.time()
        logger.info(f"make markdown cost_time:{t3 - t2}")

        _t0 = time.time()
        img_list = Path(f"{image_path}/images").glob('*') if Path(f"{image_path}/images").exists() else []
        all_task = [executor.submit(upload_image_to_oss, oss_client, file_name, img_path, image_path, app_config["BucketName"]) for img_path in img_list]
        wait(all_task, return_when=ALL_COMPLETED)
        for task in all_task:
            task_result = task.result()
            regex = re.compile(fr'.*\((.*?{Path(task_result[0]).name})')
            regex_result = regex.search(md_content)
            if regex_result:
                md_content = md_content.replace(regex_result.group(1), task_result[1])
        _t1 = time.time()
        logger.info(f"upload img cost_time:{_t1 - _t0}")

        all_md_task = [executor.submit(upload_md_to_oss, oss_client, app_config["BucketName"], f"{file_type}/{file_name}/{md.get('page_no', n)}.md", md["md_content"]) for n, md in enumerate(json.loads(md_content))]
        wait(all_md_task, return_when=ALL_COMPLETED)
        md_link_list = []
        for task in all_md_task:
            task_result = task.result()
            md_link_list.append(task_result)
        _t2 = time.time()
        logger.info(f"upload md cost_time:{_t2 - _t1}")

        return generate_response(markDownUrl=md_link_list)

    def _analysis_doc(
            self, 
            file_name: str,
            file_type: str,
            pdf_path: str,
            pf_path: str,
            image_path: str,
            doc_conv: DocConverter, 
            oss_client: Oss):
        app_config = current_app.config
        md_content, cost_time = doc_conv.convert(pdf_path, pf_path, CONVERT_TIME_OUT)
        logger.info(f"make markdown cost_time:{cost_time}")

        _t0 = time.time()
        img_list = Path(f"{image_path}/images").glob('*') if Path(f"{image_path}/images").exists() else []
        all_task = [executor.submit(upload_image_to_oss, oss_client, file_name, img_path, image_path, app_config["BucketName"]) for img_path in img_list]
        wait(all_task, return_when=ALL_COMPLETED)
        for task in all_task:
            task_result = task.result()
            regex = re.compile(fr'.*\((.*?{Path(task_result[0]).name})')
            regex_result = regex.search(md_content)
            if regex_result:
                md_content = md_content.replace(regex_result.group(1), task_result[1])
        _t1 = time.time()
        logger.info(f"upload img cost_time:{_t1 - _t0}")

        all_md_task = [executor.submit(upload_md_to_oss, oss_client, app_config["BucketName"], f"{file_type}/{file_name}/{n}.md", md) for n, md in enumerate([md_content])]
        wait(all_md_task, return_when=ALL_COMPLETED)
        md_link_list = []
        for task in all_md_task:
            task_result = task.result()
            md_link_list.append(task_result)
        _t2 = time.time()
        logger.info(f"upload md cost_time:{_t2 - _t1}")

        return generate_response(markDownUrl=md_link_list)

    @logger.catch
    def post(self):
        """
        PDF解析，将markdown结果上传至服务器
        """
        t0 = time.time()
        try:
            file_name, pdf_type, pdf_path = self._save_uploaded_file()
        except Exception as e:
            return generate_response(code=400, msg=e)

        # ############ pdf解析  ###############
        # file_name = str(Path(pdf_path).stem)
        pf_path = f"/tmp/{file_name}.txt"
        pdf_dir = f"{current_app.static_folder}/{pdf_type}/{file_name}"
        NULL_IMG_DIR = f"{current_app.static_folder}/{pdf_type}/{file_name}"
        app_config = current_app.config
        models_dir = app_config['ModelsDir']
        if not Path(NULL_IMG_DIR).exists():
            Path(NULL_IMG_DIR).mkdir(parents=True, exist_ok=True)
        if pdf_path.startswith("http://") or pdf_path.startswith("https://"):
            download_pdf = requests.get(pdf_path, stream=True)
            pdf_path = f"{pdf_dir}/{file_name}.pdf"
            with open(pdf_path, "wb") as wf:
                wf.write(download_pdf.content)
            doc_conv = DocConverter(None, models_dir=models_dir)
        elif pdf_path.startswith("s3://"):
            s3_config = S3Config(app_config["S3AK"], app_config["S3SK"], app_config["S3ENDPOINT"])
            doc_conv = DocConverter(s3_config, models_dir=models_dir)
        else:
            doc_conv = DocConverter(None, models_dir=models_dir)
        t1 = time.time()
        logger.info(f"param init cost_time:{t1 - t0}")

        oss_client = Oss(
            app_config["AccessKeyID"],
            app_config["AccessKeySecret"],
            app_config["BucketName"],
            app_config["Endpoint"],
            app_config["UrlExpires"]
        )
        
        if pdf_type == 'pdf':
            return self._analysis_pdf(
                file_name=file_name,
                file_type=pdf_type,
                pdf_path=pdf_path,
                pf_path=pf_path,
                image_path=NULL_IMG_DIR,
                doc_conv=doc_conv,
                oss_client=oss_client)
        else:
            return self._analysis_doc(
                file_name=file_name,
                file_type=pdf_type,
                pdf_path=pdf_path,
                pf_path=pf_path,
                image_path=NULL_IMG_DIR,
                doc_conv=doc_conv,
                oss_client=oss_client)