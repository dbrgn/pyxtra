#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A small commandline utility written in Python to access the Swisscom
Xtrazone SMS service

Version: 1.1

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
from StringIO import StringIO
from datetime import datetime
import gorrion

try:
    import readline
    import rlcompleter 
    import json
    import mechanize
    from BeautifulSoup import BeautifulSoup
    import xlrd
    import Tkinter
    from PIL import Image, ImageTk
except ImportError as e:
    e_split = str(e)[16:].split(',')
    try:
        module = re.search(r'the (.+) package', e_split[1]).group(1)
    except IndexError:
        module = str(e)[16:]
    print 'Python module %s not found. Install it using pip or your ' \
          'system\'s package manager.' % module
    sys.exit(1)


# Some configuration variables
__debug = False  # Set to True to show debug output
__fakesend = False  # Set to True to not send sms
__tracebacks = False  # Set to True to show tracebacks
__separator = '--------------------'

class XtrazoneError(Exception):
    """Errors related with the Xtrazone page."""
    pass

class CaptchaError(XtrazoneError):
    """Errors related with the CAPTCHA."""
    pass


def yn_choice(message, default='y'):
    choices = 'Y/n' if default.lower() in ('y', 'yes') else 'y/N'
    choice = raw_input("%s (%s) " % (message, choices))
    values = ('y', 'yes', '') if default == 'y' else ('y', 'yes')
    return True if choice.strip().lower() in values else False


def remove_accents(ustr):
    """Removes accents from an unicode string.

    Strips all accents by removing the precomposed unicode characters. String
    to convert should be in unicode format.
    
    """
    nkfd_form = unicodedata.normalize('NFKD', unicode(ustr))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


def parse_config():
    """Parse the configuration file.
    
    Parses or creates a configuration file and returns a dictionary with
    all the configuration variables.
    
    """
    # Folder that will contain all configfiles
    config_folder = os.path.expanduser(os.path.join('~', '.pyxtra'))
    config_file = os.path.join(config_folder, 'config')
    log_file = os.path.join(config_folder, 'sent.log')

    config = ConfigParser.ConfigParser()  # ConfigParser instance

    # Create folder if necessary
    if not os.path.isdir(config_folder):
        os.mkdir(config_folder)

    # Read config, write default config file if it doesn't exist yet.
    if not len(config.read(config_file)):
        print 'Could not find configuration file. Creating %s.' % config_file

        # Login data
        username = raw_input('\nXtrazone username: ').strip()
        print 'Enter your password, in case you want to store it in the ' \
              'config file. Warning: Password will be saved in plaintext.'
        password = getpass.getpass('Xtrazone password (ENTER to skip): ').strip()

        # Logging
        logging_msg = 'Do you want to log all sent sms to %s?' % log_file
        logging = 'yes' if yn_choice(logging_msg) else 'no'

        # Anticaptcha
        anticaptcha_msg = 'Do you want to use the anticaptcha service?'
        anticaptcha = 'yes' if yn_choice(anticaptcha_msg) else 'no'

        print 'Initial configuration is finished. You may edit your ' + \
              'configuration file at %s.\n' % config_file

        config.add_section('settings')
        config.set('settings', 'username', username)
        config.set('settings', 'password', password)
        config.set('settings', 'logging', logging)
        config.add_section('captcha')
        config.set('captcha', 'anticaptcha', anticaptcha)
        config.set('captcha', 'anticaptcha_max_tries', 3)
        config.write(open(config_file, 'w'))
    else:
        # Add sections if necessary
        for s in ['settings', 'captcha']:
            try:
                config.add_section(s)
            except ConfigParser.DuplicateSectionError:
                pass
        username = config.get('settings', 'username')
        password = config.get('settings', 'password')
        try:
            logging = config.getboolean('settings', 'logging')
        except (ValueError, ConfigParser.NoOptionError):
            logging_msg = 'Do you want to log all sent sms to %s?' % log_file
            logging = 'yes' if yn_choice(logging_msg) else 'no'
            config.set('settings', 'logging', logging)
        try:
            anticaptcha = config.getboolean('captcha', 'anticaptcha')
        except (ValueError, ConfigParser.NoOptionError):
            anticaptcha_msg = 'Do you want to use the anticaptcha service?'
            anticaptcha = 'yes' if yn_choice(anticaptcha_msg) else 'no'
            config.set('captcha', 'anticaptcha', anticaptcha)
        try:
            anticaptcha_max_tries = config.getint('captcha',
                                    'anticaptcha_max_tries')
        except (ValueError, ConfigParser.NoOptionError):
            config.set('captcha', 'anticaptcha_max_tries', 3)

        # Write possibly changed configuration file
        config.write(open(config_file, 'w'))

    if not 'anticaptcha_max_tries' in locals():
        anticaptcha_max_tries = 3
    if not anticaptcha in ['yes', True]:
        anticaptcha = False
    return {'username': username,
            'password': password,
            'logging': logging,
            'anticaptcha': anticaptcha,
            'anticaptcha_max_tries': anticaptcha_max_tries}
   

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
            ('User-agent', 'Mozilla/4.0 (compatible; MSIE 8.0; \
                            Windows NT 6.0; Trident/4.0)'),
            ]
    # Debugging stuff
    if __debug:
        b.set_debug_http(True)
        b.set_debug_redirects(True)
        b.set_debug_responses(True)
    return b


