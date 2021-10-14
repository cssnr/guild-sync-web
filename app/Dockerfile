FROM python:3.6-alpine
ENV TZ=America/Los_Angeles

RUN apk add --update --no-cache \
    alpine-sdk \
    build-base \
    linux-headers \
    mysql-dev \
    openldap-dev \
    pcre \
    pcre-dev \
    python3 \
    python3-dev \
    py3-pip

WORKDIR /app
COPY requirements.txt /app

RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

COPY . /app

ENTRYPOINT ["sh", "docker-entrypoint.sh"]
