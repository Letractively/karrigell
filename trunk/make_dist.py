import os
import tarfile
import Karrigell

name = 'Karrigell-{}'.format(Karrigell.version)
dist_dir = os.path.join(os.path.dirname(os.getcwd()),'dist')
if not os.path.exists(dist_dir):
    os.mkdir(dist_dir)
dist = tarfile.open(os.path.join(dist_dir,name+'.gz'),mode='w:gz')

for path in ['README.txt','MANIFEST','setup.py']:
    dist.add(path,arcname=os.path.join(name,path))

for path in ['Karrigell','HTMLTags']:
    for (dirpath,dirnames,filenames) in os.walk(path):
        exclude = [ d for d in dirnames if d[0] in '._' ]
        for d in exclude:
            dirnames.remove(d)
        for filename in filenames:
            print('add',filename)
            dist.add(os.path.join(dirpath,filename),
                arcname=os.path.join(name,path,filename))

# admin tools,cgi,wsgi
folders = ['admin_tools','cgi','wsgi']
for folder in folders:
    folder_abs = os.path.join(os.path.dirname(os.getcwd()),folder)
    for path in os.listdir(folder_abs):
        if not os.path.isfile(os.path.join(folder_abs,path)):
            continue
        if os.path.splitext(path)[1] in ['.sqlite']:
            continue
        print('add',path)
        dist.add(os.path.join(folder_abs,path),
            arcname=os.path.join(name,folder,path))

dist.close()
