#!/bin/bash

sudo rm /tmp/redis.sock
sudo service apache2 restart
sudo redis-server /var/run/redis/redis.conf 
sudo chmod 700 /tmp/redis.sock
sudo chown lie:lie /tmp/redis.sock
