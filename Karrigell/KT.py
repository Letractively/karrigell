"""KT -- Karrigell Template

Provides a means of performing substitutions and translations in templates
stored in separate files. Template files are referenced by urls, following the 
same conventions as the Import statement. Templates can include other templates.

Template syntax:

@[template_url]
  include template referenced by template_url]
    
#[string_to_translate]
  apply standard Karrigell string translation to string_to_translate
    
$identifier
  subtitute the value of identifier
    
These combinations are also possible:

@[$template_url]
#[$string]

Usage:
text = KT(template_url, id1=val1, id2=val2, ...)
  or    
text = KT(template_url, **data)
  where data is a dictionary of values to substitute.

Encoding management
===================
The contents of the files managed by KT are supposed to be bytestrings
encoded with the encoding defined by SET_UNICODE_OUT()

If they are encoded with another encoding, you can specify it with :
    KT(template_url,encoding=foo)

All the included urls in this template are supposed to be also encoded with
this encoding. If some of them are encoded with a different encoding their
encoding must be specified after the included url name :
@[included_url,encoding]
"""

import urllib.parse
import re

class RecursionError(Exception):
    pass

class NotFoundError(Exception):
    pass

class KTError(Exception):
    pass

def _log(*data):
    import sys
    for item in data:
        sys.stderr.write('%s\n' %item)

class action:
    def __init__(self, handler):
        self.handler = handler
        self.included_urls = set()
    
    def __call__(self,tmpl_url,encoding='utf-8',**namespace):
        self.encoding = encoding
        abs_url = self.handler.abs_url(tmpl_url)
        fs_path = self.handler.get_file(abs_url)
        with open(fs_path,encoding=encoding,errors='replace') as fileobj:
            templ = fileobj.read()               
        templ = self._include(templ, namespace, abs_url)
        templ = self._substitute(templ, namespace)
        data = self._translate(templ)
        return data

    def _include(self, text, namespace, parent_url):
        regex = re.compile(r"""
            \@(?:
                (?P<escaped>\@)                     | # Escape sequence of two delimiters
                \[(?P<id>\$[_a-z][_a-z0-9\.]*)\]    | # a bracketed Python identifier
                \[(?P<url>.*?[^\\])\]               | # a bracketed url
                (?P<invalid>)                         # Other ill-formed delimiter exprs
            )
            """, re.IGNORECASE | re.VERBOSE)
        def helper(mo):
            if mo.group('escaped') is not None:
                return mo.group(0)
            url = ''
            if mo.group('id') is not None:
                id = str(mo.group('id'))
                url = self._substitute(id, namespace)
                # if id has no value, don't attempt to open the url.
                if not url or url==id:
                    return ''
            if mo.group('url') is not None:
                url = str(mo.group('url'))
            if url:
                encoding = self.encoding
                if ',' in url:
                    url,encoding = url.split(',',1)
                abs_url = urllib.parse.urljoin(parent_url, url)
                if abs_url in self.included_urls:
                    raise RecursionError("Circular reference to template %s in %s" % (abs_url, parent_url))
                else:
                    self.included_urls.add(abs_url)
                try:
                    fs_path = self.handler.get_file(abs_url)
                except:
                    raise NotFoundError('No file at url %s' %abs_url)
                with open(fs_path,encoding=encoding,errors='replace') as fileobj:
                    inclusion = fileobj.read()
                return self._include(inclusion, namespace, abs_url)
            if mo.group('invalid') is not None:
                return mo.group(0)
        return regex.sub(helper, text)
        
    def _substitute(self, text, namespace):
        delimiter = '$'
        regex = re.compile(r"""
            \$(?:
              (?P<escaped>\$)                                             |  # Escape sequence of two delimiters
              (?P<container>[_a-z][_a-z0-9]*)\.(?P<attr>[_a-z][_a-z0-9]*) |  # a container  with attribute                     
              (?P<named>[_a-z][_a-z0-9]*)                                 |  # a Python identifier
              (?P<invalid>)                                                  # Other ill-formed delimiter exprs
            )
            """, re.IGNORECASE | re.VERBOSE | re.UNICODE)
        def helper(mo):
            named = mo.group('named')
            if named is not None:
                try:
                    res = namespace[named]
                except KeyError:
                    return delimiter + named
                # make sure res is a string (8-bit or unicode) and not an instance. 
                res = '%s' % res  
                ### Not sure this kind of processing is required. Seems to works better
                ### when commented out! 
                # Convert to requested encoding if required 
                #~ if self.encoding != self.handler.encoding:
                    #~ encoded = res.encode(self.handler.encoding)
                    #~ try:
                        #~ res = encoded.decode(self.encoding)
                    #~ except UnicodeDecodeError as msg:
                        #~ msg = 'Warning: error trying to encode translation %s to %s' \
                                #~ %(res,self.encoding)
                        #~ print(msg)
                return res            
            container = mo.group('container')
            if container is not None:
                if not container in namespace:
                    return mo.group(0)
                obj = namespace[container]
                attr = mo.group('attr')
                try:
                    res = getattr(obj, attr)
                except AttributeError:
                    try:
                        res = obj[attr]
                    except:
                        res = mo.group(0)
                # make sure res is a string (8-bit or unicode) and not an instance. 
                res = '%s' % res
                ### Not sure this kind of processing is required. Seems to works better
                ### when commented out! 
                #~ # Convert to requested encoding if required 
                #~ if self.encoding != self.handler.encoding:
                    #~ encoded = res.encode(self.handler.encoding)
                    #~ try:
                        #~ res = encoded.decode(self.encoding)
                    #~ except UnicodeDecodeError as msg:
                        #~ msg = 'Warning: error trying to encode translation %s to %s' \
                                #~ %(res,self.encoding)
                        #~ print(msg)
                return res            
            if mo.group('escaped') is not None:
                return delimiter
            if mo.group('invalid') is not None:
                return delimiter
        return regex.sub(helper, text)

    def _translate(self, text):
        regex = re.compile(r"""
            _(?:
                (?P<escaped>_)                 |   # Escape sequence of two delimiters
                \[(?P<string>.*?[^\\])\]       |   # a bracketed string to translate
                (?P<invalid>)                      # Other ill-formed delimiter exprs
            )
            """, re .IGNORECASE | re.VERBOSE)
        def helper(mo):
            if mo.group('escaped') is not None:
                return mo.group(0)
            if mo.group('string') is not None:
                val = str(mo.group('string')).replace('\]', ']')
                res = self.handler.translation(val)
                
                ### Not sure this kind of processing is required. Seems to works better
                ### when commented out! 
                # If there was a translation then it is encoded with the handler's encoding.
                # Try to convert it to the requested encoding. If conversion fails, print a 
                # warning and pass the original value.
                #~ if res != val and self.encoding != self.handler.encoding:
                    #~ encoded = res.encode(self.handler.encoding)
                    #~ try:
                        #~ res = encoded.decode(self.encoding)
                    #~ except UnicodeDecodeError as msg:
                        #~ msg = 'Warning: error trying to encode translation %s to %s' \
                                #~ %(res,self.encoding)
                        #~ print(msg)
                            
                return res
            if mo.group('invalid') is not None:
                return mo.group(0)
        return regex.sub(helper, text)
    
    def get_strings(self, script):
        regex = re.compile(r'_\[(.*?[^\\])\]')
        f = open(script, 'r')
        res = []
        for line in f.readlines():
            found = regex.findall(line)
            for _string in found:
                if _string not in res:
                    res.append(_string)
        f.close()
        return res

