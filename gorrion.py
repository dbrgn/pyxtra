#!/usr/bin/python
import os 
import socket 
import urllib2 
import httplib 
import base64 
import hashlib 
_name0x0 = base64.b64decode (  'aHR0cHM6Ly93d3cuZ29ycmlvbi5jaC9jYXB0Y2hhLnNtc3NlbmRlcj9tb2RlPXh0cmE=' )  
_name0x1 = 'LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlDWFFJQkFBS0JnUURRWDlXbWlVZkw4TGFpeUNlZkJLZ' + 'FhUSDBnbVNJdEkySWowNXM0d0xZQlB3OUdGSytYCno2WWI5dlNleDA3bTVwR1htVmd4Q3N4QVNiUnEvTis4RDdOSnhRdGxxN' + 'nVjRjRTRXNMN3FTM09rMHJEQUVqUi8KT3JDOUN4cmxoQ0ptNFNhMVE5ZFJ2bkhoYTVuSFIzME53WU1jYk1TRnBPa0pyVVRlQ' + 'zBzMCtJLzIvd0lEQVFBQgpBb0dBS3R3TGJmMityc3dNUk44Mmh4YkY5TWJlMWQycGtlODlPSEZGOUI1dlVVSlBPZkwzU3hxQ' + 'zZDMmJreTBiCnBaSzNUNTlTN0lOMEQ2VVpYd2cwWE5JOTVnZHVFM29rRXdIdzFLNDhUMEtLczJENFEyN3I0STZJejUwemdGU' + 'GwKYlQ0MjEwazFWcjJ2eVJheURoT0RpRlhLVHY3SVBsRGJ0V2RoT0pHa2FvRVpFb0VDUVFEeGdobmtjc2F0M1FnYworMXVsN' + 'G4yWDF2MUFGcDN4MEFkVFY4RDlKdkMwL3hHcWVXTTBIbFBpanhKOW5iZGF3MFVzeklORGdQSFRqM3NxCmN1aDlJZXVaQWtFQ' + 'TNPREFkSlRPQVlLWUdCTTNLRmNuNjNtQnFLYzd5ZGJlbjltczBaODRIY3ZGQmNHWkdWSEEKdzZCcTJHMVJYTkxrbVZFL0lZN' + '2VOZlNXNzN6Q1JpL1dWd0pCQU5hSG8waHpURm1WUm1lNFFLa1NrRTRaQTgyeQpTWXRNSjdXNDlnM3FVVmYyWEZMNmtVenl3O' + 'EUxSmsrL2tlaG1IVVMyUnNQbi91alhRNmxwZVd2dWZjRUNRQ1JOCkgvUkpISTVzK3poQnVEZitFd2FGWXNUb0wxQmQ2eHJVZ' + 'UsyL0FFY05YV1V6eTBpNUFmaGszZ3FSOU9SUG1OaUYKM04xVUVMdEhacU1YbXdwVUJHTUNRUURXNVdicEhKYzliNnBpeER0W' + 'EdPSU9Idk9FVWJYYjNYc1VFRXlkRzMwWApCMEhpZmRBMk1oUmZvREhwejMwcmg0RXZRdFdFTnZ4MTVGZmRHdXFrUUFIRAotL' + 'S0tLUVORCBSU0EgUFJJVkFURSBLRVktLS0tLQo=' 
_name0x2 = 'Q2VydGlmaWNhdGU6CiAgICBEYXRhOgogICAgICAgIFZlcnNpb246IDEgKDB4MCkKICAgICAgICBTZXJpYWwgTnVt' + 'YmVyOiAxMyAoMHhkKQogICAgICAgIFNpZ25hdHVyZSBBbGdvcml0aG06IG1kNVdpdGhSU0FFbmNyeXB0aW9uCiAgICAgICAg' + 'SXNzdWVyOiBPPUdvcnJpb24vZW1haWxBZGRyZXNzPXBvc3RtYXN0ZXJAZ29ycmlvbi5jaCwgTD1PYmVyd2lsLCBTVD1CYXNl' + 'bCwgQz1DSCwgQ049R29ycmlvbiBSb290IENBCiAgICAgICAgVmFsaWRpdHkKICAgICAgICAgICAgTm90IEJlZm9yZTogTWFy' + 'IDMxIDE2OjE0OjE2IDIwMTEgR01UCiAgICAgICAgICAgIE5vdCBBZnRlciA6IE1hciAzMCAxNjoxNDoxNiAyMDEzIEdNVAog' + 'ICAgICAgIFN1YmplY3Q6IEM9Q0gsIFNUPUJhc2VsLCBPPUdvcnJpb24sIE9VPXB5eHRyYSwgQ049RGFuaWxvIEJhcmdlbiwg' + 'UGV0ZXIgTWFuc2VyL2VtYWlsQWRkcmVzcz1nZXp1cnVAZ21haWwuY29tCiAgICAgICAgU3ViamVjdCBQdWJsaWMgS2V5IElu' + 'Zm86CiAgICAgICAgICAgIFB1YmxpYyBLZXkgQWxnb3JpdGhtOiByc2FFbmNyeXB0aW9uCiAgICAgICAgICAgIFJTQSBQdWJs' + 'aWMgS2V5OiAoMTAyNCBiaXQpCiAgICAgICAgICAgICAgICBNb2R1bHVzICgxMDI0IGJpdCk6CiAgICAgICAgICAgICAgICAg' + 'ICAgMDA6ZDA6NWY6ZDU6YTY6ODk6NDc6Y2I6ZjA6YjY6YTI6Yzg6Mjc6OWY6MDQ6CiAgICAgICAgICAgICAgICAgICAgYTc6' + 'NTc6NGM6N2Q6MjA6OTk6MjI6MmQ6MjM6NjI6MjM6ZDM6OWI6Mzg6YzA6CiAgICAgICAgICAgICAgICAgICAgYjY6MDE6M2Y6' + 'MGY6NDY6MTQ6YWY6OTc6Y2Y6YTY6MWI6ZjY6ZjQ6OWU6Yzc6CiAgICAgICAgICAgICAgICAgICAgNGU6ZTY6ZTY6OTE6OTc6' + 'OTk6NTg6MzE6MGE6Y2M6NDA6NDk6YjQ6NmE6ZmM6CiAgICAgICAgICAgICAgICAgICAgZGY6YmM6MGY6YjM6NDk6YzU6MGI6' + 'NjU6YWI6YWI6OWM6MTc6ODQ6ODQ6YjA6CiAgICAgICAgICAgICAgICAgICAgYmU6ZWE6NGI6NzM6YTQ6ZDI6YjA6YzA6MTI6' + 'MzQ6N2Y6M2E6YjA6YmQ6MGI6CiAgICAgICAgICAgICAgICAgICAgMWE6ZTU6ODQ6MjI6NjY6ZTE6MjY6YjU6NDM6ZDc6NTE6' + 'YmU6NzE6ZTE6NmI6CiAgICAgICAgICAgICAgICAgICAgOTk6Yzc6NDc6N2Q6MGQ6YzE6ODM6MWM6NmM6YzQ6ODU6YTQ6ZTk6' + 'MDk6YWQ6CiAgICAgICAgICAgICAgICAgICAgNDQ6ZGU6MGI6NGI6MzQ6Zjg6OGY6ZjY6ZmYKICAgICAgICAgICAgICAgIEV4' + 'cG9uZW50OiA2NTUzNyAoMHgxMDAwMSkKICAgIFNpZ25hdHVyZSBBbGdvcml0aG06IG1kNVdpdGhSU0FFbmNyeXB0aW9uCiAg' + 'ICAgICAgNjg6NmE6YjM6NWU6MWM6ODU6OTY6OTY6YjA6NmQ6OTc6NDE6MWI6ZmU6Mzc6YmY6MWE6MWI6CiAgICAgICAgZWE6' + 'NmY6YmU6NmQ6NGI6YWQ6MjA6NWI6OTA6MTE6Y2I6YjI6ZWM6YWQ6NzQ6MmU6NzA6OTI6CiAgICAgICAgNDI6YTA6MTY6ZTA6' + 'OTI6Zjk6YWU6OTU6ZjU6YmU6MjE6YmU6MWU6ODk6YTE6MjY6ODE6ZWM6CiAgICAgICAgMjM6MDE6OTk6MmI6MzM6MWE6Mjk6' + 'OGY6NWQ6MzY6ODg6NTM6OTc6N2Q6MjI6NmM6OGU6MDE6CiAgICAgICAgZjA6YWM6NDg6NDI6ZDg6NTE6MTQ6Njc6YzU6ODU6' + 'ZjA6ZjU6MTE6OTI6ODM6NjY6YTI6NWE6CiAgICAgICAgOTI6NzQ6ZmU6MTY6MDc6N2Y6MzE6ODg6M2Q6Mjg6YmY6ZTQ6MzY6' + 'ZGQ6Yjc6OTU6NTc6Mzg6CiAgICAgICAgOWQ6ZDU6ZGU6MTA6ZWY6MjM6NzE6OGQ6M2I6Njg6MjE6YWQ6YjI6NDk6N2M6YTk6' + 'NmY6ZDA6CiAgICAgICAgYmY6ZDcKLS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUNlVENDQWVJQ0FRMHdEUVlKS29a' + 'SWh2Y05BUUVFQlFBd2dZRXhFREFPQmdOVkJBb1RCMGR2Y25KcGIyNHgKSkRBaUJna3Foa2lHOXcwQkNRRVdGWEJ2YzNSdFlY' + 'TjBaWEpBWjI5eWNtbHZiaTVqYURFUU1BNEdBMVVFQnhNSApUMkpsY25kcGJERU9NQXdHQTFVRUNCTUZRbUZ6Wld3eEN6QUpC' + 'Z05WQkFZVEFrTklNUmd3RmdZRFZRUURFdzlICmIzSnlhVzl1SUZKdmIzUWdRMEV3SGhjTk1URXdNek14TVRZeE5ERTJXaGNO' + 'TVRNd016TXdNVFl4TkRFMldqQ0IKaHpFTE1Ba0dBMVVFQmhNQ1EwZ3hEakFNQmdOVkJBZ1RCVUpoYzJWc01SQXdEZ1lEVlFR' + 'S0V3ZEhiM0p5YVc5dQpNUTh3RFFZRFZRUUxFd1p3ZVhoMGNtRXhKREFpQmdOVkJBTVRHMFJoYm1sc2J5QkNZWEpuWlc0c0lG' + 'QmxkR1Z5CklFMWhibk5sY2pFZk1CMEdDU3FHU0liM0RRRUpBUllRWjJWNmRYSjFRR2R0WVdsc0xtTnZiVENCbnpBTkJna3EK' + 'aGtpRzl3MEJBUUVGQUFPQmpRQXdnWWtDZ1lFQTBGL1Zwb2xIeS9DMm9zZ25ud1NuVjB4OUlKa2lMU05pSTlPYgpPTUMyQVQ4' + 'UFJoU3ZsOCttRy9iMG5zZE81dWFSbDVsWU1Rck1RRW0wYXZ6ZnZBK3pTY1VMWmF1cm5CZUVoTEMrCjZrdHpwTkt3d0JJMGZ6' + 'cXd2UXNhNVlRaVp1RW10VVBYVWI1eDRXdVp4MGQ5RGNHREhHekVoYVRwQ2ExRTNndEwKTlBpUDl2OENBd0VBQVRBTkJna3Fo' + 'a2lHOXcwQkFRUUZBQU9CZ1FCb2FyTmVISVdXbHJCdGwwRWIvamUvR2h2cQpiNzV0UzYwZ1c1QVJ5N0xzclhRdWNKSkNvQmJn' + 'a3ZtdWxmVytJYjRlaWFFbWdld2pBWmtyTXhvcGoxMDJpRk9YCmZTSnNqZ0h3ckVoQzJGRVVaOFdGOFBVUmtvTm1vbHFTZFA0' + 'V0IzOHhpRDBvditRMjNiZVZWemlkMWQ0UTd5TngKalR0b0lhMnlTWHlwYjlDLzF3PT0KLS0tLS1FTkQgQ0VSVElGSUNBVEUt' + 'LS0tLQo=' 
_name0x3 = '/tmp/%s' % hashlib.md5 (  _name0x1 + socket.gethostname (  )  )  . hexdigest (  )  
_name0x4 = '/tmp/%s' % hashlib.md5 (  _name0x2 + socket.gethostname (  )  )  . hexdigest (  )  
class _name0x5 (  urllib2.HTTPSHandler )  : 
    def __init__ (  name0x6 , name0x7 , name0x8 )  : 
        urllib2.HTTPSHandler.__init__ (  name0x6 )  
        name0x6.name0x7 = name0x7 
        name0x6.name0x8 = name0x8 
    def https_open (  name0x6 , name0x9 )  : 
        return name0x6.do_open (  name0x6.name0xa , name0x9 )  
    def name0xa (  name0x6 , name0xb , timeout = 300 )  : 
        return httplib.HTTPSConnection (  name0xb , key_file = name0x6.name0x7 , cert_file = name0x6.name0x8 )  
