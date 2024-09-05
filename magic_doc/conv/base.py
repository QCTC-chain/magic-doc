'''
Author: dbliu shaxunyeman@gmail.com
Date: 2024-09-02 17:55:19
LastEditors: dbliu shaxunyeman@gmail.com
LastEditTime: 2024-09-05 09:00:49
FilePath: /magic-doc/magic_doc/conv/base.py
Description: 
'''

from abc import ABC, abstractmethod

from magic_doc.progress.pupdator import ConvProgressUpdator
from magic_pdf.rw.AbsReaderWriter import AbsReaderWriter
class BaseConv(ABC):
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def to_md(self, bits: bytes | str, pupdator:ConvProgressUpdator, **kwargs) -> str:
        return NotImplemented

    def to_mid_result(self, rw: AbsReaderWriter,  bits: bytes | str, pupdator:ConvProgressUpdator) -> list[dict] | dict:
        pupdator.update(100)
        return {}


class ParseFailed(Exception):
    pass  