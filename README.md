# wechat-chatgpt
> 基于flask和chatgpt的微信公众号聊天机器人后端

## docker 一键部署
```sh
# 安装docker-compose
sudo apt-get install docker-compose
# 修改docker-compose.yml 中的环境变量token（微信）和api_key（openai）
vim docker-compose.yml
# 部署
sudo docker-compose up -d
```

自主构建镜像
```sh
sudo docker build -t host/wechat-chatgpt --no-cache .
```

## 直接运行
```sh
# 安装pipenv
pip install pipenv
# 安装依赖
pipenv sync
# 若报错则执行
pipenv install
# 填写环境变量
export token=$token
export api_key=$api_key
# 运行
pipenv run flask run -h 0.0.0.0 -p 5030
```