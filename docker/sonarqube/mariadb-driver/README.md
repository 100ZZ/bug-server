# MariaDB JDBC Driver for SonarQube

SonarQube 10.7.0 不支持 MySQL，需要使用 MariaDB JDBC 驱动连接 MySQL 数据库。

## 安装步骤

1. 下载 MariaDB JDBC 驱动：
   ```bash
   cd /Users/lihui/Work/cursor/dm-brains/bug-server/docker/sonarqube/mariadb-driver
   wget https://repo1.maven.org/maven2/org/mariadb/jdbc/mariadb-java-client/3.3.3/mariadb-java-client-3.3.3.jar
   ```

   或者使用其他版本（推荐 3.3.x 或更高版本）：
   ```bash
   # 查看可用版本：https://mvnrepository.com/artifact/org.mariadb.jdbc/mariadb-java-client
   wget https://repo1.maven.org/maven2/org/mariadb/jdbc/mariadb-java-client/3.3.3/mariadb-java-client-3.3.3.jar
   ```

2. 验证文件：
   ```bash
   ls -lh mariadb-java-client-*.jar
   ```

3. 重启 SonarQube 容器：
   ```bash
   cd /Users/lihui/Work/cursor/dm-brains/bug-server/docker
   docker-compose restart sonarqube
   ```

## 注意事项

- JDBC 驱动 JAR 文件必须放在此目录中
- 文件名可以是 `mariadb-java-client-*.jar`，SonarQube 会自动加载
- 如果驱动文件不存在，容器启动时会报错 "Unsupported JDBC driver provider: mariadb"
