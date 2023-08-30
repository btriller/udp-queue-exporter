# udp-queue-exporter

Install dependencies on Debian:
```
apt-get install python3-prometheus-client python3-netaddr
```

Copy service file and start exporter
```
sudo cp udp-queue-exporter.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable --now udp-queue-exporter
```

Configure environment variables `LISTEN`, `LISTEN_PORTS` and `LISTEN_USERS` if you are only interested in specific sockets.
Adjust environment variables `SCRAPE_INTERVAL`, if you are scraping more often than once per 10s.
