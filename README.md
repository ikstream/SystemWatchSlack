# SystemWatchSlack
Python script with systemd units to watch for failed services

This script will use `systemd --failed` to retrieve failed services
and post them to the slack team and channel you specify

## Usage
To use SystemWatchSlack you first have to set your team and channel in `systemd-watcher.py` <br>

Afterward copy the systemd timer and service file to your systemd directory <br>
`# cp watch-systemd.* /etc/systemd/system/`

Now enable and start the timer<br>
`# systemctl enable watch-systemd.timer`<br>
`# systemctl start watch-systemd.timer`<br>

By default the timer will start the script every 10 minutes and 30 seconds after reboot. You can change this in watch-systemd.timer.<br>

Change start time after reboot to 20 seconds<br>
`OnBootSec=20sec`<br>

Change intervall to every week<br>
`OnUnitActiveSec=1w`
