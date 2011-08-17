import os
import configparser
path = os.path.join(THIS.root_dir,'translations.ini')
encoding = 'iso-8859-1'
ini = configparser.ConfigParser()
ini.read([path],encoding=encoding)

def translation(src):
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