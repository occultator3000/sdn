#!/bin/bash

echo "Installing system dependencies for Ubuntu 20.04..."

# 更新系统包
sudo apt-get update
sudo apt-get upgrade -y

# 安装基础依赖
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    curl \
    wget \
    nodejs \
    npm

# 安装 Mininet
sudo apt-get install -y mininet

# 安装 OpenFlow
sudo apt-get install -y openvswitch-switch

# 安装 Python 依赖
pip3 install ryu
pip3 install requests
pip3 install websockets
pip3 install pytest
pip3 install -r requirements.txt

# 安装最新版 Node.js (可选，如果需要更新的版本)
curl -fsSL https://deb.nodesource.com/setup_14.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装前端开发工具
sudo npm install -g @vue/cli

# 创建必要的目录
mkdir -p logs
mkdir -p db

echo "Dependencies installation completed!" 