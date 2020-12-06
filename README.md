# pyCD
Deliver the updates to `master/dev` branch via `git`.

### Installation
```shell
git clone https://github.com/Kel0/pyCD.git
cd pyCD
pyenv virtualenv 3.7.0 venv  # Creating virtualenv
pyenv local venv  # Activating venv
pip install invoke && inv install  # Install dependencies
```

### Setup
- Setup pycd.service file
```unit file (systemd)
[Unit]
Description=pyCD 'delivering service'
After=syslog.target
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/pyCD  # Set path to pyCD dir.
Environment="PATH=/path/.pyenv/versions/3.7.0/envs/pyCD/bin:$PATH"  # Set path to your venv
ExecStart=/path/.pyenv/versions/3.7.0/envs/pyCD/bin/python /path/pyCD/run.py  # Set the start command
RestartSec=1
Restart=always

[Install]
WantedBy=multi-user.target
```
- Setup the pycd.ini file
```ini
[git]
url=git url

[branches]
dev=dev
master=master

[directories]
dev=where dev branch will be located
master=where master branch will be located
```
- Setup start.sh
```shell
#!/bin/bash
cp -t /etc/systemd/system/ ./*.service;  # where the systemd services located?
echo 'Services created';
systemctl daemon-reload;

for entry in `ls ./*.service`; do
  echo 'Starting' $entry;
  sudo systemctl start $entry
done
```
Setup in the same way stop.sh

### Launch
- Start app
```shell
sudo sh start.sh
```
- Stop app
```shell
sudo sh stop.sh
```


### Logs and service status
- Get status
```shell
systemctl status pycd.service
```
- App logs
```shell
journalctl -u pycd.service
```