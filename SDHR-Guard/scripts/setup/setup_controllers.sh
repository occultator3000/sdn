#!/bin/bash

echo "Setting up SDN controllers..."

# 安装POX控制器
git clone https://github.com/noxrepo/pox.git
cd pox
git checkout eel

# 安装RYU控制器
pip install ryu

# 下载OpenDaylight
wget https://nexus.opendaylight.org/content/repositories/opendaylight.release/org/opendaylight/integration/karaf/0.8.4/karaf-0.8.4.zip
unzip karaf-0.8.4.zip

echo "Controllers setup completed!" 