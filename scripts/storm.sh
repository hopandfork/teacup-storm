#!/bin/bash
STORM_VER=1.0.2
# Cleanup
rm -rf /mnt/storm/*
rm -f /tmp/supervisor.sock
rm -f /tmp/supervisord.log
rm -f /tmp/supervisord.pid
if [ ! -e /opt/apache-storm-$STORM_VER ]; then
    # Downloads and unpacks Apache Storm on the machine.
    cd /opt/
    wget http://www-eu.apache.org/dist/storm/apache-storm-$STORM_VER/apache-storm-$STORM_VER.tar.gz
    tar -zxf apache-storm-$STORM_VER.tar.gz
    rm apache-storm-$STORM_VER.tar.gz
    mkdir /mnt/storm
fi
# Configures Storm.
cd /opt/apache-storm-$STORM_VER/conf
echo "storm.zookeeper.servers:" > ./storm.yaml
_ZOOKEEPER_SERVERS_
echo 'storm.local.dir: "/mnt/storm"' >> ./storm.yaml
echo 'nimbus.seeds: [_NIMBUS_SEEDS_]' >> ./storm.yaml
_SUPERVISOR_PORTS_

if [ ! -e /usr/local/bin/supervisord ]; then
    # This script installs the supervisor supervisord.
    easy_install supervisor
    # supervisord configuration
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
    echo "command=/opt/apache-storm-$STORM_VER/bin/storm _STORM_SERVICE_" >> /etc/supervisord.conf
    echo "autorestart=true" >> /etc/supervisord.conf
    echo "stopsignal=KILL" >> /etc/supervisord.conf
    echo "[program:logviewer]" >> /etc/supervisord.conf
    echo "command=/opt/apache-storm-$STORM_VER/bin/storm logviewer" >> /etc/supervisord.conf
    echo "autorestart=true" >> /etc/supervisord.conf
    echo "stopsignal=KILL" >> /etc/supervisord.conf
fi

# Starts Storm in supervisor mode.
/usr/local/bin/supervisord -c /etc/supervisord.conf
