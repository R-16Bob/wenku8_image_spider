import os
import sys

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 说明：关键在于每次请求都添加正确的头部信息，否则会返回403错误。
def create_session(imge_url,username,password):
    # 创建一个session对象
    session = requests.Session()

    # 登录页面的URL
    login_url = 'https://www.wenku8.net/login.php'

    # 模拟登录所需的表单数据
    login_data = {
        'username': username,  # 替换为您的用户名
        'password': password,  # 替换为您的密码
        'usecookie': '0'  # 替换为您希望保持登录状态的时间，这里是一年
    }

    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://www.wenku8.net/login.php'
    }

    # 提交登录请求
    response = session.post(login_url, data=login_data, headers=headers)

    # 检查是否登录成功
    if response.ok:
        print("登录成功！")
        # 登录成功，现在可以使用session对象发送请求，保持登录状态
        download_images(session,imge_url)

    else:
        print("登录失败")
        # 打印响应内容以获取错误信息
        print(response.content)

    # 关闭session
    session.close()

def get_header(url):
    # 设置额外的请求头
    page_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': url  # 设置Referer头，指向您要访问的页面
    }
    return page_headers
def download_images(session,page_url):

    # 发送请求获取页面内容
    page_response = session.get(page_url, headers=get_header(page_url))
    if page_response.status_code == 200:
        # 使用BeautifulSoup解析页面内容
        soup = BeautifulSoup(page_response.text, 'html.parser')

        # 查找所有<img>标签
        img_tags = soup.find_all('img')

        # 创建输出文件夹
        output_folder = 'downloaded_images'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # 下载并保存图片
        for i, img_tag in enumerate(img_tags):
            img_url = img_tag.get('src')
            if not img_url:
                continue

            # 将相对URL转换为绝对URL
            img_url = urljoin(page_url, img_url)

            # 获取图片内容
            img_response = session.get(img_url,headers=get_header(img_url))
            if img_response.status_code == 200:
                # 获取图片的扩展名
                img_extension = os.path.splitext(img_url)[1]
                if not img_extension:
                    img_extension = '.jpg'

                # 生成图片的保存路径
                img_save_path = os.path.join(output_folder, f'image_{i}{img_extension}')

                # 保存图片
                with open(img_save_path, 'wb') as f:
                    f.write(img_response.content)
                print(f"图片已下载：{img_save_path}")
            else:
                print(f"下载图片失败，状态码：{img_response.status_code}")
    else:
        print(f"获取页面内容失败，状态码：{page_response.status_code}")

if __name__ == '__main__':
    # 检查是否存在credentials.txt文件
    if not os.path.exists('credentials.txt'):
        # 文件不存在，要求用户输入用户名和密码
        username = input("请输入用户名：")
        password = input("请输入密码：")

        # 将用户名和密码写入到文件中
        with open('credentials.txt', 'w') as file:
            file.write(f"{username}\n{password}")
        print(f"用户信息已保存到本地文件：credentials.txt")
        create_session(sys.argv[1],username,password)
    else:
        # 文件存在，直接读取用户名和密码信息
        print("使用保存的用户信息进行登录")
        with open('credentials.txt', 'r') as file:
            lines = file.readlines()
            username = lines[0].strip()
            password = lines[1].strip()
            create_session(sys.argv[1],username,password)



