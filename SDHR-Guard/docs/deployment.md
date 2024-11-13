# SDN DHR Security System 部署指南

## 1. 系统要求

### 1.1 硬件要求
- CPU: 双核及以上
- 内存: 8GB及以上
- 存储: 20GB可用空间

### 1.2 软件要求
- Ubuntu 20.04 LTS
- Python 3.8+
- Node.js 14+
- Mininet 2.3.0+
- SDN控制器:
  - RYU
  - POX
  - OpenDaylight

## 2. 环境配置

### 2.1 基础环境安装

#### 更新系统

~~~bash
sudo apt update

sudo apt upgrade -y
~~~

#### 安装基础依赖（课堂有下载的请忽略，主要是opendaylight的安装）

~~~bash
sudo apt install -y python3 python3-pip python3-dev

sudo apt install -y nodejs npm

sudo apt install -y git curl wget
~~~

### 2.2 安装Mininet

~~~bash
sudo apt install -y mininet
~~~

#### 安装RYU

~~~bash
pip3 install ryu
~~~

#### 安装POX

~~~bash
git clone https://github.com/noxrepo/pox.git

cd pox

git checkout eel
~~~

### 2.3 安装SDN控制器

#### 2.3.1 安装 Java 环境

~~~bash
# 安装 Java 8

sudo apt update

sudo apt install -y openjdk-8-jdk

# 验证 Java 安装

java -version

javac -version
~~~

#### 2.3.2 安装 OpenDaylight

~~~bash
# 创建安装目录
mkdir -p ~/odl
cd ~/odl

# 下载 OpenDaylight
wget https://nexus.opendaylight.org/content/repositories/opendaylight.release/org/opendaylight/integration/karaf/0.8.4/karaf-0.8.4.zip

# 解压
unzip karaf-0.8.4.zip

# 设置环境变量
echo "export ODL_HOME=~/odl/karaf-0.8.4" >> ~/.bashrc
echo "export PATH=\$PATH:\$ODL_HOME/bin" >> ~/.bashrc
source ~/.bashrc

# 启动 OpenDaylight
cd $ODL_HOME/bin
./karaf

# 在OpenDaylight 控制台安装必要的特性
feature:install odl-restconf odl-l2switch-switch odl-mdsal-apidocs odl-dlux-core
~~~



## 3. 项目部署

### 3.1 获取代码

~~~bash
git clone [项目仓库地址]

cd sdn-dhr-security
~~~

### 3.2 后端部署

~~~bash
cd backend
~~~

#### 创建虚拟环境

~~~bash
python3 -m venv venv

source venv/bin/activate
~~~

#### 安装依赖

~~~bash
pip install -r requirements.txt
~~~

#### 初始化配置

~~~bash
python init_config.py
~~~

#### 启动后端服务

~~~bash
python main.py
~~~

### 3.3 前端部署

~~~bash
cd frontend
~~~

#### 安装依赖

~~~bash
npm install
~~~

#### 开发环境运行

~~~bash
npm run serve
~~~

#### 生产环境构建

~~~bash
npm run build
~~~

## 4. 系统配置

### 4.1 控制器配置
编辑 `backend/config/settings.py`:

（已实现）

~~~python
CONTROLLERS = {
'ryu': {
'host': 'localhost',
'port': 6633
},
'pox': {
'host': 'localhost',
'port': 6634
},
'odl': {
'host': 'localhost',
'port': 6653
}
}
~~~

### 4.2 DHR配置
编辑 `backend/config/dhr_config.py`:

（已完成）

~~~python
DHR_CONFIG = {
'min_controllers': 2,
'max_controllers': 5,
'schedule_interval': 5,
'sync_interval': 30
}
~~~

## 5. 验证部署

### 5.1 系统检查

~~~bash
# 检查后端服务

curl http://localhost:5000/api/health

# 检查前端服务

curl http://localhost:8080
~~~

### 5.2 运行测试

~~~bash
# 运行集成测试

cd backend

pytest tests/integration/

# 运行白盒测试

pytest tests/whitebox/
~~~

## 6. 常见问题

### 6.1 控制器连接问题
- 检查控制器端口是否被占用
- 确保防火墙配置正确
- 验证控制器服务状态

### 6.2 性能优化
- 调整系统参数
- 配置日志级别
- 优化数据库查询

## 7. 维护指南

### 7.1 日志管理
- 日志位置: `backend/logs/`
- 日志轮转配置
- 错误追踪

### 7.2 备份策略
- 配置备份
- 数据备份
- 恢复流程

## 8. 安全建议

### 8.1 系统安全
- 定期更新系统
- 配置防火墙
- 监控系统状态

### 8.2 访问控制
- 配置认证
- 设置权限
- 审计日志
EOF

