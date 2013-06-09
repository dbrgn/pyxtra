import urllib2 
import httplib 
import base64 
import tempfile 
_name0x0 = base64.b64decode (  'aHR0cHM6Ly93d3cuZ29ycmlvbi5jaC9jYXB0Y2hhLnNtc3NlbmRlcj9tb2RlPXh0cmE=' )  
_name0x1 = 'LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlDWFFJQkFBS0JnUURRWDlXbWlVZkw4TGFpeUNlZkJLZ' + 'FhUSDBnbVNJdEkySWowNXM0d0xZQlB3OUdGSytYCno2WWI5dlNleDA3bTVwR1htVmd4Q3N4QVNiUnEvTis4RDdOSnhRdGxxN' + 'nVjRjRTRXNMN3FTM09rMHJEQUVqUi8KT3JDOUN4cmxoQ0ptNFNhMVE5ZFJ2bkhoYTVuSFIzME53WU1jYk1TRnBPa0pyVVRlQ' + 'zBzMCtJLzIvd0lEQVFBQgpBb0dBS3R3TGJmMityc3dNUk44Mmh4YkY5TWJlMWQycGtlODlPSEZGOUI1dlVVSlBPZkwzU3hxQ' + 'zZDMmJreTBiCnBaSzNUNTlTN0lOMEQ2VVpYd2cwWE5JOTVnZHVFM29rRXdIdzFLNDhUMEtLczJENFEyN3I0STZJejUwemdGU' + 'GwKYlQ0MjEwazFWcjJ2eVJheURoT0RpRlhLVHY3SVBsRGJ0V2RoT0pHa2FvRVpFb0VDUVFEeGdobmtjc2F0M1FnYworMXVsN' + 'G4yWDF2MUFGcDN4MEFkVFY4RDlKdkMwL3hHcWVXTTBIbFBpanhKOW5iZGF3MFVzeklORGdQSFRqM3NxCmN1aDlJZXVaQWtFQ' + 'TNPREFkSlRPQVlLWUdCTTNLRmNuNjNtQnFLYzd5ZGJlbjltczBaODRIY3ZGQmNHWkdWSEEKdzZCcTJHMVJYTkxrbVZFL0lZN' + '2VOZlNXNzN6Q1JpL1dWd0pCQU5hSG8waHpURm1WUm1lNFFLa1NrRTRaQTgyeQpTWXRNSjdXNDlnM3FVVmYyWEZMNmtVenl3O' + 'EUxSmsrL2tlaG1IVVMyUnNQbi91alhRNmxwZVd2dWZjRUNRQ1JOCkgvUkpISTVzK3poQnVEZitFd2FGWXNUb0wxQmQ2eHJVZ' + 'UsyL0FFY05YV1V6eTBpNUFmaGszZ3FSOU9SUG1OaUYKM04xVUVMdEhacU1YbXdwVUJHTUNRUURXNVdicEhKYzliNnBpeER0W' + 'EdPSU9Idk9FVWJYYjNYc1VFRXlkRzMwWApCMEhpZmRBMk1oUmZvREhwejMwcmg0RXZRdFdFTnZ4MTVGZmRHdXFrUUFIRAotL' + 'S0tLUVORCBSU0EgUFJJVkFURSBLRVktLS0tLQo=' 
_name0x2 = 'Q2VydGlmaWNhdGU6CiAgICBEYXRhOgogICAgICAgIFZlcnNpb246IDMgKDB4MikKICAgICAgICBTZXJpYWwgTnVt' + 'YmVyOiAxNSAoMHhmKQogICAgU2lnbmF0dXJlIEFsZ29yaXRobTogc2hhMVdpdGhSU0FFbmNyeXB0aW9uCiAgICAgICAgSXNz' + 'dWVyOiBPPUdvcnJpb24vZW1haWxBZGRyZXNzPXBvc3RtYXN0ZXJAZ29ycmlvbi5jaCwgTD1PYmVyd2lsLCBTVD1CYXNlbCwg' + 'Qz1DSCwgQ049R29ycmlvbiBSb290IENBCiAgICAgICAgVmFsaWRpdHkKICAgICAgICAgICAgTm90IEJlZm9yZTogQXByIDIz' + 'IDE4OjQ4OjQxIDIwMTMgR01UCiAgICAgICAgICAgIE5vdCBBZnRlciA6IEFwciAyMiAxODo0ODo0MSAyMDE2IEdNVAogICAg' + 'ICAgIFN1YmplY3Q6IEM9Q0gsIFNUPUJhc2VsLCBPPUdvcnJpb24sIE9VPXB5eHRyYSwgQ049RGFuaWxvIEJhcmdlbiwgUGV0' + 'ZXIgTWFuc2VyL2VtYWlsQWRkcmVzcz1nZXp1cnVAZ21haWwuY29tCiAgICAgICAgU3ViamVjdCBQdWJsaWMgS2V5IEluZm86' + 'CiAgICAgICAgICAgIFB1YmxpYyBLZXkgQWxnb3JpdGhtOiByc2FFbmNyeXB0aW9uCiAgICAgICAgICAgICAgICBQdWJsaWMt' + 'S2V5OiAoMTAyNCBiaXQpCiAgICAgICAgICAgICAgICBNb2R1bHVzOgogICAgICAgICAgICAgICAgICAgIDAwOmQwOjVmOmQ1' + 'OmE2Ojg5OjQ3OmNiOmYwOmI2OmEyOmM4OjI3OjlmOjA0OgogICAgICAgICAgICAgICAgICAgIGE3OjU3OjRjOjdkOjIwOjk5' + 'OjIyOjJkOjIzOjYyOjIzOmQzOjliOjM4OmMwOgogICAgICAgICAgICAgICAgICAgIGI2OjAxOjNmOjBmOjQ2OjE0OmFmOjk3' + 'OmNmOmE2OjFiOmY2OmY0OjllOmM3OgogICAgICAgICAgICAgICAgICAgIDRlOmU2OmU2OjkxOjk3Ojk5OjU4OjMxOjBhOmNj' + 'OjQwOjQ5OmI0OjZhOmZjOgogICAgICAgICAgICAgICAgICAgIGRmOmJjOjBmOmIzOjQ5OmM1OjBiOjY1OmFiOmFiOjljOjE3' + 'Ojg0Ojg0OmIwOgogICAgICAgICAgICAgICAgICAgIGJlOmVhOjRiOjczOmE0OmQyOmIwOmMwOjEyOjM0OjdmOjNhOmIwOmJk' + 'OjBiOgogICAgICAgICAgICAgICAgICAgIDFhOmU1Ojg0OjIyOjY2OmUxOjI2OmI1OjQzOmQ3OjUxOmJlOjcxOmUxOjZiOgog' + 'ICAgICAgICAgICAgICAgICAgIDk5OmM3OjQ3OjdkOjBkOmMxOjgzOjFjOjZjOmM0Ojg1OmE0OmU5OjA5OmFkOgogICAgICAg' + 'ICAgICAgICAgICAgIDQ0OmRlOjBiOjRiOjM0OmY4OjhmOmY2OmZmCiAgICAgICAgICAgICAgICBFeHBvbmVudDogNjU1Mzcg' + 'KDB4MTAwMDEpCiAgICAgICAgWDUwOXYzIGV4dGVuc2lvbnM6CiAgICAgICAgICAgIFg1MDl2MyBCYXNpYyBDb25zdHJhaW50' + 'czogCiAgICAgICAgICAgICAgICBDQTpGQUxTRQogICAgICAgICAgICBOZXRzY2FwZSBDb21tZW50OiAKICAgICAgICAgICAg' + 'ICAgIE9wZW5TU0wgR2VuZXJhdGVkIENlcnRpZmljYXRlCiAgICAgICAgICAgIFg1MDl2MyBTdWJqZWN0IEtleSBJZGVudGlm' + 'aWVyOiAKICAgICAgICAgICAgICAgIDNEOjVCOjI3Ojc4OjdGOjMwOjAxOjFEOkMwOjU0OjBEOjk1OkY4OjlGOjc2Ojc1OjQ2' + 'OjYyOjg1Ojg0CiAgICAgICAgICAgIFg1MDl2MyBBdXRob3JpdHkgS2V5IElkZW50aWZpZXI6IAogICAgICAgICAgICAgICAg' + 'a2V5aWQ6NDY6REY6QTI6OTI6MEY6Mjc6RUI6NTE6RDQ6NzE6RkM6QUI6N0Y6REI6M0M6MzU6NUU6OTg6RjU6ODMKCiAgICBT' + 'aWduYXR1cmUgQWxnb3JpdGhtOiBzaGExV2l0aFJTQUVuY3J5cHRpb24KICAgICAgICAgMmQ6ODk6OWM6YmE6OGM6NWI6MTU6' + 'MzA6ZTk6OGY6ODA6ODA6YzI6OWU6OWY6ZTY6Zjg6YmU6CiAgICAgICAgIDk3OmJmOmUyOjczOjkwOjZiOjFiOjA2OjIxOjFj' + 'Ojk3OjJhOjBhOjNlOmRjOmVkOjZjOjI4OgogICAgICAgICA4ZDpmMDplMzo4NToyYjo1OToxZjo2MDphODphNzo0MDpkYjo2' + 'Mjo5NzoxYzpjNTphZDo3OToKICAgICAgICAgYzM6ZmI6NzA6Mzk6ZTI6NTg6ZTE6NmI6ZjU6YTk6Y2I6NzU6ZTA6MTI6YmU6' + 'Y2M6YWQ6Mjg6CiAgICAgICAgIGRlOmM0OjIzOmMyOmZjOjllOjU1OmYwOjlhOmIxOmI5OmFlOjkyOjQzOjUxOjAzOmFkOmU2' + 'OgogICAgICAgICA1OTo5Mjo3MzpiZTplNjo2ZDpmMzo0NDozMTo3MTpjMDo3Nzo1MjozZjphNjo2Mjo1YzpkODoKICAgICAg' + 'ICAgOWM6ZWU6OWQ6YjI6NGQ6MWY6YWM6MjI6MmY6M2Q6YWM6NDI6MjU6YTM6NTU6ZDk6Y2Y6ZjY6CiAgICAgICAgIGJkOmI0' + 'Ci0tLS0tQkVHSU4gQ0VSVElGSUNBVEUtLS0tLQpNSUlDK3pDQ0FtU2dBd0lCQWdJQkR6QU5CZ2txaGtpRzl3MEJBUVVGQURD' + 'QmdURVFNQTRHQTFVRUNoTUhSMjl5CmNtbHZiakVrTUNJR0NTcUdTSWIzRFFFSkFSWVZjRzl6ZEcxaGMzUmxja0JuYjNKeWFX' + 'OXVMbU5vTVJBd0RnWUQKVlFRSEV3ZFBZbVZ5ZDJsc01RNHdEQVlEVlFRSUV3VkNZWE5sYkRFTE1Ba0dBMVVFQmhNQ1EwZ3hH' + 'REFXQmdOVgpCQU1URDBkdmNuSnBiMjRnVW05dmRDQkRRVEFlRncweE16QTBNak14T0RRNE5ERmFGdzB4TmpBME1qSXhPRFE0' + 'Ck5ERmFNSUdITVFzd0NRWURWUVFHRXdKRFNERU9NQXdHQTFVRUNCTUZRbUZ6Wld3eEVEQU9CZ05WQkFvVEIwZHYKY25KcGIy' + 'NHhEekFOQmdOVkJBc1RCbkI1ZUhSeVlURWtNQ0lHQTFVRUF4TWJSR0Z1YVd4dklFSmhjbWRsYml3ZwpVR1YwWlhJZ1RXRnVj' + 'MlZ5TVI4d0hRWUpLb1pJaHZjTkFRa0JGaEJuWlhwMWNuVkFaMjFoYVd3dVkyOXRNSUdmCk1BMEdDU3FHU0liM0RRRUJBUVVB' + 'QTRHTkFEQ0JpUUtCZ1FEUVg5V21pVWZMOExhaXlDZWZCS2RYVEgwZ21TSXQKSTJJajA1czR3TFlCUHc5R0ZLK1h6NlliOXZT' + 'ZXgwN201cEdYbVZneENzeEFTYlJxL04rOEQ3Tkp4UXRscTZ1YwpGNFNFc0w3cVMzT2swckRBRWpSL09yQzlDeHJsaENKbTRT' + 'YTFROWRSdm5IaGE1bkhSMzBOd1lNY2JNU0ZwT2tKCnJVVGVDMHMwK0kvMi93SURBUUFCbzNzd2VUQUpCZ05WSFJNRUFqQUFN' + 'Q3dHQ1dDR1NBR0crRUlCRFFRZkZoMVAKY0dWdVUxTk1JRWRsYm1WeVlYUmxaQ0JEWlhKMGFXWnBZMkYwWlRBZEJnTlZIUTRF' + 'RmdRVVBWc25lSDh3QVIzQQpWQTJWK0o5MmRVWmloWVF3SHdZRFZSMGpCQmd3Rm9BVVJ0K2lrZzhuNjFIVWNmeXJmOXM4TlY2' + 'WTlZTXdEUVlKCktvWklodmNOQVFFRkJRQURnWUVBTFltY3VveGJGVERwajRDQXdwNmY1dmkrbDcvaWM1QnJHd1loSEpjcUNq' + 'N2MKN1d3b2pmRGpoU3RaSDJDb3AwRGJZcGNjeGExNXcvdHdPZUpZNFd2MXFjdDE0QksrekswbzNzUWp3dnllVmZDYQpzYm11' + 'a2tOUkE2M21XWkp6dnVadDgwUXhjY0IzVWorbVlselluTzZkc2swZnJDSXZQYXhDSmFOVjJjLzJ2YlE9Ci0tLS0tRU5EIENF' + 'UlRJRklDQVRFLS0tLS0K' 
class _name0x3 (  urllib2.HTTPSHandler )  : 
    def __init__ (  name0x4 , name0x5 , name0x6 )  : 
        urllib2.HTTPSHandler.__init__ (  name0x4 )  
        name0x4.name0x5 = name0x5 
        name0x4.name0x6 = name0x6 
    def https_open (  name0x4 , name0x7 )  : 
        return name0x4.do_open (  name0x4.name0x8 , name0x7 )  
    def name0x8 (  name0x4 , name0x9 , timeout = 300 )  : 
        return httplib.HTTPSConnection (  name0x9 , key_file = name0x4.name0x5 , cert_file = name0x4.name0x6 )  
