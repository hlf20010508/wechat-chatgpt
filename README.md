# wechat-chatgpt
> 基于flask和chatgpt的微信公众号聊天机器人后端

## 注意
本代码默认使用微信的自动回复api（大部分人的账号没法通过微信验证）。

若已通过微信验证，强烈推荐使用微信的人工回复api，使用异步应答，可以避免`chatgpt`5秒内答不出来而产生的错误。

需要在`app.py`中的`main()`中更改代码，已在代码中作出标记。

## docker 一键部署
```sh
# 安装docker-compose
sudo apt-get install docker-compose
# 修改docker-compose.yml 中的环境变量
# 微信：token
# openai：api_key
# 可选参数：model（模型版本），preset（一段对人设的描述），memory_length（记忆长度）
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
# 填写环境变量
export token=$token
export api_key=$api_key
# 可选
export model=$model
export preset=$preset
export memory_length=$memory_length
# 运行
pipenv run flask run -h 0.0.0.0 -p 5030
```