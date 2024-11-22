'''
Author: dbliu shaxunyeman@gmail.com
Date: 2024-11-22 17:45:38
LastEditors: shaxunyeman shaxunyeman@gmail.com
LastEditTime: 2024-11-22 20:15:59
FilePath: /magic-doc/magic_doc/restful_api/api/main.py
Description: 
'''

if __name__ == '__main__':
    import requests
    import json
    from pathlib import Path
    from io import BytesIO

    def __analysis_magic_doc(
            server_host: str,
            file_path: str):
        url = f'{server_host}/analysis/pdf'
        file_type = str(Path(file_path).suffix).strip('.')
        file_name = str(Path(file_path).stem)
        file_name = f'{file_name}.{file_type}'

        with open(file_path, 'rb') as f:
            files = {'doc_file': (file_name, f, f'application/{file_type}')}  # 文件名、文件内容、文件类型
            response = requests.post(
                url, 
                files=files, 
                data= {
                    'doc_name': file_name,
                    'doc_type': file_type
                    })
        f.close()
        return json.loads(response.text)

    def __download_analysis_result(server_host: str, object_name: str):
        url = f'{server_host}/download/pdf'
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "objectName": object_name
        }

        response = requests.post(url, headers=headers, json=data)
        bio = BytesIO(response.content)
        text = bio.read().decode('utf-8', errors='ignore')
        return text
    
    response = __analysis_magic_doc(
        'http://127.0.0.1:5556',
        '/Users/dbliu/Desktop/深圳出差1022/报销/住宿/结账单20241104_1.pdf')
    # response = __analysis_magic_doc(
    #     'http://127.0.0.1:5556',
    #     '/Users/dbliu/Desktop/储能日报每日上报/1月日报/莱芜孟家储能电站01月01日日报.docx'
    # )

    md_content = __download_analysis_result(
        'http://127.0.0.1:5556', 
        'pdf/结账单20241104_1/0.md')
    print(md_content)