from sys import argv
from codecs import open
from re import compile
from copy import copy
import urllib
import codecs
import json
import sys
import os

#shitty globals for regex
re_translation = compile(r'^"(.+)" = "(.+)";$')
re_comment_single = compile(r'^/\*.*\*/$')
re_comment_start = compile(r'^/\*.*$')
re_comment_end = compile(r'^.*\*/$')


api_url = "http://api.microsofttranslator.com/V2/Ajax.svc/Translate"
app_id = ''

def _unicode_urlencode(params):
    """
    A unicode aware version of urllib.urlencode.
    Borrowed from pyfacebook :: http://github.com/sciyoshi/pyfacebook/
    """
    if isinstance(params, dict):
        params = params.items()
        return urllib.urlencode([(k, isinstance(v, unicode) and v.encode('utf-8') or v) for k, v in params])


def _run_query(args):
    """
    takes arguments and optional language argument and runs query on server
    """
    data = _unicode_urlencode(args)
    sock = urllib.urlopen(api_url + '?' + data)
    result = sock.read()
    if result.startswith(codecs.BOM_UTF8):
        result = result.lstrip(codecs.BOM_UTF8).decode('utf-8')
    elif result.startswith(codecs.BOM_UTF16_LE):
        result = result.lstrip(codecs.BOM_UTF16_LE).decode('utf-16-le')
    elif result.startswith(codecs.BOM_UTF16_BE):
        result = result.lstrip(codecs.BOM_UTF16_BE).decode('utf-16-be')
    return json.loads(result)

def set_app_id(new_app_id):
    global app_id
    app_id = new_app_id

def translate(text, source, target, html=False):
    """
    action=opensearch
    """
    if not app_id:
        raise ValueError("AppId needs to be set by set_app_id")

    query_args = {
    'appId': app_id,
    'text': text,
    'from': source,
    'to': target,
    'contentType': 'text/plain' if not html else 'text/html',
    'category': 'general'
    }
    return _run_query(query_args)



	#SHITTTTT Google translate is paid only



"""
	#SHITTTTT Google translate is paid only
class Translate(object):
  

    def __init__(self):
        super(Translate, self).__init__()
        self.langs = ["af", "sq", "ar", "be", "bg", "ca", "zh-CN", "zh-TW",
        "hr", "cs", "da", "nl", "en", "et", "tl", "fi", "fr",
        "gl", "de", "el", "ht", "iw", "hi", "hu", "is", "id",
        "ga", "it", "ja", "lv", "lt", "mk", "ms", "mt", "no",
        "fa", "pl", "pt", "ro", "ru", "sr", "sk", "sl", "es",
         "sw", "sv", "th", "tr", "uk", "vi", "cy", "yi"]
         
        self.API_KEY = "AIzaSyC5wXV9B15WaWQ08qMDD-0O-ZihSnbpi48"
        self.API_URL = "https://www.googleapis.com/language/translate/v2?\key=%s&q=%s&source=%s&target=%s&prettyprint=false"

        self.uri = self.API_URL


    def translate(self, params):
        #Translates texts
         #      keywords:
          #     params - Dictionary
           #    src_text - String
            #   src_lang - 2 letter iso code for language
             #  dest_lang - 2 letter iso code for language
       
    
        
        req_uri = self.uri % (self.API_KEY, urllib2.quote(params['src_text']),
        params['src_lang'],
        params['dest_lang'])

        hdl = urllib2.urlopen(req_uri)
        resp = hdl.read()
        hdl.close()
        j = json.loads(resp)
        try:
            return j['data']['translations'][0]['translatedText']
        except TypeError:
            return "Failed to translate"
"""        


class LocalizedString():
    def __init__(self, comments, translation):
        self.comments, self.translation = comments, translation
        self.key, self.value = re_translation.match(self.translation).groups()

    def __unicode__(self):
        return u'%s%s\n' % (u''.join(self.comments), self.translation)

class LocalizedFile():
    
    
    def __init__(self, fname=None, auto_read=False):
        self.fname = fname
        self.strings = []
        self.strings_d = {}

        if auto_read:
            self.read_from_file(fname)

    def read_from_file(self, fname=None):
        fname = self.fname if fname == None else fname
        try:
            f = open(fname, encoding='utf_8', mode='r')
        except:
            print 'File %s does not exist.' % fname
            exit(-1)

        line = f.readline()
        while line:
            comments = [line]

            if not re_comment_single.match(line):
                while line and not re_comment_end.match(line):
                    line = f.readline()
                    comments.append(line)

            line = f.readline()
            if line and re_translation.match(line):
                translation = line
            else:
                raise Exception('invalid file')

            line = f.readline()
            while line and line == u'\n':
                line = f.readline()

            string = LocalizedString(comments, translation)
            self.strings.append(string)
            self.strings_d[string.key] = string

        f.close()

    def save_to_file(self, fname=None):
        fname = self.fname if fname == None else fname
        try:
            f = open(fname, encoding='utf_8', mode='w')
        except:
            print 'Couldn\'t open file %s.' % fname
            exit(-1)

        for string in self.strings:
            f.write(string.__unicode__())

        f.close()

    def merge_with(self, new):
        merged = LocalizedFile()

        for string in new.strings:
            if self.strings_d.has_key(string.key):
                new_string = copy(self.strings_d[string.key])
                new_string.comments = string.comments
                string = new_string

            merged.strings.append(string)
            merged.strings_d[string.key] = string

        return merged
        
#load in strings file
LF=LocalizedFile("demo.strings",True)
set_app_id('2A9444C210A043010CB9FC4AB8B6DE797AE88790')
for k in LF.strings_d:
	#get current value
	text=LF.strings_d[k].value
	#prepare translation request
	"""
	# src_text - String
               src_lang - 2 letter iso code for language
               dest_lang - 2 letter iso code for langu
    """
	#trequest={"src_text": text,
    #          "src_lang": "en",
    #          "dest_lang": "fr"}
	#translate
	print translate(text,"en","fr")
    #update the dictionary with the translated value

#save the translated file as something else

