#!/bin/bash
redis-server &
socket-redis --socket-ports=8090,8091,8092 &
python2 server.py &
python2 positiondaemon.py
