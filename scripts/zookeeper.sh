#!/bin/bash
# Downloads and unpacks ZooKeeper on the machine.
cd /opt/
wget http://apache.org/dist/zookeeper/zookeeper-3.4.6/zookeeper-3.4.6.tar.gz
tar -zxf zookeeper-3.4.6.tar.gz
rm zookeeper-3.4.6.tar.gz
# Configures ZooKeeper.
mkdir /var/zookeeper
cd zookeeper-3.4.6
echo "tickTime=2000\ndataDir=/var/zookeeper\nclientPort=2181" > ./conf/zoo.cfg
# Starts ZooKeeper.
./bin/zkServer.sh start
