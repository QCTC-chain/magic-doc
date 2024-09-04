'''
Author: dbliu shaxunyeman@gmail.com
Date: 2024-09-02 17:55:19
LastEditors: dbliu shaxunyeman@gmail.com
LastEditTime: 2024-09-03 17:47:53
FilePath: /magic-doc/magic_doc/model/seq_layout.py
Description: 
'''


from magic_doc.model.sub_modules.layoutlmv3.model_init import Layoutlmv3_Predictor

class SeqLayout:
    def __init__(self, config, device):
        self.model = Layoutlmv3_Predictor(config, device)

    def __call__(self, params):
        """
        params: list[(idx, image)]
        """
        if len(params) == 0:
            return []

        results = []
        for idx, image in params:
            layout_res = self.model(image)
            results.append((idx, layout_res))
        return results

