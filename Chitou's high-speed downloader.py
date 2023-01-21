from __future__ import annotations
from tqdm import tqdm
import requests
import multitasking
import signal
signal.signal(signal.SIGINT, multitasking.killall)

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}
# 定义 1 MB 多少为 B
MB = 1024**2




def get_file_size(url: str, raise_error: bool = False) -> int:

    response = requests.head(url)
    file_size = response.headers.get('Content-Length')
    if file_size is None:
        if raise_error is True:
            raise ValueError('该文件不支持多线程分段下载！')
        return file_size
    return int(file_size)


def download(url: str, file_name: str, retry_times: int = 3, each_size=16*MB) -> None:

    f = open(file_name, 'wb')
    file_size = get_file_size(url)
    xiancheng = int(file_size/(1024*1024))
    if xiancheng > multitasking.config["CPU_CORES"] * 100:
        xiancheng = multitasking.config["CPU_CORES"] * 100
    if xiancheng == 0:
        xiancheng = 1
    xiancheng = int(input("线程数，推荐"+str(xiancheng)))
    if xiancheng == 0:
        xiancheng = 1

    @multitasking.task
    def start_download(start: int, end: int) -> None:
        _headers = headers.copy()
        _headers['Range'] = f'bytes={start}-{end}'
        response = session.get(url, headers=_headers, stream=True)
        chunk_size = 128
        chunks = []
        for chunk in response.iter_content(chunk_size=chunk_size):
            # 暂存获取的响应
            chunks.append(chunk)
            # 更新进度条
            bar.update(chunk_size)
        f.seek(start)
        for chunk in chunks:
            f.write(chunk)
        # 释放已写入的资源
        del chunks

    session = requests.Session()
    parts = []
    qishibyte = 0
    for i in range(xiancheng-1):
        parts.append((qishibyte,int((i+1)*(file_size/xiancheng))))
        qishibyte = int((i+1)*(file_size/xiancheng))
    parts.append((qishibyte,file_size))
    print("文件大小:"+str(file_size / 1024 / 1024) + "MB")
    print(f'分块数：{len(parts)}')
    #进度条
    bar = tqdm(total=file_size, desc=f'下载文件：{file_name}')
    for part in parts:
        start, end = part
        start_download(start, end)
    multitasking.wait_for_tasks()
    f.close()
    bar.close()


if "__main__" == __name__:
    multitasking.set_max_threads(multitasking.config["CPU_CORES"] * 100)
    print("本下载器不可下载exe等文件因为我不敢保证可以下到可以运行的exe")
    url = input("下载链接:")
    file_name = ""
    for i in range(len(url)):
        a = url[int(len(url) - i - 1)]
        if a == "/":
            break
        else:
            file_name = a+file_name
    print("文件名："+file_name)
    #下载文件
    download(url, file_name)
#https://maven.minecraftforge.net/net/minecraftforge/forge/1.12.2-14.23.5.2859/forge-1.12.2-14.23.5.2859-mdk.zip
#https://download.jetbrains.com/idea/ideaIC-2022.3.1.exe
#https://autopatchcn.yuanshen.com/client_app/download/launcher/20230106140848_fN1vtJLrG9TuUSXW/pcadsgsem/yuanshen_setup_20230104155435.exe