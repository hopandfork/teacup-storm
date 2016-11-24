#!/bin/bash
# Downloads and unpacks ZooKeeper on the machine.
cd /opt/
wget http://apache.org/dist/zookeeper/zookeeper-3.4.6/zookeeper-3.4.6.tar.gz
tar -zxf zookeeper-3.4.6.tar.gz
rm zookeeper-3.4.6.tar.gz
# Configures ZooKeeper.
mkdir /var/zookeeper
cd zookeeper-3.4.6
echo "tickTime=2000" >  ./conf/zoo.cfg
echo "dataDir=/var/zookeeper" >> ./conf/zoo.cfg
echo "clientPort=2181" >> ./conf/zoo.cfg
# This script installs the supervisor supervisord, found at www.supervisord.org
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
echo "command=/opt/zookeeper-3.4.6/bin/zkServer.sh start-foreground" >> /etc/supervisord.conf
echo "autorestart=true" >> /etc/supervisord.conf
echo "stopsignal=KILL" >> /etc/supervisord.conf
# Starts ZooKeeper in supervisor mode.
/usr/local/bin/supervisord -c /etc/supervisord.conf
# Adds daily cleanup job
echo "/opt/zookeeper-3.4.6/bin/zkCleanup.sh /var/zookeeper -n 4" > /etc/cron.daily/zookeeper
