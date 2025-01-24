# syntax=docker/dockerfile:1

# 定義一個可變參數 PYTHON_VERSION，默認值為 3.12.3
ARG PYTHON_VERSION=3.12.3 

# 使用指定版本的 Python slim 基礎映像
FROM python:${PYTHON_VERSION}-slim

# 添加一個標籤，標記運行時環境為 Flask
LABEL fly_launch_runtime="flask"

# 定義一個掛載點 /data
VOLUME /data

# 將本地 /database/future_telling.db 文件複製到容器的 /data/ 目錄
COPY /database/future_telling.db /data/

# 設置工作目錄為 /code
WORKDIR /code

# 將本地的 requirements.txt 文件複製到容器內
COPY requirements.txt requirements.txt

# 安裝 requirements.txt 中列出的 Python 依賴
RUN pip3 install -r requirements.txt

# 將當前目錄下的所有文件複製到容器內的當前工作目錄 (/code)
COPY . .

# 暴露容器的 8080 端口
EXPOSE 8080

# 設置容器啟動時執行的命令，運行 Flask 應用
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=8080"]
