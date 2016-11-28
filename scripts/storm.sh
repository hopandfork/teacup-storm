#!/bin/bash
# Downloads and unpacks Apache Storm on the machine.
cd /opt/
wget https://github.com/apache/storm/archive/v0.10.2.tar.gz
tar -zxf storm-0.10.2.tar.gz
rm storm-0.10.2.tar.gz
# Configures Storm.
mkdir /mnt/storm
cd storm-0.10.2/conf
echo "storm.zookeeper.servers:" > ./storm.yaml
echo '  - "111.222.333.444"' >> ./storm.yaml
echo 'storm.local.dir: "/mnt/storm"' >> ./storm.yaml
echo 'nimbus.seeds: ["111.222.333.44"]' >> ./storm.yaml
echo "supervisor.slots.ports:" >> ./storm.yaml
echo "- 6700" >> ./storm.yaml
echo "- 6701" >> ./storm.yaml
echo "- 6702" >> ./storm.yaml
echo "- 6703" >> ./storm.yaml

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
echo "[program:storm]" >> /etc/supervisord.conf
#echo "command=/opt/zookeeper-3.4.6/bin/zkServer.sh start-foreground" >> /etc/supervisord.conf
echo "autorestart=true" >> /etc/supervisord.conf
echo "stopsignal=KILL" >> /etc/supervisord.conf
# Starts Storm in supervisor mode.
/usr/local/bin/supervisord -c /etc/supervisord.conf
# Adds daily cleanup job
# echo "/opt/zookeeper-3.4.6/bin/zkCleanup.sh /var/zookeeper -n 4" > /etc/cron.daily/zookeeper