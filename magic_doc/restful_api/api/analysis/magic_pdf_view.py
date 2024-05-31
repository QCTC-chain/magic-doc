import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from flask import request, current_app
from flask_restful import Resource
from marshmallow import ValidationError
from pathlib import Path
from magic_doc.pdf_transform import DocConverter, S3Config
from .serialization import MagicPdfSchema
from magic_pdf.libs.MakeContentConfig import DropMode, MakeMode
from magic_pdf.dict2md.ocr_mkcontent import union_make
from magic_doc.restful_api.common.oss.oss import Oss
from .ext import upload_image_to_oss
from magic_doc.restful_api.common.custom_response import generate_response
from loguru import logger

executor = ThreadPoolExecutor()


class MagicPdfView(Resource):
    @logger.catch
    def post(self):
        """
        PDF解析，将markdown结果上传至服务器
        """
        t0 = time.time()
        magic_pdf_schema = MagicPdfSchema()
        try:
            params = magic_pdf_schema.load(request.get_json())
        except ValidationError as err:
            return generate_response(code=400, msg=err.messages)
        pdf_path = params.get('pageUrl')
        # ############ pdf解析  ###############
        file_name = str(Path(pdf_path).stem)
        pf_path = f"/tmp/{file_name}.txt"
        pdf_dir = f"{current_app.static_folder}/pdf/{file_name}"
        NULL_IMG_DIR = f"{current_app.static_folder}/pdf/{file_name}"
        app_config = current_app.config
        if not Path(NULL_IMG_DIR).exists():
            Path(NULL_IMG_DIR).mkdir(parents=True, exist_ok=True)
        if pdf_path.startswith("http://") or pdf_path.startswith("https://"):
            download_pdf = requests.get(pdf_path, stream=True)
            pdf_path = f"{pdf_dir}/{file_name}.pdf"
            with open(pdf_path, "wb") as wf:
                wf.write(download_pdf.content)
            doc_conv = DocConverter(None)
        elif pdf_path.startswith("s3://"):
            s3_config = S3Config(app_config["S3AK"], app_config["S3SK"], app_config["S3ENDPOINT"])
            doc_conv = DocConverter(s3_config)
        else:
            doc_conv = DocConverter(None)
        t1 = time.time()
        logger.info(f"param init cost_time:{t1 - t0}")
        result = doc_conv.convert_to_mid_result(pdf_path, pf_path, 60)
        t2 = time.time()
        logger.info(f"pdf doc_conv cost_time:{t2 - t1}")
        md_content = union_make(result[0], MakeMode.MM_MD, DropMode.NONE, NULL_IMG_DIR)
        t3 = time.time()
        logger.info(f"make markdown cost_time:{t3 - t2}")
        local_md_path = f"{pdf_dir}/{file_name}.md"
        with open(local_md_path, "w") as f:
            f.write(md_content)
        t4 = time.time()
        logger.info(f"save markdown cost_time:{t4 - t3}")
        _t0 = time.time()
        oss_client = Oss(
            app_config["AccessKeyID"],
            app_config["AccessKeySecret"],
            app_config["BucketName"],
            app_config["Endpoint"],
            app_config["UrlExpires"]
        )
        img_list = Path(f"{NULL_IMG_DIR}/images").glob('*') if Path(f"{NULL_IMG_DIR}/images").exists() else []
        for img_path in img_list:
            executor.submit(upload_image_to_oss, oss_client, file_name, img_path, NULL_IMG_DIR, app_config["BucketName"], "md_content")
        _t1 = time.time()
        logger.info(f"upload img cost_time:{_t1 - _t0}")
        md_object_name = f"pdf/{file_name}/{file_name}.md"
        oss_rep = oss_client.put_file(app_config["BucketName"], md_object_name, local_md_path)
        md_link = oss_rep["file_link"]
        _t2 = time.time()
        logger.info(f"upload md cost_time:{_t2 - _t1}")

        return generate_response(markDownUrl=md_link)
