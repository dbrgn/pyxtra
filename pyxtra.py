#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A small commandline utility written in Python to access the Swisscom
Xtrazone SMS service

License:
Copyright (C) 2011 Danilo Bargen, Peter Manser

pyxtra is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

pyxtra is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
pyxtra. If not, see http://www.gnu.org/licenses/.
"""

import os
import sys
import urllib
import re
import getpass
import ConfigParser
import unicodedata

try:
    import readline
    import json
    import mechanize
    from BeautifulSoup import BeautifulSoup
    import xlrd
except ImportError as e:
    module = str(e)[16:]
    print 'Python module %s not found. Install it using pip or your ' \
          'system\'s package manager.' % module
    sys.exit(1)


# Some configuration variables
_debug = False  # Set to True to show debug output
separator = '--------------------'


class XtrazoneError(Exception):
    """Errors related with the Xtrazone page."""
    pass

class CaptchaError(XtrazoneError):
    """Errors related with the CAPTCHA."""
    pass


def remove_accents(ustr):
    """Removes accents from an unicode string.

    Strips all accents by removing the precomposed unicode characters. String
    to convert should be in unicode format."""
    nkfd_form = unicodedata.normalize('NFKD', unicode(ustr))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

def parse_config():
    """Parse the configuration file."""
    config_folder = os.path.expanduser(os.path.join('~', '.pyxtra'))  # Folder that will contain all configfiles
    config_file = os.path.join(config_folder, 'config')

    config = ConfigParser.ConfigParser()  # ConfigParser instance

    # Create folder if necessary
    if not os.path.isdir(config_folder):
        os.mkdir(config_folder)

    # Read config, write default config file if it doesn't exist yet.
    if not len(config.read(config_file)):
        print 'Could not find configuration file. Creating %s.' % config_file
        username = raw_input('\nXtrazone username: ').strip()
        print 'Enter your password, in case you want to store it in the ' \
              'config file. Warning: Password will be saved in plaintext.'
        password = getpass.getpass('Xtrazone password (ENTER to skip): ').strip()
        print '\nPlease choose your preferred image viewer. On Ubuntu, we ' \
              'suggest "eog", which is installed by default.'
        imageviewer = raw_input('Image viewer: ').strip()
        print 'Initial configuration is finished.\n'

        config.add_section('settings')
        config.set('settings', 'username', username)
        config.set('settings', 'password', password)
        config.set('settings', 'imageviewer', imageviewer)
        config.write(open(config_file, 'w'))
    else:
        username = config.get('settings', 'username')
        password = config.get('settings', 'password')
        imageviewer = config.get('settings', 'imageviewer')

    return username, password, imageviewer
   

def init():
    """Initialize and return mechanize instance."""
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
    return b


def login(browser, username, password, imageviewer):
    """Display the CAPTCHA and log in."""
    if password == '':
        password = raw_input('Xtrazone password: ').strip()

    # Get CAPTCHA URL
    browser.open('https://xtrazone.sso.bluewin.ch/index.html.de')
    browser.addheaders = [
            ('X-Requested-With', 'XMLHttpRequest'),
            ('X-Header-XtraZone', 'XtraZone'),
            ('Referer', 'https://xtrazone.sso.bluewin.ch/index.html.de'),
            ]
    url = 'https://xtrazone.sso.bluewin.ch/index.php/20,53,ajax,,,283/' \
           '?route=%2Flogin%2Fgetcaptcha'
    data = {'action': 'getCaptcha',
            'do_sso_login': 0,
            'passphrase': '',
            'sso_password': password,
            'sso_user': username,
            'token': '',
            }
    browser.open(url, urllib.urlencode(data))
    resp = json.loads(browser.response().read())  # Convert response to dict
    captcha_url = 'http:' + resp['content']['messages']['operation']['imgUrl']
    captcha_token = resp['content']['messages']['operation']['token']
    
    # Display CAPTCHA using image viewer of choice.
    print 'Image viewer has been launched to display CAPTCHA.'
    os.system('%s %s > /dev/null 2>&1 &' % (imageviewer, captcha_url))
    captcha = ''
    while captcha == '':
        captcha = raw_input('Please enter CAPTCHA: ').strip()
    
    # Log in
    browser.addheaders = [
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
    browser.open(url, urllib.urlencode(data))

    resp = json.loads(browser.response().read())
    if resp['status'] == 'captcha_failed':
        raise CaptchaError('CAPTCHA failed: %s' % resp['message'])
    if resp['status'] != 'login_ok':
        raise XtrazoneError('Login failed: %s' % resp['message'])


def get_user_info(browser):
    """Retrieve user info.
    
    Return nickname, full name and remaining SMS.
    """
    browser.open('https://xtrazone.sso.bluewin.ch/index.php/' \
                 '20,53,ajax,,,283/?route=%2Flogin%2Fuserboxinfo')
    resp = json.loads(browser.response().read())

    # Parse HTML
    html = resp['content']
    soup = BeautifulSoup(html)
    nickname = (soup.find('div', {'class': 'userinfo'})
                .find('h5').contents[0].strip())
    fullname = (soup.find('div', {'class': 'userinfo'})
                .find('a', {'href': '/index.php/20?route=%2Fprofile'})
                .contents[0].strip())
    remaining = (int(re.search('&nbsp;([0-9]{1,3})&nbsp;',
                 soup.find('div', {'class': 'userinfo'}).find('span')
                 .contents[0]).group(1)))

    return nickname, fullname, remaining


def pull_contacts(browser):
    """Retrieve contact list.

    Retrieves an .xls-export of all contacts, parses it and returns a list.
    """
    url = 'https://xtrazone.sso.bluewin.ch/index.php/20,53,ajax,,,98/?route=' \
          '%2Fprofile%2Fcontact%2Fexcelexport&suspAjax=1'
    browser.open(url)
    resp = browser.response().read()
    book = xlrd.open_workbook(file_contents=resp)
    sheet = book.sheet_by_index(0)
    contacts = [sheet.row_values(row) for row in range(1, sheet.nrows)]
    return sorted(contacts, key=lambda c: c[2])


def add_contact(browser, prename='', name='', nr=''):
    """Add a new contact to the XtraZone address book"""
    while prename == '': prename = raw_input('First name: ').strip()
    if name == '': name = raw_input('Name: ').strip()
    while nr == '': nr = raw_input('Nr: ').strip()
    
    url = 'https://xtrazone.sso.bluewin.ch/index.php/20,53,ajax,,,283/?route=' \
          '%2Fprofile%2Fcontact%2Faddcontact&refresh=/profile/contact/list'
    data = {'contactId': '',
            'name': name,
            'natelnr': nr,
            'prename': prename,
            'save': 'Speichern',
            }
    browser.open(url, urllib.urlencode(data))

    resp = json.loads(browser.response().read())
    resp['content']

    if resp['content']['isError'] == True:
        raise XtrazoneError(
                'Adding contact failed: %s' % resp['content']['headline'])
    print 'Successfully saved contact %s %s.' % (prename, name)
    

def print_contacts(contacts):
    """Print nicely formatted contact list."""
    def natel_nr(nr):
        nr = str(nr)[2:11]
        return '0%s %s %s %s' % (nr[0:2], nr[2:5], nr[5:7], nr[7:9])

    print separator
    for contact in contacts:
        print '%s: %s' % (contact[2].strip(), natel_nr(contact[1]))
    print separator


def send_sms(browser, contacts):
    """Send SMS.
    
    Query for cell phone number and message and send SMS.
    """

    # Configure and enable tab completion
    def completer(text, state):
        """Contacts completer function for readline module"""
        options = [x[2].strip() for x in contacts
                   if x[2].lower().startswith(text.strip().lower())]
        try:
            return options[state]
        except IndexError:
            return None
    readline.set_completer(completer)
    readline.set_completer_delims(',')
    readline.parse_and_bind('tab: complete')

    def replace_contacts(text):
        """Replace contacts with corresponding cell phone numbers."""
        numbers = text.split(',')
        for nr in numbers:
            f = filter(lambda c: c[2].strip().lower() == nr.strip().lower(),
                       contacts)
            try:
                text = text.replace(nr, '0' + str(f[0][1])[2:11])
            except IndexError:
                pass
        return text

    # Get receiver number(s)
    while 1:
        receiver = raw_input('Receiver(s): ')
        receiver_clean = replace_contacts(receiver)
        # Test whether all contacts have been matched
        if not re.sub('[ +,]', '', receiver_clean).isdigit():
            print 'Unmatched contact or invalid phone number. ' + \
                   'Only comma separated contact names or numbers are allowed.'
        else:
            readline.set_completer()  # Disable tab completion
            break
    # Get message text
    while 1:
        message = raw_input('Message: ').strip()
        if len(message) == 0:
            print 'Please enter a message'
        elif len(unicode(message, 'utf-8')) > 440:
            print 'Message too long (max 440 characters)'
        else:
            break

    # Actually send the SMS
    url = 'https://xtrazone.sso.bluewin.ch/index.php/20,53,ajax,,,283/' \
          '?route=%2Fmessaging%2Foutbox%2Fsendmobilemsg'
    data = {'attachmentId': '',
            'attachments': '',
            'messagebody': message,
            'receiversnames': receiver_clean,
            'recipients': '[]',
            }
    browser.open(url, urllib.urlencode(data))
    resp = json.loads(browser.response().read())
    if (resp['content']['headline'] != 'Verarbeitung erfolgreich' or
        resp['content']['isError'] != False):
        raise XtrazoneError('Unknown error sending SMS.')

    # Show success message
    #print resp['content']['messages']['generic'][0]
    print 'SMS sent successfully.'


def main():
    # Parse configuration file
    username, password, imageviewer = parse_config()

    # Initialize mechanize browser session
    browser = init()

    # Display CAPTCHA and log in
    while(1):
        try:
            login(browser, username, password, imageviewer)
            break
        except CaptchaError as e:
            print 'Wrong captcha. Try again.'

    # Get contacts
    print 'Retrieving contacts...'
    contacts = pull_contacts(browser)

    # Show welcome message
    nickname, fullname, remaining = get_user_info(browser)
    print 'Hi, %s. You have %s SMS remaining.' % (fullname, remaining)

    # Main menu
    while(1):
        msg = "Press 'n' to compose an sms, 'c' to show contacts, " \
              "'s' to search contacts, 'a' to add a contact or 'x' to exit: "
        choice = raw_input(msg).strip().lower()
        if choice == 'n':
            try:
                send_sms(browser, contacts)
                print "%s SMS remaining." % get_user_info(browser)[2]
            except KeyboardInterrupt:
                print 'Cancel...'
                continue
        elif choice == 'c':
            print_contacts(contacts)
        elif choice == 'a':
            try:            
                add_contact(browser)
                contacts = pull_contacts(browser)
            except XtrazoneError as e:
                print 'Error: ' + str(e)
        elif choice == 's':
            searchstr = raw_input("Enter a search string: ").decode(sys.stdout.encoding)
            searchstr = remove_accents(searchstr)
            fcontacts = lambda x: x[2].lower().find(searchstr.lower()) != -1
            print_contacts(filter(fcontacts, contacts))
        elif choice == 'x':
            break

    print 'Goodbye.'


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print 'Error: ' + str(e)
        sys.exit(1)
