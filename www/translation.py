"""Simple translation engine

Translations are saved in a text file of this format :
[key](...string to translate...)
[fr](...translation in French...)
[it](...translation in Italian...)
[default](...optional default translation...)
(...optional blank lines between translations ...)


A script can import this module by
_ = Import('trad.py').translate

When the script call the function _(source), the function searches if source
is present as [key] in the translation file

If so :
- if one of the translations matches one of the Accept-language headers 
defined in the user's browser, returns it
- else, if a default translation is present, returns it
- else return the source

If no match is found, the function returns the argument

The parameters to define are the path of the translation file and its encoding
"""
import os
import re

path = os.path.join(THIS.root_dir,'translations.txt')
encoding = 'iso-8859-1'

def translate(src):
    try:
        dico = open(path,encoding=encoding)
    except IOError:
        # no translation file : return src
        return src
    while True:
        lang = None
        line = dico.readline()
        if not line: #EOF
            return src
        line = line.rstrip()
        if line=="[key]"+src:
            trad = {} # dictionary built from the translation file
            while True:
                line = dico.readline()
                if not line:
                    break
                line = line.rstrip()
                mo = re.search(r'^\[(.*?)\](.*)$',line)
                if mo:
                    lang = mo.groups()[0]
                    if lang=="key": # next key
                        break
                    trad[lang] = mo.groups()[1]
                elif lang:
                    trad[lang] += '\n'+line
            langs = REQUEST_HEADERS.get('Accept-language').split(',')
            for lang in langs:
                lang = lang.split(';')[0]
                lang = lang.split('-')[0]
                if lang in trad:
                    return trad[lang]
            print(trad)
            if 'default' in trad:
                return trad['default']
            return src
    return src
