#!/bin/bash
cp -t /etc/systemd/system/ ./*.service;
echo 'Services created';
systemctl daemon-reload;

for entry in `ls ./*.service`; do
  echo 'Starting' $entry;
  sudo systemctl start $entry
done