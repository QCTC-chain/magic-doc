'''
Author: dbliu shaxunyeman@gmail.com
Date: 2024-09-02 17:55:19
LastEditors: dbliu shaxunyeman@gmail.com
LastEditTime: 2024-09-04 09:37:59
FilePath: /magic-doc/test/test_docconv.py
Description: 
'''

from magic_doc.docconv import ConvException, S3Config, DocConverter

def test_conv_localfile():
    convert = DocConverter(None, models_dir='/Users/dbliu/work/machine-learn/PDF-Extract-Kit/models')
    many_docs = ["/path/docs/mypdf.pdf", "/path/docs/mydoc.docx", "/path/docs/mydoc.doc", "/path/docs/mydoc.pptx", "/path/docs/mydoc.ppt"]
    for i, doc in enumerate(many_docs):
        try:
            markdown = convert.convert(doc, f"/path/progress/progress-{i}.txt")
            # do something with markdown
        except ConvException as e:
            assert False, f"Failed to convert {doc}, Reason: {e.message}"
        except Exception as e:
            assert False, f"Failed to convert {doc}: {e}"
        
        
def test_conv_s3file():
    s3cfg = S3Config("ak", "sk", "endpoint")
    convert = DocConverter(s3cfg, models_dir='/Users/dbliu/work/machine-learn/PDF-Extract-Kit/models')
    many_docs = ["s3://bucket/mypdf.pdf", "s3://bucket/mydoc.docx", "s3://bucket/mydoc.doc", "s3://bucket/mydoc.pptx", "s3://bucket/mydoc.ppt"]
    for i, doc in enumerate(many_docs):
        try:
            markdown = convert.convert(doc, f"/path/progress/progress-{i}.txt")
            # do something with markdown
        except ConvException as e:
            assert False, f"Failed to convert {doc}, Reason: {e.message}"
        except Exception as e:
            assert False, f"Failed to convert {doc}: {e}"
            