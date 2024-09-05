<div id="top"></div>
<div align="center">

[![license](https://img.shields.io/github/license/InternLM/magic-doc.svg)](https://github.com/InternLM/magic-doc/tree/main/LICENSE)
[![issue resolution](https://img.shields.io/github/issues-closed-raw/InternLM/magic-doc)](https://github.com/InternLM/magic-doc/issues)
[![open issues](https://img.shields.io/github/issues-raw/InternLM/magic-doc)](https://github.com/InternLM/magic-doc/issues)

<p align="center">
    👋 加入我们 <a href="https://discord.gg/xa29JuW87d" target="_blank">Discord</a> 和 <a href="https://github.com/InternLM/InternLM/assets/25839884/a6aad896-7232-4220-ac84-9e070c2633ce" target="_blank">微信社区</a>
</p>

[English](README.md) | [简体中文](README_zh-CN.md)

</div>

<div align="center">

</div>


### 安装
前置依赖： python3.10

安装依赖

**linux/osx** 

```bash
apt-get/yum/brew install libreoffice
```

**windows**
```text
安装 libreoffice 
添加 "install_dir\LibreOffice\program" to 环境变量 PATH
```


安装 Magic-Doc


```bash
pip install qctc-doc[cpu] --extra-index-url https://wheels.myhloli.com # cpu version
or
pip install qctc-doc[gpu] --extra-index-url https://wheels.myhloli.com # gpu version
```


## 简介

Magic-Doc 是一个轻量级、开源的用于将多种格式的文档（PPT/PPTX/DOC/DOCX/PDF）转化为 markdown 格式的工具。支持转换本地文档或者位于 AWS S3 上的文件


## 使用示例

```python
# for local file
from magic_doc.docconv import DocConverter, S3Config
converter = DocConverter(s3_config=None)
markdown_content, time_cost = converter.convert("some_doc.pptx", conv_timeout=300)
```

```python
# for remote file located in aws s3
from magic_doc.docconv import DocConverter, S3Config

s3_config = S3Config(ak='${ak}', sk='${sk}', endpoint='${endpoint}')
converter = DocConverter(s3_config=s3_config)
markdown_content, time_cost = converter.convert("s3://some_bucket/some_doc.pptx", conv_timeout=300)
```


## 性能
环境：AMD EPYC 7742 64-Core Processor, NVIDIA A100, Centos 7

| 文件类型        | 转化速度| 
| ------------------ | -------- | 
| PDF (digital)      | 347 (page/s)   | 
| PDF (ocr)          | 2.7 (page/s)   | 
| PPT                | 20 (page/s)    | 
| PPTX               | 149 (page/s)   | 
| DOC                | 600 (page/s)   | 
| DOCX               | 1482 (page/s)  | 


## 致谢

- [Antiword](https://github.com/rsdoiel/antiword)
- [LibreOffice](https://www.libreoffice.org/)
- [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/)
- [paddleocr](https://github.com/PaddlePaddle/PaddleOCR)


## 🖊️ 引用

```bibtex
@misc{2024magic-doc,
    title={Magic-Doc: A Toolkit that Converts Multiple File Types to Markdown},
    author={Magic-Doc Contributors},
    howpublished = {\url{https://github.com/InternLM/magic-doc}},
    year={2024}
}
```


## 开源许可证

该项目采用[Apache 2.0 开源许可证](LICENSE)。

<p align="right"><a href="#top">🔼 Back to top</a></p>