def login(browser, username, password, anticaptcha=False, anticaptcha_max_tries=3):
    """Display the CAPTCHA and log in."""
    
    captcha_tries = 0
        
    while 1:
        try:
            if password == '':
                password = getpass.getpass('Xtrazone password: ').strip()
                
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
            captcha_token = resp['content']['messages']['operation']['token']

            captcha = ''
            captcha_tries += 1
            
            # Try to crack CAPTCHA automatically (Service by gorrion.ch)
            if anticaptcha and captcha_tries <= anticaptcha_max_tries:
                print 'Trying to crack CAPTCHA... (Try %s)' % captcha_tries
                try:
                    captcha = gorrion.get_captcha(captcha_token)
                except gorrion.GorrionError as e:
                    print e.message
                    anticaptcha = False
                    raise CaptchaError(e.message)
                    
            # User has to enter CAPTCHA manually
            else:
                if anticaptcha and captcha_tries == anticaptcha_max_tries + 1:
                    print 'Automatically cracking CAPTCHA failed. :('
                
                captcha_url = 'http:%s' % resp['content']['messages']['operation']['imgUrl']
                # Display CAPTCHA in a new window
                tk_root = Tkinter.Tk(className='CAPTCHA')
                img = ImageTk.PhotoImage(
                        Image.open(
                          StringIO(
                            urllib.urlopen(captcha_url).read()
                          )
                        )
                      )
                captcha_label = Tkinter.Label(tk_root, image=img)
                captcha_label.pack()
                
                # Get CAPTCHA text
                while captcha == '':
                    captcha = raw_input('Please enter CAPTCHA: ').strip()
                    
                # Destroy CAPTCHA window
                try:
                    tk_root.destroy()
                except Tkinter.TclError:
                    pass
                
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
            
            # Everything worked fine :)
            if anticaptcha and captcha_tries <= anticaptcha_max_tries:
                if captcha:  # Report successful CAPTCHAs to the anticaptcha service
                    try:
                        gorrion.report(captcha, 1)
                    except gorrion.GorrionError as e:
                        print 'Anticaptcha reporting: %s' % e.message
            break
            
        except CaptchaError as e:
            if anticaptcha and captcha_tries <= anticaptcha_max_tries:
                if captcha:  
                    pass  # Possibly report to gorrion
            if captcha_tries > anticaptcha_max_tries:
                print 'Wrong CAPTCHA. Try again.'

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
    while prename == '':
        prename = raw_input('First name: ').strip()
    if name == '':
        name = raw_input('Name: ').strip()
    while nr == '':
        nr = raw_input('Nr: ').strip()
    
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
        """Return correctly formatted cell phone nr."""
        nr = str(nr)[2:11]
        return '0%s %s %s %s' % (nr[0:2], nr[2:5], nr[5:7], nr[7:9])

    print __separator
    for contact in contacts:
        print '%s: %s' % (contact[2].strip(), natel_nr(contact[1]))
    print __separator


