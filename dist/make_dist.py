import os
import tarfile
import Karrigell

name = 'Karrigell-{}'.format(Karrigell.version)
dist = tarfile.open(name+'.gz',mode='w:gz')

parent = os.path.dirname(os.getcwd())

for path in ['README.txt','MANIFEST','setup.py']:
    dist.add(os.path.join(parent,'trunk',path),
        arcname=os.path.join(name,path))

for path in ['Karrigell','HTMLTags']:
    abs_path = os.path.join(parent,'trunk',path)
    for (dirpath,dirnames,filenames) in os.walk(abs_path):
        exclude = [ d for d in dirnames if d[0] in '._' ]
        for d in exclude:
            dirnames.remove(d)
        for filename in filenames:
            print('add',filename)
            dist.add(os.path.join(dirpath,filename),
                arcname=os.path.join(name,path,filename))

# admin tools,cgi,wsgi
folders = ['www','cgi','wsgi',os.path.join('www','admin')]
for folder in folders:
    folder_abs = os.path.join(parent,folder)
    for path in os.listdir(folder_abs):
        if not os.path.isfile(os.path.join(folder_abs,path)):
            continue
        if os.path.splitext(path)[1] in ['.sqlite']:
            continue
        print('add',path)
        dist.add(os.path.join(folder_abs,path),
            arcname=os.path.join(name,folder,path))

dist.close()
