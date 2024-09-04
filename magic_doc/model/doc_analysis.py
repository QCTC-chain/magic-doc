import logging
import time

import torch
import yaml

from magic_pdf.model.pdf_extract_kit import CustomPEKModel
from magic_doc.utils.yaml_load import patch_yaml_load_with_env

logging.disable(logging.WARNING)


class DocAnalysis(object):
    """
    Description:
      class definition of DocAnalysis module:
    """

    def __init__(
        self, 
        models_dir = '/tmp/models',
        configs="magic_doc/resources/model/model_configs.yaml", 
        **kwargs
    ):
        """
        Description:
          initialize the class instance

        Parameters:
          configs: path to config that contains model weights.
          apply_layout: do layout analysis or not, must be True (defaults to be True).
          apply_formula: do formulat detection and recognition or not, defaults to be False.
          apply_ocr: do ocr(text detection and recognition) or not, defaults to be False.

        """
        self.configs = patch_yaml_load_with_env(configs, "model", yaml.FullLoader)  # load config and patch with env var !
        model_input = {
            "ocr": kwargs.get("apply_ocr", self.configs["models"]["ocr"]),
            "show_log": True,
            "layout": kwargs.get("apply_layout", self.configs["models"]["layout"]), 
            "formula": kwargs.get("apply_formula", self.configs["models"]["formula"]), 
            "table_config": kwargs.get("table_config", self.configs["models"]["table_config"]),
            "models_dir": models_dir,
            "device": "cuda" if torch.cuda.is_available() else "cpu",
        }
        self._pdf_extract_model = CustomPEKModel(**model_input)
        
        logging.info("DocAnalysis init done!")

    def __call__(self, image_list):
        """
        Description:
          do document analysis on input images

        Parameters:
          image_list: list of image array, [np.array, ...]

        Return:
          result: doc analysis result
        """
        model_json = []
        doc_analyze_start = time.time()
        for index, img_dict in enumerate(image_list):
            img = img_dict["img"]
            page_width = img_dict["width"]
            page_height = img_dict["height"]
            result = self._pdf_extract_model(img)
            page_info = {"page_no": index, "height": page_height, "width": page_width}
            page_dict = {"layout_dets": result, "page_info": page_info}
            model_json.append(page_dict)
        doc_analyze_cost = time.time() - doc_analyze_start
        logging.info(f"doc analyze cost: {doc_analyze_cost}")

        return model_json
