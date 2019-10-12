#!/usr/bin/python
# Version 2.0
# Script designed to get Cox Communications internet
# usage data into a JSON format for Home Assistant.
#
# 10/17/2017: Output to file
# 11/02/2017: Updated to use mechanicalsoup
# 10/11/2019: Downgraded to use mechanicalsoup 6.0 for better intergration with https://hub.docker.com/r/homeassistant/home-assistant/

import re
import os
import json
import argparse
import mechanicalsoup

login_url = "https://www.cox.com/resaccount/sign-in.cox"
stats_url = "https://www.cox.com/internet/mydatausage.cox"

parser = argparse.ArgumentParser()
parser.add_argument('--username', help='Cox username')
parser.add_argument('--password', help='Cox password')
args = parser.parse_args()

json_file = "/config/scripts/cox_usage.json"

browser = mechanicalsoup.Browser()

""" Save this for when we can use a newer version of mechanicalsoup
# Setup browser
browser = mechanicalsoup.StatefulBrowser(
    soup_config={'features': 'lxml'},
    user_agent='Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13',
)
"""
 
#Disable SSL verification workaround for issue #2
browser.session.verify = False

# Open the login URL
login_page = browser.get(login_url)

# Similar to assert login_page.ok but with full status code in case of failure.
login_page.raise_for_status()

# Find the form named sign-in
login_form = mechanicalsoup.Form(
    login_page.soup.select_one('form[name="sign-in"]'))

# Specify username and password
login_form.input({'username':  args.username, 'password': args.password})

# Submit the form
browser.submit(login_form, login_page.url)

# Read the stats URL
stats_page = browser.get(stats_url)

# Grab the script with the stats in it
stats = stats_page.soup.findAll(
    'script', string=re.compile('utag_data'))[0].string

# Split and RSplit on the first { and on the last } which is where the data object is located
jsonValue = '{%s}' % (stats.split('{', 1)[1].rsplit('}', 1)[0],)

# Load into json
data = json.loads(jsonValue)

# Print JSON to file
with open(json_file, 'w+') as outfile:
    json.dump(data, outfile, sort_keys=True)