class GorrionError (  Exception )  : 
    pass 
class GorrionService (  object )  : 
    def get_captcha (  name0x4 , name0xa )  : 
        name0xb = name0x4._name0xc (  )  
        try : 
            name0xd = name0xb.open (  '%s&token=%s' % (  _name0x0 , name0xa )  )  . read (  )  
        except urllib2.HTTPError : 
            raise GorrionError (  'Could not connect to anticaptcha service.' )  
        if name0xd.startswith (  'Captcha: ' )  : 
            name0xe = name0xd.replace (  'Captcha: ' , '' )  
        else : 
            raise GorrionError (  'Anticaptcha service returns invalid reply.' )  
        if name0xe == 'std::exception' : 
            raise GorrionError (  'Anticaptcha service returned an exception. ' + 'Invalid or expired token?' )  
        return name0xe 
    def report (  name0x4 , name0xe , name0xf )  : 
        if isinstance (  name0xe , str )  : 
            name0xb = name0x4._name0xc (  )  
            if name0xf not in [ 0 , 1 ] : 
                raise GorrionError (  'Success value must be 0 or 1.' )  
            try : 
                name0xb.open (  '%s&validcaptcha=%s&success=%u' % (  _name0x0 , name0xe , name0xf )  )  
            except urllib2.URLError : 
                raise GorrionError (  'Could not report to anticaptcha service.' )  
        else : 
            raise GorrionError (  'Captcha must be a string' )  
    def _name0xc (  name0x4 )  : 
        name0x4.name0x10 = tempfile.NamedTemporaryFile (  )  
        name0x4.name0x10.write (  base64.b64decode (  _name0x1 )  )  
        name0x4.name0x10.flush (  )  
        name0x4.name0x11 = tempfile.NamedTemporaryFile (  )  
        name0x4.name0x11.write (  base64.b64decode (  _name0x2 )  )  
        name0x4.name0x11.flush (  )  
        try : 
            name0x12 = name0x4.name0x10.name 
            name0x13 = name0x4.name0x11.name 
            name0xb = urllib2.build_opener (  _name0x3 (  name0x12 , name0x13 )  )  
        except urllib2.URLError : 
            raise GorrionError (  'Could not connect to anticaptcha service.' )  
        else : 
            return name0xb 
