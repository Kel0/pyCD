for entry in `ls ./*.service`; do
  sudo systemctl stop $entry;
  rm /etc/systemd/system/$entry;
  echo 'Deleted' $entry
done