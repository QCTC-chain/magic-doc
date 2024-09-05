'''
Author: dbliu shaxunyeman@gmail.com
Date: 2024-09-02 17:55:19
LastEditors: dbliu shaxunyeman@gmail.com
LastEditTime: 2024-09-05 10:03:21
FilePath: /magic-doc/magic_doc/common/default_config.py
Description: 
'''

from magic_doc.utils.yaml_load import patch_dict_with_env

class PdfFastParseMethod:
    AUTO = "auto"
    FAST = "fast"
    LITEOCR = "lite_ocr"

class PdfHqParseMethod:
    AUTO = "auto"
    OCR = "ocr"
    TXT = "txt"


DEFAULT_CONFIG = {
    "pdf": {
        "fast": {
            "parsemethod": PdfFastParseMethod.AUTO,
            "liteocrmodelinstance": 1,
        }, 
        "hq": {
            "parsemethod": PdfHqParseMethod.AUTO,
        }
    }
}


DEFAULT_CONFIG = patch_dict_with_env("filter", DEFAULT_CONFIG)

