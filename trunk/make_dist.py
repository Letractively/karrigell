import os
import tarfile
import Karrigell

name = 'Karrigell-{}'.format(Karrigell.version)
dist = tarfile.open(os.path.join('dist',name+'.gz'),mode='w:gz')

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

# admin tools
for (dirpath,dirnames,filenames) in os.walk(os.path.join(os.path.dirname(os.getcwd()),'admin_tools')):
    exclude = [ d for d in dirnames if d[0] in '._' ]
    for d in exclude:
        dirnames.remove(d)
    for filename in [ f for f in filenames 
        if not os.path.splitext(f)[1] in ['.sqlite'] ]:
        print('add',filename)
        dist.add(os.path.join(dirpath,filename),
            arcname=os.path.join(name,'admin_tools',path,filename))

dist.close()
