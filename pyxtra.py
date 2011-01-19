#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import json
import re
import urllib
import mechanize
from BeautifulSoup import BeautifulSoup

# Add your data here
imageviewer = 'eog' # Preferred image viewer like eog, mirage, feh...
username = '' # Xtrazone username
password = '' # Xtrazone password

# Config variables
_debug = False # Set to True to show debug output

def main():
    # Check config
    if (username == '' or password == ''):
        print 'Error: Please set your username and password'
        return 1
        
    # Initialize mechanize instance
    b = mechanize.Browser()
    
    # Browser options
    b.set_handle_equiv(True)
    b.set_handle_redirect(True)
    b.set_handle_referer(True)
    b.set_handle_robots(False)

    # Follow refresh 0 but don't hang on refresh > 0
    b.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # User agent
    b.addheaders = [
            ('User-agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)'),
            ]

    # Debugging stuff
    if _debug:
        b.set_debug_http(True)
        b.set_debug_redirects(True)
        b.set_debug_responses(True)


    # Get CAPTCHA URL
    try:
        # This will start the session etc
        b.open('https://xtrazone.sso.bluewin.ch/index.html.de')

        b.addheaders = [
                ('X-Requested-With', 'XMLHttpRequest'),
                ('X-Header-XtraZone', 'XtraZone'),
                ('Referer', 'https://xtrazone.sso.bluewin.ch/index.html.de'),
                ]
        url = 'https://xtrazone.sso.bluewin.ch/index.php/20,53,ajax,,,283/?route=%2Flogin%2Fgetcaptcha'
        data = {'action': 'getCaptcha',
                'do_sso_login': 0,
                'passphrase': '',
                'sso_password': password,
                'sso_user': username,
                'token': '',
                }
        b.open(url, urllib.urlencode(data))

        resp = json.loads(b.response().read()) # Convert response to dictionary
        captcha_url = 'http:' + resp['content']['messages']['operation']['imgUrl']
        captcha_token = resp['content']['messages']['operation']['token']
    except Exception as e:
        print 'Error: Could not retrieve CAPTCHA: %s' % e
        return 1


    # Display CAPTCHA using image viewer of choice
    print 'Image viewer has been launched to display CAPTCHA.'
    os.system('%s %s > /dev/null 2>&1 &' % (imageviewer, captcha_url)) # TODO: very unsafe, fix
    captcha = raw_input('Please enter CAPTCHA: ')
    if captcha == '':
        print 'Error: CAPTCHA may not be empty.'
        return 1


    # Log in
    try:
        b.addheaders = [
                ('X-Requested-With', 'XMLHttpRequest'),
                ('X-Header-XtraZone', 'XtraZone'),
                ('Referer', 'https://xtrazone.sso.bluewin.ch/index.html.de'),
                ]
        url = 'https://xtrazone.sso.bluewin.ch/index.php/22,39,ajax_json,,,157/'
        data = {'action': 'ssoLogin',
                'do_sso_login': 1,
                'passphrase': captcha,
                'sso_password': password,
                'sso_user': username,
                'token': captcha_token,
                }
        b.open(url, urllib.urlencode(data))

        resp = json.loads(b.response().read()) # Convert response to dictionary
        if resp['status'] == 'login_failed':
            print 'Error: %s' % resp['message']
            return 1
    except Exception as e:
        print 'Error: Could not log in: %s' % e
        return 1


    # Retrieve user info
    try:
        b.open('https://xtrazone.sso.bluewin.ch/index.php/20,53,ajax,,,283/?route=%2Flogin%2Fuserboxinfo')
        resp = json.loads(b.response().read()) # Convert response to dictionary

        # Parse HTML
        html = resp['content']
        soup = BeautifulSoup(html)
        nickname = soup.find('div', {'class': 'userinfo'}) \
                .find('h5').contents[0].strip()
        fullname = soup.find('div', {'class': 'userinfo'}) \
                .find('a', {'href': '/index.php/20?route=%2Fprofile'}).contents[0].strip()
        remaining = int(re.search('&nbsp;([0-9]{1,3})&nbsp;',
                soup.find('div', {'class': 'userinfo'}).find('span').contents[0]).group(1))

        print 'Hi %s (%s), you have %u SMS/MMS left' % (fullname, nickname, remaining)

    except Exception as e:
        print 'Error: Could not retrieve number of remaining SMS: %s' % e
        return 1


if __name__ == '__main__':
    sys.exit(main())
