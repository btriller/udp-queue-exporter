#!/usr/bin/env python3

import time
from time import sleep, monotonic as timer
from datetime import datetime, timezone, timedelta
import pwd
import os
import sys
from prometheus_client import start_http_server, Summary, Gauge, Counter
import netaddr
import socket
from os import environ

PROCESS_UDP_TIME = Summary("process_udp_seconds", "Time spent processing udp")
ports = [int(p) for p in environ.get("LISTEN_PORTS", "").split(',') if environ.get("LISTEN_PORTS", "")]
users = [str(pwd.getpwnam(u).pw_uid) for u in environ.get("LISTEN_USERS", "").split(',') if environ.get("LISTEN_USERS", "")]

@PROCESS_UDP_TIME.time()
def process_udp():
    with open('/proc/net/udp', encoding="utf-8") as f:
        next(f)
        for line in f:
            fields = line.split()
            if fields[3] != '07':
                continue
            local_ip_hex, local_port_hex = fields[1].split(':')
            local_port = int(local_port_hex, 16)
            if ports and local_port not in ports:
                continue
            uid = fields[7]
            if users and uid not in users:
                continue
            local_address = f"{netaddr.IPAddress(socket.ntohl(int(local_ip_hex, 16)))}:{local_port}"
            q = fields[4].split(':')
            tx = int(q[0], 16)
            rx = int(q[1], 16)
            drops = int(fields[-1])
            labels = {'local_address': local_address, 'uid': uid}
            rx_.labels(**labels).set(rx)
            tx_.labels(**labels).set(tx)
            labelvalues = tuple(str(l) for l in labels.values())
            if labelvalues in drops_._metrics:
                drops_._metrics[labelvalues]._value.set(drops)
            else:
                drops_.labels(**labels).inc(drops)

start_http_server(port=int(environ.get('LISTEN', 8000)), addr="localhost")

interval = int(environ.get('SCRAPE_INTERVAL', 10))
deadline = timer()
label_names = ["local_address", "uid"]
rx_ = Gauge('udp_rx_queue', 'rx', labelnames=label_names)
tx_ = Gauge('udp_tx_queue', 'tx', labelnames=label_names)
drops_ = Counter('udp_drops', 'drops', labelnames=label_names)

# Generate some requests.
while True:
    deadline += interval
    process_udp()
    print(f"{datetime.now()} parsed /proc/net/udp")
    sys.stdout.flush()
    delay = deadline - timer()
    if delay > 0:
        sleep(delay)
