Login("admin")

import os
import html
import urllib.parse

banner = Import('banner.py')
script_strings = Import("script_strings.py")
lang_list = Import("langs.py")

head = HEAD(
    LINK(rel="stylesheet",href="../style.css")+
    META(http_equiv="Content-Type",content="text/html; charset=utf-8")
    )

def index(url_path='/'):
    # url path is unquoted
    head <= TITLE('Karrigell - '+_('Administration tools'))
    container = DIV(Id="container")
    container <= banner.banner(home=True,title=_('Translations'))
    
    if THIS.translation_db is None:
        content = DIV(style="padding:50px;")
        content <= H3("No translation database set")
        container <= content
        return HTML(head+BODY(container))

    elts = url_path.lstrip('/').split('/')

    links = A("..",href="?")+' / '
    for (i,elt) in enumerate(elts[:-1]):
        address = '/'.join(elts[:i+1])
        address = urllib.parse.quote_plus(address)
        links += A(elt or '..',href="index?url_path=/"+address)+ '/ '
    links += B(elts[-1])            
    container <= links

    table = TABLE(Id="navig")
    fs_path = THIS.get_file(url_path)
    if os.path.isdir(fs_path):
        folder = fs_path
        url_path = url_path.rstrip('/')+'/'
    else:
        folder = os.path.dirname(fs_path)
    paths = os.listdir(folder)
    subfolders = [ p for p in paths if os.path.isdir(os.path.join(folder,p)) ]
    for subfolder in subfolders:
        sub_url = urllib.parse.urljoin(url_path,subfolder)
        row = TR()
        row <= TD(A(IMG(src="../folder_open.png",border=0),
            href="?url_path="+urllib.parse.quote_plus(sub_url)))
        row <= TD(B(subfolder))
        table <= row

    files = [ p for p in paths if os.path.isfile(os.path.join(folder,p)) ]
    for _file in files:
        abs_path = os.path.join(folder,_file)
        if os.path.splitext(_file)[1] == '.py' \
            and script_strings.get_strings(abs_path):
            sub_path = urllib.parse.urljoin(url_path,_file)
            sub_path = urllib.parse.quote_plus(sub_path)
            cell = A(_file,href="?url_path={}".format(sub_path))
        else:
            cell = _file
        table <= TR(TD('&nbsp;')+TD(cell))

    content = TABLE()
    row = TR()
    row <= TD(table,valign="top")

    if os.path.isfile(fs_path):
        row <= TD(_translator(url_path,fs_path),Class="translation")
    content <= row
    container <= content
    return HTML(head+BODY(container))

def _translator(url_path,script):
    name = os.path.basename(script)
    ext = os.path.splitext(script)[1]
    if ext in [".py"]:
        strings = script_strings.get_strings(script)
    langs = ACCEPTED_LANGUAGES
    if not langs:
        return _("You must select the language in your browser")
    # select prefered language form browser preferences
    lang = langs.split(",")[0].split(";")[0][:2]

    header = TR()
    header <= TH(_("Original string in script"))
    lang_str = lang
    if lang in lang_list.langs:
        lang_str += ' ({})'.format(lang_list.langs[lang])
    header <= TH(_('Translation into')+'&nbsp;'+lang_str)
    lines = [header]
    for i,_string in enumerate(strings):
        _string1 = html.escape(_string,quote=True)
        line = TD(_string)+INPUT(Type="hidden",name="orig-%s" %i,value=_string1)
        _trans = THIS.translation_db.get_translation(_string,lang)
        if _trans is None:
            _input = TEXTAREA(_string,name="%s-%s" %(lang,i),
                    cols=35,rows=1+len(_string1)/25,
                    style="font-style:italic;")
        else:
            _trans = _trans.replace('"','&quot;')
            _input = TEXTAREA(_trans,name="%s-%s" %(lang,i),
                    cols=35,rows=1+len(_string1)/25)
        line += TD(_input)
        lines += [TR(line)]
    
    explain = I(_('Strings in italic have no translation yet. '))+BR()
    explain += _('To change the language, update your browser languages list')
    
    form = FORM(action="update",method="post")
    form <= TABLE(Sum(lines),Id="hor-minimalist-b")
    form <= INPUT(Type="hidden",name="url_path",value=url_path)
    form <= INPUT(Type="submit",value=_("Save translations"))
    return explain+form

def update(**kw):
    url_path = kw['url_path']
    del kw['url_path']
    dico = {}
    for k,v in kw.items():
        lang,num = k.split("-")
        if not num in dico:
            dico[num]={lang:v}
        else:
            dico[num][lang] = v

    for num in dico:
        original = dico[num]['orig']
        for language in [ lang for lang in dico[num] if lang != 'orig' ]:
            THIS.translation_db.set_translation(original,language,
                dico[num][language])
    raise HTTP_REDIRECTION("index?url_path="+url_path)

