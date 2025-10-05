sudo tee /etc/systemd/system/time-report.service >/dev/null <<'UNIT'
[Unit]
Description=Time report JSON server
After=network-online.target
Wants=network-online.target

[Service]
User=chris
Group=chris
Environment=PYTHONUNBUFFERED=1
WorkingDirectory=/home/chris/time-report
ExecStart=/home/chris/time-report-env/bin/python /home/chris/time-report/app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable --now time-report.service
sudo systemctl status time-report.service

