import os
import re
import shutil
import urllib.request

proxy_handler = urllib.request.ProxyHandler(proxies={'http':'http://p-goodway.rd.francetelecom.fr:3128'})
opener = urllib.request.build_opener(proxy_handler)

url = "http://code.google.com/p/karrigell/w/list"
req = opener.open(url)
src = req.read().decode('utf-8')
pages = []
for mo in re.finditer('(?s)<td class="vt id col_0"><a href="/p/karrigell/wiki/(.*?)">(.*?)</a></td>',src):
    pages.append(mo.groups()[0])

if os.path.exists('html'):
    shutil.rmtree('html')
os.mkdir('html')
os.mkdir(os.path.join('html','images'))

for path in ['wiki.css','prettify.js']:
    shutil.copyfile(path,os.path.join('html',path))
for path in os.listdir('images'):
    shutil.copyfile(os.path.join('images',path),
        os.path.join('html','images',path))
        
for page in pages:
    print(page,'...')
    url = "http://code.google.com/p/karrigell/wiki/%s?show=content,sidebar" %page
    req = opener.open(url)

    src = req.read().decode('utf-8')

    src = src.replace('http://www.gstatic.com/codesite/ph/images/','images/')
    src = re.sub('/p/karrigell/wiki/(.*?)"',r'\1.html"',src)
    src = re.sub('(?s)<div style="float:right;">(.*?)</div>','',src)
    src = re.sub('(?s)<div class="ifCollapse"(.*?)</div>','',src)
    src = re.sub('(?s)<div class="ifExpand"(.*?)Edit(.*?)</div>','',src)
    src = re.sub('(?s)<div id="wikiauthor"(.*?)</div>','',src)
    src = re.sub('(?s)<img (.*?)star_off.gif(.*?)>','',src)
    src = re.sub('(?s)<a class="label" (.*?)>Featured</a>','',src)

    stylesheet = '<link rel="stylesheet" href="wiki.css">\n'
    src = src.replace('<head>','<head>\n'+stylesheet)

    prettify = """<script src="prettify.js"></script>
     <script type="text/javascript">
     prettyPrint();
     </script>
    """
    src = src.replace('</body>',prettify+'</body>')

    out = open(os.path.join('html','%s.html' %page),'w',encoding="utf-8")
    out.write(src)
    out.close()
