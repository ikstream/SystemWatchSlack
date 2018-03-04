#!/usr/bin/env python
"""watch for failed systemd services and notify user through slack"""
################################################################################
#
# MIT License
#
# Copyright (c) 2017 Stefan Venz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
################################################################################

import json
import os.path
import re
import socket
import subprocess as subp
from time import strftime
import requests

FAILED_LOG = '/tmp/failed_services.log'
LOGFILE = '/var/log/failed_services.log'

class Team:
    """contains slack channel  and user data"""
    username = "SystemWatchSlack"
    webhook = "https://hooks.slack.com/services/your/webhook/here/"
    emoji = ":no_entry:"
    channel = "#general"

def set_parameters(service):
    """create message to send to slack"""
    hostname = socket.gethostname()
    msg = "{} failed on {}".format(service, hostname)
    send_message(msg)


def send_message(msg):
    """send the actual message"""
    msg_data = {"channel": Team.channel, "username": Team.username, "text": msg,
                "icon_emoji": Team.emoji}
    alert = requests.post(Team.webhook, data=json.dumps(msg_data))


def parse_systemd():
    """ get any failed services from systemd --failed"""
    failed_services = []
    sysd = subp.Popen(["systemctl --failed"], stdout=subp.PIPE, shell=True)
    (out, err) = sysd.communicate()
    now = strftime("%c")
    found_service = False

    text = (out.decode("utf-8")).split('\n')

    if not os.path.exists(FAILED_LOG):
        open(FAILED_LOG, 'x').close

    for line in text:
        elements = re.findall(r"[\w'.]+", line)
        for word in elements:
            if word == "failed":
                failed_services.append(elements[0])
                break

    #remove everything from log, if no failed services are found
    if not failed_services:
        open(FAILED_LOG, 'w').close

    with open(FAILED_LOG, 'r+') as log:
        lines = log.readline()
        for service in failed_services:
            if service in lines:
                continue
            else:
                set_parameters(service)
                log.write("{}\n".format(service))

    if not os.path.exists(LOGFILE):
        open(LOGFILE, 'x').close

    for service in failed_services:
        with open(LOGFILE, 'a+') as fail_log:
            fail_log.write("{}: {}\n".format(now, service))

parse_systemd()
