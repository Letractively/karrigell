import os
import tarfile
import sys

cwd,parent = os.getcwd(),os.path.dirname
k_path = os.path.join(parent(cwd),'trunk')
sys.path.insert(0,k_path)

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
            if filename.lower().endswith('.bat'):
                continue
            print('add',filename)
            dist.add(os.path.join(dirpath,filename),
                arcname=os.path.join(name,path,filename))

# admin tools,cgi,wsgi
folders = ['www','cgi','wsgi',os.path.join('www','admin'),'data','tests']
for folder in folders:
    folder_abs = os.path.join(parent,folder)
    dist.add(os.path.join(parent,folder),arcname=os.path.join(name,folder),
        recursive=False)
    for path in os.listdir(folder_abs):
        if not os.path.isfile(os.path.join(folder_abs,path)):
            continue
        if os.path.splitext(path)[1] in ['.sqlite']:
            continue
        print('add',path)
        dist.add(os.path.join(folder_abs,path),
            arcname=os.path.join(name,folder,path))
dist.close()

# unzip in temporary folder
import tempfile
temp_dir = tempfile.TemporaryDirectory()
print('Unzip in '+temp_dir.name)
src = tarfile.open(name+'.gz')
src.extractall(temp_dir.name)

# install
os.chdir(os.path.join(temp_dir.name,name))
print('Install')
os.system(sys.executable+' setup.py install')
