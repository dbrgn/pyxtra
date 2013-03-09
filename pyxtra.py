#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A small command-line utility written in Python to access the Swisscom
Xtrazone SMS service

Version: 1.6

License:
Copyright (C) 2011-2013 Danilo Bargen, Peter Manser and contributors.

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
import re
import stat
import urllib
import hashlib
import getpass
import ConfigParser
import unicodedata
from StringIO import StringIO
from datetime import datetime
from gorrion import GorrionService, GorrionError

try:
    import readline
    import json
    import mechanize
    from bs4 import BeautifulSoup
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
__tracebacks = False  # Set to True to show tracebacks
__separator = '--------------------'
__xtra_sms_max_length = 440  # Max length of xtrazone sms is 440
__nr_validation_regex = r'^(((((\+|00)?41)|0)7[6-9])|((\+|00)?423))\d{7}$'
__strict_nr_validation_regex = r'^41\d{9}$'

STDIN_ENC = sys.stdin.encoding
STDOUT_ENC = sys.stdout.encoding


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
    return u''.join([c for c in nkfd_form if not unicodedata.combining(c)])


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
        username = raw_input('\nUsername: ').strip()
        print 'Enter your password, in case you want to store it in the ' \
              'config file. Warning: Password will be saved in plaintext.'
        password = getpass.getpass('Password (ENTER to skip): ').strip()

        # Logging
        logging_msg = 'Do you want to log all sent SMS to %s?' % log_file
        logging = 'yes' if yn_choice(logging_msg) else 'no'

        # Auto send long sms
        auto_send_long_sms_msg = 'Do you want to ignore warnings for SMS ' \
                                 'longer than %u characters?' % __xtra_sms_max_length
        auto_send_long_sms = 'yes' if yn_choice(auto_send_long_sms_msg, 'n') else 'no'

        # Anticaptcha
        anticaptcha_msg = 'Do you want to use the anticaptcha service?'
        anticaptcha = 'yes' if yn_choice(anticaptcha_msg) else 'no'

        print 'Initial configuration is finished. You may edit your ' + \
              'configuration file at %s.\n' % config_file

        config.add_section('settings')
        config.set('settings', 'username', username)
        config.set('settings', 'password', password)
        config.set('settings', 'logging', logging)
        config.set('settings', 'auto_send_long_sms', auto_send_long_sms)

        config.add_section('captcha')
        config.set('captcha', 'anticaptcha', anticaptcha)
        config.set('captcha', 'anticaptcha_max_tries', 3)
        config.write(open(config_file, 'w'))
        os.chmod(config_file, stat.S_IREAD | stat.S_IWRITE)
    else:
        # Add sections if necessary
        for s in ['settings', 'captcha']:
            try:
                config.add_section(s)
            except ConfigParser.DuplicateSectionError:
                pass

        # Get user data
        username = config.get('settings', 'username')
        password = config.get('settings', 'password')

        # Get logging settings
        try:
            logging = config.getboolean('settings', 'logging')
        except (ValueError, ConfigParser.NoOptionError):
            logging_msg = 'Do you want to log all sent SMS to %s?' % log_file
            logging = 'yes' if yn_choice(logging_msg) else 'no'
            config.set('settings', 'logging', logging)

        # Get long sms settings
        try:
            auto_send_long_sms = config.getboolean('settings',
                                    'auto_send_long_sms')
        except (ValueError, ConfigParser.NoOptionError):
            auto_send_long_sms_msg = 'Do you want to ignore warnings for SMS ' \
                                     'longer than %u characters?' % __xtra_sms_max_length
            auto_send_long_sms = 'yes' if yn_choice(auto_send_long_sms_msg, 'n') else 'no'
            config.set('settings', 'auto_send_long_sms', auto_send_long_sms)

        # Get anticaptcha settings
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

    # Set default values
    if not 'anticaptcha_max_tries' in locals():
        anticaptcha_max_tries = 3
    if not anticaptcha in ['yes', True]:
        anticaptcha = False
    if not auto_send_long_sms in ['yes', True]:
        auto_send_long_sms = False
    return {'username': username,
            'password': password,
            'logging': logging,
            'auto_send_long_sms': auto_send_long_sms,
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
        ('User-agent', 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 7.1; Trident/5.0)'),
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
    if anticaptcha:
        gorrion = GorrionService()

    while 1:
        try:
            if not password:
                password = getpass.getpass('Xtrazone password: ').strip()

            # Get CAPTCHA URL
            browser.open('https://xtrazone.sso.bluewin.ch/index.html')

            browser.addheaders = [
                ('X-Requested-With', 'XMLHttpRequest'),
                ('X-Header-XtraZone', 'XtraZone'),
                ('Referer', 'https://xtrazone.sso.bluewin.ch/index.html'),
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
                if captcha_tries == 1:
                    print 'Trying to crack CAPTCHA...'
                try:
                    captcha = gorrion.get_captcha(captcha_token)
                except Exception as e:
                    anticaptcha = False
                    print 'Error, cracking CAPTCHA failed (%s)' % str(e)

            # User has to enter CAPTCHA manually
            else:
                if anticaptcha and captcha_tries == anticaptcha_max_tries + 1:
                    print 'Automatically cracking CAPTCHA failed. :('

                captcha_url = 'http:%s' % resp['content']['messages']['operation']['imgUrl']
                # Display CAPTCHA in a new window
                tk_root = Tkinter.Tk(className='CAPTCHA')
                img_bytes = StringIO(urllib.urlopen(captcha_url).read())
                img_obj = Image.open(img_bytes)
                img = ImageTk.PhotoImage(img_obj)
                captcha_label = Tkinter.Label(tk_root, image=img)
                captcha_label.pack()

                # Get CAPTCHA text
                while not captcha:
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
                ('Referer', 'https://xtrazone.sso.bluewin.ch/index.html'),
            ]
            url = 'https://xtrazone.sso.bluewin.ch/index.php/22,39,ajax_json,,,157/'
            data = {
                'action': 'ssoLogin',
                'do_sso_login': 1,
                'passphrase': captcha,
                'sso_password': password,
                'sso_user': username,
                'token': captcha_token,
            }
            browser.open(url, urllib.urlencode(data))

            resp = json.loads(browser.response().read())
            if resp['status'] == 'captcha_failed':
                raise RuntimeError('CAPTCHA failed: %s' % resp['message'])
            if resp['status'] != 'login_ok':
                raise RuntimeError('Login failed: %s' % resp['message'])

            # Everything worked fine :)
            if anticaptcha and captcha_tries <= anticaptcha_max_tries:
                if captcha:  # Report successful CAPTCHAs to gorrion
                    try:
                        gorrion.report(captcha, 1)
                    except GorrionError as e:
                        print 'Anticaptcha reporting: %s' % str(e)
            break

        except RuntimeError as e:
            if anticaptcha and captcha_tries <= anticaptcha_max_tries:
                if captcha:
                    pass  # TODO Possibly report to gorrion
            if captcha_tries > anticaptcha_max_tries:
                print 'Wrong CAPTCHA. Try again.'

    if anticaptcha:
        del gorrion


def get_user_info(browser):
    """Retrieve user info.

    Return nickname, full name, number and remaining SMS.
    """
    browser.open('https://xtrazone.sso.bluewin.ch/index.php/20,53,ajax,,,283/'
                 '?route=%2Flogin%2Fuserboxinfo')
    resp = json.loads(browser.response().read())

    soup1 = BeautifulSoup(resp['content'])
    userinfo = soup1.find('div', 'userinfo')

    nickname = userinfo.find('h5').text
    fullname = userinfo.find('h6').text
    remaining = filter(lambda c: c.isdigit(), userinfo.find('span').text)

    browser.open('https://xtrazone.sso.bluewin.ch/index.php/20?route=%2Fprofile')
    soup2 = BeautifulSoup(browser.response().read())
    profile = soup2.find('dl', 'profile personal')
    try:
        own_number = profile.find(text=re.compile(r'^41\d{9}')).strip()
    except AttributeError:
        raise RuntimeError('Could not retrieve own number from profile.')

    return nickname, fullname, remaining, own_number


def pull_contacts(browser):
    """Retrieve contact list.

    Retrieves an .xls-export of all contacts, parses it and returns a list.
    """
    url = 'https://xtrazone.sso.bluewin.ch/index.php/20,53,ajax,,,98/?route=' \
          '%2Fprofile%2Fcontact%2Fexcelexport&suspAjax=1'
    browser.open(url)
    resp = browser.response().read()
    if not resp:
        return []
    book = xlrd.open_workbook(file_contents=resp, logfile=open(os.devnull, 'w'))
    sheet = book.sheet_by_index(0)
    contacts = [sheet.row_values(row) for row in range(1, sheet.nrows)]
    return sorted(contacts, key=lambda c: c[2])


def add_contact(browser, prename='', name='', nr=''):
    """Add a new contact to the XtraZone address book"""
    while not prename:
        prename = raw_input('First name: ').strip()
    if not name:
        name = raw_input('Name: ').strip()
    while not nr:
        nr = raw_input('Nr: ').strip()

    url = 'https://xtrazone.sso.bluewin.ch/index.php/20,53,ajax,,,283/?route=' \
          '%2Fprofile%2Fcontact%2Faddcontact&refresh=/profile/contact/list'
    data = {'contactId': '',
            'name': name,
            'natelnr': nr,
            'prename': prename,
            'save': 'Speichern',
            }
    print 'Adding contact, this might take a while...'
    browser.open(url, urllib.urlencode(data))

    resp = json.loads(browser.response().read())

    if 'Auf diese Inhalte kannst Du nicht zugreifen' in resp['content']:
        print 'Session has expired. Reconnecting...'
        cfg = parse_config()
        login(browser, cfg['username'], cfg['password'],
              cfg['anticaptcha'], cfg['anticaptcha_max_tries'])
        print 'Session is restored. Please try again.'
    if resp['content']['isError']:
        raise RuntimeError('Adding contact failed: %s' % resp['content']['headline'])
    print 'Successfully saved contact %s %s.' % (prename, name)


def delete_contact(browser, own_number, other_numbers):
    """Delete a contact from the XtraZone address book."""

    # Validate other_number
    invalid_numbers = []
    numbers = other_numbers.split(',')
    for i, num in enumerate(numbers):
        num = filter(lambda c: c.isdigit(), num)
        if num.startswith('0'):
            num = '41' + num[1:]
        if not re.match(__strict_nr_validation_regex, num):
            invalid_numbers.append(num)
        numbers[i] = num
    if invalid_numbers:
        raise RuntimeError('Invalid phone numbers: {}'.format(', '.join(invalid_numbers)))

    # Actually send delete request
    url = 'https://xtrazone.sso.bluewin.ch/index.php/20,53,ajax,,,283/?route=' \
          '%2Fprofile%2Fcontact%2Fdeletecontact&refresh=/profile/contact/contactsanchors'
    for other_number in numbers:
        own_hash = hashlib.md5(own_number).hexdigest()
        other_hash = hashlib.md5(other_number).hexdigest()
        data = {'id': 'com.swisscom.person:{}:{}'.format(own_hash, other_hash)}
        print 'Deleting {}...'.format(other_number)
        browser.open(url, urllib.urlencode(data))

        resp = json.loads(browser.response().read())

        # Handle errors
        if resp['content']['isError']:
            msg = resp['content']['headline']
            if 'messages' in resp['content'] and 'generic' in resp['content']['messages']:
                msg = u'{}: {}'.format(msg, resp['content']['messages']['generic'][0])
            raise RuntimeError(u'Deleting contact {} failed: {}'
                    .format(other_number, msg).encode(STDOUT_ENC, 'replace'))

    pluralized = 'contact' if len(numbers) == 1 else 'contacts'


def print_contacts(contacts):
    """Print nicely formatted contact list."""
    def natel_nr(nr):
        """Return correctly formatted cell phone nr."""
        nr = str(nr)[2:11]
        return '0%s %s %s %s' % (nr[0:2], nr[2:5], nr[5:7], nr[7:9])

    print __separator
    if contacts:
        for contact in contacts:
            print '%s: %s' % (contact[2].strip(), natel_nr(contact[1]))
    else:
        print "(no matches)"
    print __separator


def query_contact(contacts=[], query_string='Receivers: '):
    """Query for contact number and return it."""

    # Configure and enable tab completion

    delimiter = ', ' if sys.platform == 'darwin' else ','

    def completer(text, state):
        """Contacts completer function for readline module"""
        options = [x[2].strip() for x in contacts
                   if x[2].lower().startswith(text.strip().lower())]
        try:
            return options[state] + delimiter
        except IndexError:
            return None

    readline.set_completer(completer)
    readline.set_completer_delims(delimiter)
    if sys.platform == 'darwin':
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")

    def validate_contacts(text):
        """Replace contacts with corresponding cell phone numbers."""
        numbers = text.split(',')
        numbers = map(lambda x: unicode(x, STDIN_ENC), numbers)  # To unicode
        invalid_numbers = []
        for nr in numbers:
            # TODO: could several numbers match?
            f = [c for c in contacts
                   if c[2].strip().lower() == nr.strip().lower()]
            if f:
                text = text.replace(nr, '0' + str(f[0][1])[2:11])
            else:
                # Current nr is not a name in address book. Validate it.
                if not re.match(__nr_validation_regex, nr.replace(' ', '')):
                    invalid_numbers.append(nr)
        if invalid_numbers:
            raise ValueError(', '.join([nr.strip() for nr in invalid_numbers]))
        return text

    # Get receiver number(s)
    while 1:
        receiver = raw_input(query_string).strip(', ')
        try:
            receiver_clean = validate_contacts(receiver)
        except ValueError as e:
            print 'Error: Unmatched contact or invalid phone number (%s).' % unicode(e)
        else:
            readline.set_completer()  # Disable tab completion
            return receiver_clean


def send_sms(browser, receiver, logging=False, auto_send_long_sms=False, message=None):
    """Send SMS.

    Query for message and send SMS.
    """
    # Get message text
    while not message:
        message = raw_input('Message: ').strip()
        message = unicode(message, STDIN_ENC).encode(STDOUT_ENC, 'replace')

    count = len(message)
    if count > __xtra_sms_max_length:
        if auto_send_long_sms or yn_choice('Message is %u characters long and '
                                           'will be split into several SMS. '
                                           'Do you want to send it anyway?' % count):
            i = 0
            while i < count:
                send_sms(browser, receiver, logging, auto_send_long_sms,
                         message[i:i + __xtra_sms_max_length - 1])
                i += __xtra_sms_max_length - 1
            return

    # Actually send the SMS
    url = 'https://xtrazone.sso.bluewin.ch/index.php/20,53,ajax,,,283/' \
          '?route=%2Fmessaging%2Foutbox%2Fsendmobilemsg'
    data = {'attachmentId': '',
            'attachments': '',
            'messagebody': message,
            'receiversnames': receiver,
            'recipients': '[]',
            }
    browser.open(url, urllib.urlencode(data))
    resp = json.loads(browser.response().read())
    try:
        valid_headlines = (
            u'Verarbeitung erfolgreich',
            u'Traitement réussi.',
            u'Elaborazione riuscita.',
        )
        resp_headline = resp['content']['headline']
        resp_error = resp['content']['isError']
        if resp_headline not in valid_headlines or resp_error is not False:
            raise RuntimeError('Unknown error sending SMS.')
    except TypeError:  # Something went wrong.
        if __debug:
            print resp
        if 'Auf diese Inhalte kannst Du nicht zugreifen' in resp['content']:
            print 'Session has expired. Reconnecting...'
            cfg = parse_config()
            login(browser, cfg['username'], cfg['password'],
                  cfg['anticaptcha'], cfg['anticaptcha_max_tries'])
            send_sms(browser, receiver, logging, auto_send_long_sms, message)
        else:
            raise RuntimeError('Unknown error sending SMS.')
    else:
        print 'SMS sent successfully.'

    # If desired, log SMS
    if logging:
        pyxtra_folder = os.path.expanduser(os.path.join('~', '.pyxtra'))
        log_file = os.path.join(pyxtra_folder, 'sent.log')
        log_file_created = not os.path.exists(log_file)
        f = open(log_file, 'a')  # Open file for appending
        print >> f, 'Date: %s' % datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        print >> f, 'Receivers: %s' % receiver
        print >> f, 'Message: %s\n' % message
        f.close()
        if log_file_created:
            os.chmod(log_file, stat.S_IREAD | stat.S_IWRITE)


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
    nickname, fullname, remaining, own_number = get_user_info(browser)
    print 'Hi %s. You have %s SMS remaining.' % (fullname, remaining)

    def print_help():
        print 'Available commands:'
        print '\tn,   new      - Compose an SMS'
        print '\tn!,  new!     - SMS mode (<Ctrl>+c to exit)'
        print '\tn!!, new!!    - Conversation mode (<Ctrl>+c to exit)'
        print '\tc,   contacts - Show contacts'
        print '\ts,   search   - Search contacts'
        print '\ta,   add      - Add a new contact'
        print '\td,   delete   - Delete one or more contacts'
        print '\th,   help     - Show this help'
        print '\tq,   quit     - Quit'

    # Main menu
    print "Use 'h' or 'help' to show available commands."
    while 1:
        input = raw_input('> ').strip().lower().partition(' ')
        choice = input[0]
        params = input[2]

        if choice in ['h', 'help']:
            print_help()
        elif choice in ['n', 'new', 'n!', 'new!', 'n!!', 'new!!']:
            try:
                receiver_lock = choice in ['n!!', 'new!!']
                if receiver_lock:
                    receiver = query_contact(contacts)
                while 1:
                    if not receiver_lock:
                        receiver = query_contact(contacts)
                    send_sms(browser, receiver, cfg['logging'], cfg['auto_send_long_sms'])
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
            except RuntimeError as e:
                print 'Error: %s' % str(e)
        elif choice in ['d', 'delete']:
            try:
                other_number = query_contact(contacts, query_string='Contacts: ')
                delete_contact(browser, own_number, other_number)
                contacts = pull_contacts(browser)
            except KeyboardInterrupt:
                print '\nCancel...'
                continue
            except RuntimeError as e:
                print 'Error: %s' % str(e)
        elif choice in ['s', 'search']:
            searchstr = params

            if not searchstr:
                try:
                    searchstr = raw_input("Enter a search string: ").decode(STDIN_ENC)
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
            raise RuntimeError(msg)
    except ConfigParser.NoOptionError:
        msg = 'Error in configuration file. Please remove your configfile ' + \
              '(usually in ~/.pyxtra/) and try again.'
        if not __tracebacks:
            print 'Error: %s' % msg
            sys.exit(1)
        else:
            raise RuntimeError(msg)
    except Exception as e:
        if not __tracebacks:
            print 'Error: %s' % str(e)
            sys.exit(1)
        else:
            raise