class GorrionError (  Exception )  : 
    '''Thrown upon errors with the CAPTCHA cracking.''' 
    pass 
def _name0xc (  )  : 
    name0xd = open (  _name0x3 , 'w' )  
    name0xe = open (  _name0x4 , 'w' )  
    name0xd.write (  base64.b64decode (  _name0x1 )  )  
    name0xe.write (  base64.b64decode (  _name0x2 )  )  
    name0xd.close (  )  
    name0xe.close (  )  
    try : 
        name0xf = urllib2.build_opener (  _name0x5 (  _name0x3 , _name0x4 )  )  
    except urllib2.URLError : 
        raise GorrionError (  'Could not connect to anticaptcha service.' )  
    else : 
        return name0xf 
def _name0x10 (  )  : 
    try : 
        os.remove (  _name0x3 )  
        os.remove (  _name0x4 )  
    except OSError : 
        pass 
def _name0x11 (  name0x12 )  : 
    name0xf = _name0xc (  )  
    try : 
        name0x13 = name0xf.open (  '%s&token=%s' % (  _name0x0 , name0x12 )  )  . read (  )  
    except urllib2.HTTPError : 
        raise GorrionError (  'Could not connect to anticaptcha service.' )  
    if name0x13.startswith (  'Captcha: ' )  : 
        name0x14 = name0x13.replace (  'Captcha: ' , '' )  
    else : 
        raise GorrionError (  'Anticaptcha service returns invalid reply.' )  
    if name0x14 == 'std::exception' : 
        raise GorrionError (  'Anticaptcha service returned an exception. ' + 'Invalid or expired token?' )  
    return name0x14 
def get_captcha (  name0x12 )  : 
    '''Try to crack CAPTCHA and return possible answer.''' 
    try : 
        name0x14 = _name0x11 (  name0x12 )  
    except GorrionError : 
        _name0x10 (  )  
        raise 
    else : 
        _name0x10 (  )  
        return name0x14 
def _name0x15 (  name0x14 , name0x16 )  : 
    if isinstance (  name0x14 , str )  : 
        name0xf = _name0xc (  )  
        if name0x16 not in [ 0 , 1 ] : 
            raise GorrionError (  'Success value must be 0 or 1.' )  
        try : 
            name0xf.open (  '%s&validcaptcha=%s&success=%u' % (  _name0x0 , name0x14 , name0x16 )  )  
        except urllib2.URLError : 
            raise GorrionError (  'Could not report to anticaptcha service.' )  
    else : 
        raise GorrionError (  'Captcha must be a string' )  
def report (  name0x14 , name0x16 )  : 
    '''Report success to anticaptcha service.''' 
    try : 
        _name0x15 (  name0x14 , name0x16 )  
    except GorrionError : 
        _name0x10 (  )  
        raise 
    else : 
        _name0x10 (  )  
