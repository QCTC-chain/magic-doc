### 搭建 minio 服务

```
# 下载 minio 镜像
docker pull minio/minio

# 启动 minio 镜像
docker run \
  -p 9000:9000 \
  -p 9001:9001 \
  --name minio1 \
  -v ~/minio/docker/data:/data \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  minio/minio:latest server /data --console-address ":9001"
```

### 创建 Access key

1. 在浏览器输入 http://127.0.0.1:9001/

2. 使用 minioadmin/minioadmin 登陆

3. 创建 access key，将 `Access key` 和 `Secret Key` 保存至 `magic_doc/restful_api/config/config.yaml`配置文件中

4. 创建名称为 `magic-doc` 的 bucket

5.  `magic_doc/restful_api/config/config.yaml`  配置如下所示：

   ```yaml
    基本配置
   BaseConfig: &base
     DEBUG: true
     LOG_LEVEL: "DEBUG"
     SQLALCHEMY_TRACK_MODIFICATIONS: true
     SQLALCHEMY_DATABASE_URI: ""
     SECRET_KEY: "#$%^&**$##*(*^%%$**((&"
     JWT_SECRET_KEY: "#$%^&**$##*(*^%%$**((&"
     JWT_ACCESS_TOKEN_EXPIRES: 300
     AccessKeyID: "6b6C5NCmgq4F0kqoYVvA"
     AccessKeySecret: "C0QJJ2QH5FkzowndWDn5Vu2mxQ3Qi7mfrI2BwMLm"
     Endpoint: "127.0.0.1:9000"
     BucketName: "magic-doc"
     UrlExpires: 60
   
     S3AK: ""
     S3SK: ""
     S3ENDPOINT: ""
   
   
   # 开发配置
   DevelopmentConfig:
     <<: *base
   
   # 生产配置
   ProductionConfig:
     <<: *base
   
   # 测试配置
   TestingConfig:
     <<: *base
   
   # 当前使用配置
   CurrentConfig: "DevelopmentConfig"
   ```

   ### Minio Python SDK
   
   https://min.io/docs/minio/linux/developers/python/API.html



