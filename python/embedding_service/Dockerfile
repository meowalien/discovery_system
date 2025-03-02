# 使用官方 Python 3.12.7 slim 版本作為基底映像
FROM python:3.12.7-slim

# 設定工作目錄
WORKDIR /app

ARG VERSION
RUN test -n "$VERSION" || (echo "ERROR: VERSION is not set!" && exit 1)

# 將 build arg 設定為環境變數，供容器內部使用
ENV VERSION=${VERSION}

# 複製需求檔案進入容器 (假設有 requirements.txt)
COPY requirements.txt .

# 安裝所需的 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製所有程式碼到容器中
COPY .. .

# 設定環境變數 (可選，用以提升容器效能與開發體驗)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 容器啟動時執行的指令，假設主程式為 app.py
CMD ["python", "app.py"]