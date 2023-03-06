FROM python:3.8.16-alpine3.17
WORKDIR /wechat-chatgpt
COPY ./ ./
RUN pip install --no-cache-dir pipenv &&\
    pipenv install &&\
    pipenv --clear
