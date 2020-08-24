# 轻量级接口测试框架
## 简介
    - 用于校验同一个接口不同host的json返回值是否一致
    - 使用pytest测试框架，yaml语法编写测试用例
## 用到技术
    - pytest
    - sqlalchemy 
## 使用方法
    - 在config.py中配置不同的host、数据库链接地址(默认使用sqllite数据库)
    - 在case/XXX.yaml 中参考示例格式编写用例
    - 在当前目录下执行命令```pytest```