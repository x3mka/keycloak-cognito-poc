FROM python:3.11

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    pkg-config \
    libtool \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Обязательно установить lxml из исходников, чтобы использовать системный libxml2
RUN pip install --no-binary=lxml lxml
RUN pip install --no-cache-dir setuptools wheel setuptools_scm

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]