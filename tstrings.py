from codecs import open
from re import compile
from copy import copy
import urllib
import codecs
import json
import sys
import os
import argparse

#globals for regex
re_translation = compile(r'^"(.+)" = "(.+)";$')
re_comment_single = compile(r'^/\*.*\*/$')
re_comment_start = compile(r'^/\*.*$')
re_comment_end = compile(r'^.*\*/$')
SPEECH=chr(34)

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


class LocalizedString():
    def __init__(self, comments, translation):
        self.comments, self.translation = comments, translation
        self.key, self.value = re_translation.match(self.translation).groups()

    def __unicode__(self):
        return u'%s%s\n' % (u''.join(self.comments), self.translation)

class LocalizedFile():
    def __init__(self, translator,fname=None, auto_read=False,source="en",dest="fr"):
        self.fname = fname
        self.strings = []
        self.strings_d = {}
        self.translator=translator
        self.source=source
        self.dest=dest
		
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
            translatedstring=self.translator(string.value,self.source,self.dest)
            for c in comments:
            	self.strings.append(c)
            #I'm not sure at this time of night how to migrate the regex symbols across but lucky I know what they are :-P
            self.strings.append(SPEECH + string.key + SPEECH + " = " + SPEECH + translatedstring + SPEECH+'\n')
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
            f.write(string)

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

def main():
    parser = argparse.ArgumentParser(description='A damn sinmple .strings translator so we can observe other languages with mildy accurate information. ',
    epilog="Yes.. it's a pile of steaming,smelly hacks :-)")

    parser.add_argument('-i',help='Input file',required=True)
    parser.add_argument('-o',help='Output file',required=True)
    parser.add_argument('-s',help='Source Langauge (e.g en,fr etc - Check bing (Usually start with en as it is accurate)',required=False,default='en')
    parser.add_argument('-d',help='Dest Language (e.g fr,ko,ru etc -Check bing',required=False,default='fr')
  
    Options = parser.parse_args()
  
    #brads bing id using for translation
    set_app_id('2A9444C210A043010CB9FC4AB8B6DE797AE88790')
    #load in strings file
    LF=LocalizedFile(translate,Options.i,True,Options.s,Options.d)
    LF.save_to_file(Options.o)

#save the translated file as something else
main()
