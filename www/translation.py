import os
import configparser

ini = None

def use(path=None,encoding='iso-8859-1'):
    global ini
    if path is None:
        path = os.path.join(THIS.root_dir,'translations.ini')
    else:
        path = THIS.abs_path(path)
    ini = configparser.ConfigParser()
    try:
        ini.read([path],encoding=encoding)
    except TypeError:
        ini.read([path]) # encoding is not supported by Python3.1
    return ini

def translate(src):
    if not ini.has_section(src):
        return src
    langs = REQUEST_HEADERS.get('Accept-language').split(',')
    for lang in langs:
        lang = lang.split(';')[0]
        lang = lang.split('-')[0]
        try:
            return ini.get(src,lang)
        except configparser.NoOptionError:
            continue
    try:
        return ini.get(src,'default')
    except configparser.NoOptionError:
        return src 

use()