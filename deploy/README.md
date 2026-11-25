# 本地 Docker 部署

本目录启动 PostgreSQL、etcd、对象存储、Milvus 和 Attu，不包含前端和 Agent 服务。

## 镜像拉取失败

教程的 `minio/minio:RELEASE.2024-04-18T19-09-19Z` 已无法从 Docker Hub 匿名拉取。
截至 2026-11-18，`quay.io/minio/minio` 也无法匿名拉取，单纯改仓库地址或换成 `latest` 不能解决。

`pull access denied` 中的 `may require 'docker login'` 是通用提示，并不意味着注册 Docker Hub 账号就能获得该仓库的访问权限。
其他镜像显示 `Interrupted` 或随后出现 `No such image`，需要先修复这次拉取失败，再分别判断。


### 方案二：使用 Silo 兼容分支

`docker-compose.silo.yml` 是可选覆盖配置，使用固定版本的 `pgsty/silo`。
Silo 是 Pigsty 维护的独立 MinIO 社区分支，并非 MinIO 官方镜像。它保留 S3 接口、`MINIO_*` 环境变量和 `/minio/*` 路径。

覆盖配置替换对象存储镜像、启动命令和健康检查；服务名仍为 `minio`，Milvus 的 `MINIO_ADDRESS=minio:9000` 等连接参数保持一致。

在当前目录执行：

```bash
docker compose -f docker-compose.yml -f docker-compose.silo.yml config --quiet
docker compose -f docker-compose.yml -f docker-compose.silo.yml pull
docker compose -f docker-compose.yml -f docker-compose.silo.yml up -d
docker compose -f docker-compose.yml -f docker-compose.silo.yml ps

docker compose stop
docker compose start
```

后续管理这套配置时也带上两个 `-f` 参数，避免回到原 MinIO 镜像。
如果已有重要数据，先备份并验证兼容性再切换对象存储；重试拉取不需要删除数据卷。

如启动后仍失败，查看日志：

```bash
docker compose -f docker-compose.yml -f docker-compose.silo.yml logs --tail=100 minio milvus
```

镜像仓库返回拒绝访问，与 `timeout`、`EOF`、DNS 或代理错误是不同问题。后几种错误应检查 Docker 守护进程的网络、代理和证书配置。

## WSL2 网络和端口

本机学习通常不需要关闭 Windows 防火墙，也不需要像远程虚拟机那样先开放全部服务端口。
Compose 的 `ports` 已将以下容器端口发布到宿主环境，Windows 端通常可通过 `localhost` 访问：

| 服务 | 默认本机地址 | 用途 |
| --- | --- | --- |
| PostgreSQL | `localhost:5432` | 数据库客户端、后端连接 |
| MinIO / Silo | `http://localhost:9000` | S3 接口 |
| 对象存储控制台 | `http://localhost:9001` | 浏览器管理界面 |
| Milvus | `localhost:19530` | SDK 连接 |
| Milvus 健康检查 | `http://localhost:9091/healthz` | 健康状态 |
| Attu | `http://localhost:3000` | 浏览器管理界面 |

端口可被 Compose 环境变量覆盖，以 `docker compose ps` 的实际映射为准。
etcd 的 `2379` 仅供 Compose 网络内的 Milvus 使用，当前配置没有将它发布到宿主机。

只有让局域网其他设备访问时，才需要按实际入口放行 Windows 入站规则，并根据 WSL 的 NAT / mirrored 模式处理转发或 Hyper-V 防火墙规则。
镜像拉取是访问外部仓库的出站请求，开放上表中的入站端口不能解决仓库拒绝访问。

## 参考

- [Microsoft：WSL 网络访问](https://learn.microsoft.com/en-us/windows/wsl/networking)
- [Apache Flink：MinIO 的 Quay 镜像停止匿名拉取](https://issues.apache.org/jira/browse/FLINK-40802)
- [Silo 项目及兼容性说明](https://github.com/pgsty/silo)
- [Silo 固定版本的容器部署说明](https://silo.pigsty.io/download/)
