#!/bin/bash
# Installs zookeeper on the machine.
cd /opt/
wget http://apache.org/dist/zookeeper/zookeeper-3.4.6/zookeeper-3.4.6.tar.gz
tar -zxf zookeeper-3.4.6.tar.gz
rm zookeeper-3.4.6.tar.gz
# Configures Zookeeper.
cd zookeeper-3.4.6
cp ./conf/zoo_sample.cfg ./conf/zoo.cfg
