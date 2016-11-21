#!/bin/bash
# This script installs the supervisor supervisord, found at www.supervisord.org
easy_install supervisor
echo_supervisord_conf > /etc/supervisord.conf
echo "[program:zookeeper]\ncommand=zkServer.sh start-foreground\nautorestart=true\nstopsignal=KILL\n" > /etc/supervisord.conf

