#!/bin/bash

# Copyright 2016, 2017 Hop and Fork.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ZK_VER=3.4.6
# Cleanup
rm -rf /var/zookeeper/*
rm -f /tmp/supervisord.log
rm -f /tmp/supervisor.sock
rm -f /tmp/supervisord.pid
if [ ! -e /opt/zookeeper-$ZK_VER ]; then
    # Downloads and unpacks ZooKeeper on the machine.
    cd /opt/
    wget http://apache.org/dist/zookeeper/zookeeper-$ZK_VER/zookeeper-$ZK_VER.tar.gz
    tar -zxf zookeeper-$ZK_VER.tar.gz
    rm zookeeper-$ZK_VER.tar.gz
    # Configures ZooKeeper.
    mkdir /var/zookeeper
    cd zookeeper-$ZK_VER
    echo "tickTime=2000" >  ./conf/zoo.cfg
    echo "dataDir=/var/zookeeper" >> ./conf/zoo.cfg
    echo "clientPort=2181" >> ./conf/zoo.cfg
     # Adds daily cleanup job
    echo "/opt/zookeeper-$ZK_VER/bin/zkCleanup.sh /var/zookeeper -n 4" > /etc/cron.daily/zookeeper
fi
if [ ! -e /usr/local/bin/supervisord ]; then
    # This script installs the supervisor supervisord
    easy_install supervisor
    echo "[unix_http_server]" > /etc/supervisord.conf
    echo "file=/tmp/supervisor.sock" >> /etc/supervisord.conf
    echo "[supervisord]" >> /etc/supervisord.conf
    echo "logfile=/tmp/supervisord.log" >> /etc/supervisord.conf
    echo "logfile_maxbytes=50MB" >> /etc/supervisord.conf
    echo "logfile_backups=10" >> /etc/supervisord.conf
    echo "loglevel=info" >> /etc/supervisord.conf
    echo "pidfile=/tmp/supervisord.pid" >> /etc/supervisord.conf
    echo "nodaemon=false" >> /etc/supervisord.conf
    echo "minfds=1024" >> /etc/supervisord.conf
    echo "minprocs=200" >> /etc/supervisord.conf
    echo "[rpcinterface:supervisor]" >> /etc/supervisord.conf
    echo "supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface" >> /etc/supervisord.conf
    echo "[supervisorctl]" >> /etc/supervisord.conf
    echo "serverurl=unix:///tmp/supervisor.sock" >> /etc/supervisord.conf
    echo "[program:zookeeper]" >> /etc/supervisord.conf
    echo "command=/opt/zookeeper-$ZK_VER/bin/zkServer.sh start-foreground" >> /etc/supervisord.conf
    echo "autorestart=true" >> /etc/supervisord.conf
    echo "stopsignal=KILL" >> /etc/supervisord.conf
fi
# Starts ZooKeeper in supervisor mode.
/usr/local/bin/supervisord -c /etc/supervisord.conf