def send_sms(browser, contacts=[], logging=False):
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
    if sys.platform == 'darwin': 
        readline.parse_and_bind("bind ^I rl_complete")
    else: 
        readline.parse_and_bind("tab: complete")
    
    def replace_contacts(text):
        """Replace contacts with corresponding cell phone numbers."""
        numbers = text.split(',')
        for nr in numbers:
            f = [c for c in contacts
                   if c[2].strip().lower() == nr.strip().lower()]
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
        if not message:
            print 'Please enter a message'
        elif len(unicode(message, 'utf-8')) > 440:
            print 'Message too long (max 440 characters)'
        else:
            break
    
    if not __fakesend:
        while 1:
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
            try:
                if (resp['content']['headline'] != 'Verarbeitung erfolgreich' or
                    resp['content']['isError'] != False):
                    raise XtrazoneError('Unknown error sending SMS.')
            except TypeError:  # Something went wrong.
                if __tracebacks:
                    print resp
                if 'Auf diese Inhalte kannst Du nicht zugreifen' in resp['content']:
                    print 'Session has expired. Reconnecting...'
                    cfg = parse_config()
                    login(browser, cfg['username'], cfg['password'],
                          cfg['anticaptcha'], cfg['anticaptcha_max_tries'])
                else:
                    raise XtrazoneError('Unknown error sending SMS.')
            else:
                print 'SMS sent successfully.'
                break
    else:
        print 'SMS won\'t be send, because fakesend is activated.'
    
    # If desired, log SMS
    if logging:
        pyxtra_folder = os.path.expanduser(os.path.join('~', '.pyxtra'))
        log_file = os.path.join(pyxtra_folder, 'sent.log')
        f = open(log_file, 'a')  # Open file for appending
        print >> f, 'Date: %s' % datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        print >> f, 'Receivers (original): %s' % receiver
        print >> f, 'Receivers (cleaned): %s' % receiver_clean
        print >> f, 'Message: %s\n' % message
        f.close()
    
def main():
    """Main program loop.

    Parses the configuration, initializes the mechanize-browser, calls all
    functions to log in and shows a looped interface to send SMS messages and
    show or add contacts.
    """
    # Parse configuration file
    cfg = parse_config()

    # Initialize mechanize browser session
    browser = init()

    # Log in
    login(browser, cfg['username'], cfg['password'],
          cfg['anticaptcha'], cfg['anticaptcha_max_tries'])
    # Get contacts
    print 'Retrieving contacts...'
    contacts = pull_contacts(browser)
    
    # Show welcome message
    nickname, fullname, remaining = get_user_info(browser)
    print 'Hi %s. You have %s SMS remaining.' % (fullname, remaining)
    
    def print_help():
        print 'Available commands:'
        print '\tn,  new      - Compose an SMS' 
        print '\tn!, new!     - SMS mode (<Ctrl>+c to exit)' 
        print '\tc,  contacts - Show contacts'
        print '\ts,  search   - Search contacts'
        print '\ta,  add      - Add a new contact'
        print '\th,  help     - Show this help'
        print '\tq,  quit     - Quit'
    
    # Main menu
    print "Use 'h' or 'help' to show available commands."
    while 1:
        choice = raw_input('> ').strip().lower()
        if choice in ['h', 'help']:
            print_help()
        elif choice in ['n!', 'new!', 'n', 'new']:
            try:
                while 1:
                    send_sms(browser, contacts, cfg['logging'])
                    print "%s SMS remaining." % get_user_info(browser)[2]
                    if choice in ['n', 'new']:
                        break
            except KeyboardInterrupt:
                print '\nCancel...'
                continue
        elif choice in ['c', 'contacts']:
            print_contacts(contacts)
        elif choice in ['a', 'add']:
            try:            
                add_contact(browser)
                contacts = pull_contacts(browser)
            except KeyboardInterrupt:
                print '\nCancel...'
                continue
            except XtrazoneError as e:
                print 'Error: %s' % str(e)
        elif choice in ['s', 'search']:
            try:
                searchstr = raw_input("Enter a search string: ").decode(sys.stdout.encoding)
            except KeyboardInterrupt:
                print '\nCancel...'
                continue
            searchstr = remove_accents(searchstr)
            fcontacts = lambda x: x[2].lower().find(searchstr.lower()) != -1
            print_contacts(filter(fcontacts, contacts))
        elif choice in ['x', 'q', 'exit', 'quit']:
            break
        
        elif not choice:
            continue
        
        else:
            print "Unknown command. Use 'help' to show available commands."
    
    print 'Goodbye.'


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-v', '--version', '-h', '--help']:
            print __doc__
        else:
            print 'pyxtra is an interactive application and does not ' \
                  'support any commandline arguments.'
        sys.exit(1)
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print '\nGoodbye.'
        sys.exit(0)
    except mechanize.URLError:
        msg = 'Could not connect to Xtrazone. Check your internet connection.'
        if not __tracebacks:
            print 'Error: %s' % msg
            sys.exit(1)
        else:
            raise XtrazoneError(msg)    
    except ConfigParser.NoOptionError:
        msg = 'Error in configuration file. Please remove your configfile ' + \
              '(usually in ~/.pyxtra/) and try again.'
        if not __tracebacks:
            print 'Error: %s' % msg
            sys.exit(1)
        else:
            raise XtrazoneError(msg)    
    except Exception as e:
        if not __tracebacks:
            print 'Error: %s' % str(e)
            sys.exit(1)
        else:
            raise
