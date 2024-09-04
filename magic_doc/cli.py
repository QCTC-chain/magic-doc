import os
from datetime import datetime
import click
from pathlib import Path
from magic_doc.libs.version import __version__

from magic_doc.utils.config import get_s3_config
from magic_doc.utils.path_utils import get_local_dir, parse_s3path, prepare_env
from magic_doc.docconv import DocConverter, S3Config

from loguru import logger
from magic_doc.conv.pdf_magicpdf import SingletonModelWrapper

log_level = "ERROR"
log_dir = os.path.join(get_local_dir(), "magic-doc", "logs")
if not Path(log_dir).exists():
    Path(log_dir).mkdir(parents=True, exist_ok=True)
log_name = f'log_{datetime.now().strftime("%Y-%m-%d")}.log'
log_file_path = os.path.join(log_dir, log_name)
logger.add(str(log_file_path), rotation='00:00', encoding='utf-8', level=log_level, enqueue=True)


def abort(message=None, exit_code=1):
    click.echo(click.style(message, fg='red'))
    exit(exit_code)


total_cost_time = 0
total_convert_error = 0
total_file_broken = 0
total_unsupported_files = 0
total_time_out = 0
total_success_convert = 0

@click.group()
@click.version_option(__version__, "--version", "-v", help="显示版本信息")
def cli():
    pass

@cli.command()
# @click.version_option(__version__, "--version", "-v", help="显示版本信息")
@click.option('-f', '--file-path', 'input_file_path', type=click.STRING,
              help='file path, support s3/local/list, list file need end with ".list"')
@click.option('-p', '--progress-file-path', 'progress_file_path', default="/tmp/magic_doc_progress.txt", type=click.STRING,
              help='path to the progress file to save')
@click.option('-t', '--conv-timeout', 'conv_timeout', default=300, type=click.INT, help='timeout')
@click.option("-o", "--output", "output", default="", type=click.STRING)
@click.option("--models-dir", "models_dir", default="/tmp/models/", type=click.STRING, help="specify the models path")
def cli_conv(input_file_path, progress_file_path, conv_timeout, output, models_dir):
    global total_cost_time, total_convert_error, total_file_broken, \
        total_unsupported_files, total_time_out, total_success_convert

    def parse_doc(doc_path, pf_path=None):
        """使用全局变量统计耗时和error数量"""
        global total_cost_time, total_convert_error, total_file_broken, \
            total_unsupported_files, total_time_out, total_success_convert
        try:
            file_name = str(Path(doc_path).stem)
            '''创建同名进度缓存文件'''
            if not pf_path:
                pf_path = f"/tmp/{file_name}.txt"
            '''如果文档路径为s3链接，先获取s3配置并初始化'''
            if doc_path.startswith("s3://"):
                bucket, key = parse_s3path(doc_path)
                ak, sk, endpoint = get_s3_config(bucket)
                s3_config = S3Config(ak, sk, endpoint)
            else:
                '''非s3路径不需要初始化s3配置'''
                s3_config = None
            doc_conv = DocConverter(s3_config, models_dir=models_dir)
            markdown_string, cost_time = doc_conv.convert(doc_path, pf_path, conv_timeout)
            total_cost_time += cost_time
            logger.info(f"convert {doc_path} to markdown, cost {cost_time} seconds")
            # click.echo(markdown_string)
            base_name, doc_type = os.path.splitext(doc_path)
            out_put_dir = output or prepare_env(file_name, doc_type.lstrip(".").lower())
            with open(os.path.join(out_put_dir, file_name + ".md"), "w", encoding='utf-8') as md_file:
                md_file.write(markdown_string)
            total_success_convert += 1
            return cost_time
        except Exception as e:
            logger.exception(e)
            # 只统计转换出错的数量
            if "Convert failed" in str(e):
                total_convert_error += 1
            elif "Convert timeout" in str(e):
                total_time_out += 1
            elif "File is broken" in str(e):
                total_file_broken += 1
            elif "Unsupported file format" in str(e):
                total_unsupported_files += 1
            # abort(f'Error: {traceback.format_exc()}')

    if not input_file_path:
        logger.error(f"Error: Missing argument '--file-path'.")
        abort(f"Error: Missing argument '--file-path'.")
    else:
        '''适配多个文档的list文件输入'''
        if input_file_path.endswith(".list"):
            with open(input_file_path, "r") as f:
                for line in f.readlines():
                    line = line.strip()
                    parse_doc(line, progress_file_path)
        else:
            '''适配单个文档的输入'''
            parse_doc(input_file_path, progress_file_path)

    logger.info(f"total cost time: {int(total_cost_time)} seconds")
    logger.info(f"total convert error: {total_convert_error}")
    logger.info(f"total file broken: {total_file_broken}")
    logger.info(f"total unsupported files: {total_unsupported_files}")
    logger.info(f"total time out: {total_time_out}")
    logger.info(f"total success: {total_success_convert}")


parse_pdf_methods = click.Choice(["ocr", "digital", "auto"])
@cli.command()
@click.option("-m", "--method", "method", type=parse_pdf_methods,
    help="指定解析方法。digital: 文本型 pdf 解析方法， ocr: 光学识别解析 pdf, auto: 程序智能选择解析方法",
    default="auto")
@click.option('-f', '--file-path', 'doc_path', type=click.STRING,
              help='file path, support local or s3')
@click.option("-o", "--output", "output", default="", type=click.STRING)
@click.option("-d", "--debug", is_flag=True, default=False)
@click.option("--models-dir", "models_dir", default="/tmp/models/", type=click.STRING, help="specify the models path")
def pdf_cli(method, doc_path, output, debug, models_dir):

    os.environ["APPLY_FORMULA"] = "TRUE"

    if output_dir == "":
        if os.path.isdir(doc_path):
            output_dir = os.path.join(doc_path, "output")
        else:
            output_dir = os.path.join(os.path.dirname(output), "output")
    
    from magic_pdf.tools.common import do_parse
    from magic_pdf.libs.MakeContentConfig import MakeMode
    model = SingletonModelWrapper() 

    if doc_path.startswith("s3://"):
        bucket, key = parse_s3path(doc_path)
        ak, sk, endpoint = get_s3_config(bucket)
        s3_config = S3Config(ak, sk, endpoint)
    else:
        '''非s3路径不需要初始化s3配置'''
        s3_config = None
    doc_conv = DocConverter(s3_config, models_dir=models_dir)
    bits = doc_conv.get_raw_file_content(doc_path)

    file_name = str(Path(doc_path).stem)
    model_list = model(bits)

    if method == "digital":
        method = "txt"
    do_parse(
        output_dir,
        file_name, 
        bits, 
        model_list, 
        method, 
        f_draw_span_bbox=True,
        f_draw_layout_bbox=True,
        f_dump_md=True,
        f_dump_middle_json=True,
        f_dump_model_json=True,
        f_dump_orig_pdf=True,
        f_dump_content_list=False,
        f_make_md_mode=MakeMode.MM_MD,
        f_draw_model_bbox=False,
    )


if __name__ == '__main__':
    cli()
