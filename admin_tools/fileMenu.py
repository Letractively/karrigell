import os
import urllib.parse

script_strings = Import('script_strings.py')

style = LINK(rel="stylesheet",href="../style.css")

def index(base='/'):
    head= HEAD()
    head <= style

    body = A(_("Home"),href="/",target="_top")
    body += BR("Scripts")
        
    table = TABLE(Id="box-table-b")
    
    folder = THIS.get_file(base)
    paths = os.listdir(folder)
    subfolders = [ p for p in paths if os.path.isdir(os.path.join(folder,p)) ]
    for subfolder in subfolders:
        row = TR()
        row <= TD(A(IMG(src="../folder_open.png",border=0),
            href="?base="+urllib.parse.quote(urllib.parse.urljoin(base,subfolder))))
        row <= TD(B(subfolder))
        table <= row

    files = [ p for p in paths if os.path.isfile(os.path.join(folder,p)) ]
    for _file in files:
        abs_path = os.path.join(folder,_file)
        if os.path.splitext(_file)[1] == '.py' \
            and script_strings.get_strings(abs_path):
            cell = A(_file,
                href="../translator.py?script="+urllib.parse.quote(abs_path),
                target="right")
        else:
            cell = _file
        table <= TR(TD('&nbsp;')+TD(cell))

    body += table   
    return HTML(head+BODY(body))
