import os

from magic_pdf.libs.MakeContentConfig import DropMode, MakeMode
from magic_pdf.pipe.UNIPipe import UNIPipe
from magic_pdf.pipe.OCRPipe import OCRPipe
from magic_pdf.pipe.TXTPipe import TXTPipe
from magic_doc.conv.base import BaseConv

from magic_doc.progress.filepupdator import FileBaseProgressUpdator
from magic_doc.progress.pupdator import ConvProgressUpdator
from magic_doc.utils import get_repo_directory
from magic_doc.utils.null_writer import NullWriter
from magic_pdf.dict2md.ocr_mkcontent import union_make
from magic_pdf.libs.json_compressor import JsonCompressor
from magic_pdf.rw.AbsReaderWriter import AbsReaderWriter
from magic_pdf.rw.DiskReaderWriter import DiskReaderWriter
from magic_pdf.tools.common import prepare_env
from magic_doc.common.default_config import DEFAULT_CONFIG, PdfHqParseMethod


NULL_IMG_DIR = "/tmp"

class SingletonModelWrapper:

    def __new__(cls, models_dir):
        if not hasattr(cls, "instance"):
            from magic_doc.model.doc_analysis import DocAnalysis
            apply_ocr = os.getenv("APPLY_OCR", "TRUE") == "TRUE" 
            apply_layout = os.getenv("APPLY_LAYOUT", "TRUE") == "TRUE" 
            apply_formula = os.getenv("APPLY_FORMULA", "FALSE") == "TRUE"
            apply_table = os.getenv("APPLY_TABLE", "FALSE") == "TRUE"
            
            cls.instance = super(SingletonModelWrapper, cls).__new__(cls)
            cls.instance.doc_analysis = DocAnalysis(  # type: ignore
                models_dir=models_dir,
                configs=os.path.join(
                    get_repo_directory(), "resources/model/model_configs.yaml"
                ),
                apply_ocr=apply_ocr, 
                apply_layout=apply_layout, 
                apply_formula=apply_formula,
                table_config={
                    'is_table_recog_enable': apply_table,
                    'max_time': 400,
                }
            )
        return cls.instance
    
    def __call__(self, bits: bytes):
        from magic_pdf.model.doc_analyze_by_custom_model import load_images_from_pdf
        images = load_images_from_pdf(bits, dpi=200)
        return self.doc_analysis(images) # type: ignore

class Pdf(BaseConv):

    def __init__(self, models_dir):
        super().__init__()
        self.models_dir = models_dir

    def __construct_pdf_pipe(self, bits, model_list, image_writer, parse_method):
        if parse_method == PdfHqParseMethod.AUTO:
            jso_useful_key = {"_pdf_type": "", "model_list": model_list}
            pipe = UNIPipe(bits, jso_useful_key, image_writer, is_debug=True)  # type: ignore
        elif parse_method == PdfHqParseMethod.OCR:
            pipe = OCRPipe(bits, model_list, image_writer, is_debug=True)  # type: ignore
        elif parse_method == PdfHqParseMethod.TXT:
            pipe = TXTPipe(bits, model_list, image_writer, is_debug=True)  # type: ignore
        else:
            raise Exception("unknown parse method under hq mode")
        return pipe


    def to_md(self, bits: bytes | str, pupdator: ConvProgressUpdator, **kwargs) -> str:

        output_dir = kwargs.get('output', None)
        pdf_file_name = kwargs.get('file_name', None)
        parse_method = kwargs.get('method', None)
        parse_method = parse_method if parse_method else DEFAULT_CONFIG["pdf"]["hq"]["parsemethod"]

        if output_dir and pdf_file_name:
            local_image_dir, local_md_dir = prepare_env(
                output_dir, 
                pdf_file_name, 
                parse_method,
            )
            image_writer, md_writer = DiskReaderWriter(local_image_dir), DiskReaderWriter(local_md_dir)
            image_dir = str(os.path.basename(local_image_dir))
        else:
            image_writer = NullWriter()
            md_writer = None
            image_dir = None

        model_proc = SingletonModelWrapper(self.models_dir)
        pupdator.update(0)

        model_list = model_proc(bits)  # type: ignore
        pupdator.update(50)
        
        pipe = self.__construct_pdf_pipe(bits, model_list, image_writer, parse_method)
        pipe.pipe_classify() # 默认ocrpipe的时候不需要再做分类，可以节省时间
        pipe.pipe_parse()
        pupdator.update(100)

        if not image_dir:
            pdf_mid_data = JsonCompressor.decompress_json(pipe.get_compress_pdf_mid_data())
            pdf_info_list = pdf_mid_data["pdf_info"]
            md_content = union_make(pdf_info_list, MakeMode.NLP_MD, DropMode.NONE, NULL_IMG_DIR)
        else:
            md_content = pipe.pipe_mk_markdown(
                image_dir, 
                drop_mode=DropMode.NONE, 
                md_make_mode=MakeMode.MM_MD
            )
            if md_writer:
                md_writer.write(
                    content=md_content,
                    path=f"{pdf_file_name}.md",
                    mode=AbsReaderWriter.MODE_TXT,
                )

        return md_content # type: ignore

    def to_mid_result(self, image_writer: AbsReaderWriter, bits: bytes | str, pupdator: ConvProgressUpdator) -> list[dict] | dict:
        model_proc = SingletonModelWrapper()
        pupdator.update(0)

        model_list = model_proc(bits)  # type: ignore
        pupdator.update(50)
        # jso_useful_key = {
        #     "_pdf_type": "",
        #     "model_list": model_list,
        # }
        pipe = self.__construct_pdf_pipe(bits, model_list, image_writer)
        # pipe.pipe_classify()
        pipe.pipe_parse()
        pupdator.update(100)

        pdf_mid_data = JsonCompressor.decompress_json(pipe.get_compress_pdf_mid_data())
        pdf_info_list = pdf_mid_data["pdf_info"]
        return pdf_info_list

if __name__ == "__main__":
    with open("/opt/data/pdf/20240423/pdf_test2/ol006018w.pdf", "rb") as f:
        bits_data = f.read()
        parser = Pdf(models_dir='/Users/dbliu/work/machine-learn/PDF-Extract-Kit/models')
        md_content = parser.to_md(
            bits_data, FileBaseProgressUpdator("debug/progress.txt")
        )
        with open("debug/pdf2md.by_model.md", "w") as f:
            f.write(md_content) # type: ignore

