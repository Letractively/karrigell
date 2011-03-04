import os
import urllib.parse

script_strings = Import('script_strings.py')

Login("admin")
ENCODING = "utf-8"

header = HEAD(
    LINK(rel="stylesheet",href="../style.css")+
    META(http_equiv="Content-Type",content="text/html; charset=utf-8")
    )

def index(script):
    script1 = urllib.parse.unquote(script)
    name = os.path.basename(script1)
    ext = os.path.splitext(script1)[1]
    if ext in [".py"]:
        strings = script_strings.get_strings(script1)
    list_langs = ACCEPTED_LANGUAGES.split(",")
    langs = []
    for lang in list_langs:
        lang1 = lang.split(";")[0][:2]
        if not lang1 in langs:
            langs.append(lang1)

    lines = [TR(TH(_("In script"))+Sum([TH(lang) for lang in langs]))]
    for i,_string in enumerate(strings):
        _string1 = _string.replace('"','&quot;')
        line = TD(_string)+INPUT(Type="hidden",name="orig-%s" %i,value=_string1)
        for lang in langs:
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
    
    explain = H3(_("Translating strings in %s") %name)
    explain += I(_('Strings in italic have no translation yet. '))
    explain += _('Enter your translation and save changes')
    
    form = FORM(action="update",method="post")
    form <= TABLE(Sum(lines),Id="hor-minimalist-b")
    form <= INPUT(Type="hidden",name="script",value=script)
    form <= INPUT(Type="submit",value=_("Save translations"))
    return HTML(header+BODY(explain+form))

def update(**kw):
    script = kw['script']
    del kw['script']
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

    body = _("Translations saved")
    body += BR()+A(_("Back"),href="index?script="+script)
    return HTML(header+BODY(body))

