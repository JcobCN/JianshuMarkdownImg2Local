import sys

import threadpool
import mistletoe
from bs4 import BeautifulSoup
import httpx
import os
import re

def download_pics(url, file, img_name):
    img_data = httpx.get(url).content
    filename = os.path.basename(file).split('.')[0]
    dirname = os.path.dirname(file)
    targer_dir = os.path.join(dirname, f'{filename}.assets')
    if not os.path.exists(targer_dir):
        os.mkdir(targer_dir)

    # img_name = f'{uuid.uuid4().hex}.png'
    with open(os.path.join(targer_dir, img_name), 'w+') as f:
        f.buffer.write(img_data)


def download_and_replace_image(filepath: str):
    url_suffix = 'https://upload-images.jianshu.io/upload_images/'
    print(f'正在处理文件：{filepath}')
    print(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        file_content = f.read()
        html = mistletoe.markdown(file_content)
        soup = BeautifulSoup(html, features='html.parser')
        for img in soup.find_all('img'):
            img_url: str = img.get('src')
            if not img_url.startswith('http://') and not img_url.startswith('https://'):
                print(f'不是有效的网络图片链接，跳过')
                return
            img_base_name = os.path.basename(img_url.replace(url_suffix, '').replace('?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240', ''))
            print(f'下载图片：{img_base_name}')
            img_name = img_base_name
            if '.' in img_base_name:
                # img_base_name = img_name[0:img_name.index('.')]
                img_name = img_base_name
            else:
                # 没有图片后缀的话就加上jpg
                img_name = img_base_name + '.png'
                # img_name += '.png'
            download_pics(img_url, filepath, img_name)

            img_relative_path = os.path.join(os.path.basename(filepath).replace('.md', '.assets'), img_name)
            print(f'替换图片链接：{img_url} with {img_relative_path}')

            file_content = re.sub(f"!\\[.*?\\]\\((.*?){img_base_name}(.*?)\\)", f'{{% assets {img_base_name} %}}', file_content)
            file_content = file_content.replace(f'{{% assets {img_base_name} %}}', f'![]({img_relative_path})')

        updated_file_content = file_content

    with open(filepath, 'w+', encoding='utf-8') as f:
        print(f'改动写入文件：{filepath}')
        f.write(updated_file_content)

def run(_path:str):
    print('正在处理。')

    # work_path = os.path.join('.', 'docs')
    work_path = _path

    pool = threadpool.ThreadPool(4)
    args = []

    for root, dirs, files in os.walk(work_path):
        for filename in files:
            if filename.endswith('md'):
                filepath = os.path.abspath(os.path.join(root, filename))
                args.append(filepath)
                # download_and_replace_image(filepath)

    tasks = threadpool.makeRequests(download_and_replace_image, args)
    [pool.putRequest(task) for task in tasks]

    print('=> 线程池开始运行')
    pool.wait()
    print('任务完成。')

if __name__ == '__main__':
    run(sys.argv[1])