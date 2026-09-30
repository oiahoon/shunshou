"""Check share metadata and image delivery locally or against production."""
from html.parser import HTMLParser
from pathlib import Path
import argparse, struct, urllib.request
class Meta(HTMLParser):
 def __init__(self): super().__init__(); self.tags={}
 def handle_starttag(self, tag, attrs):
  a=dict(attrs)
  if tag=='meta':
   key=a.get('property',a.get('name'))
   if key in self.tags: raise AssertionError('Duplicate metadata: '+key)
   self.tags[key]=a.get('content','')
p=argparse.ArgumentParser(); p.add_argument('--live',action='store_true'); args=p.parse_args()
root=Path(__file__).resolve().parents[2]/'services/resolver/public'
base='https://shunshou.miaowu.org'
for name in ['index','insta-share','dianping','business-trip','avatar-studio']:
 route='/' if name=='index' else '/shortcuts/'+name
 raw=urllib.request.urlopen(base+route).read().decode() if args.live else (root/(name+'.html')).read_text()
 parser=Meta(); parser.feed(raw); t=parser.tags
 assert t['og:url']==base+route
 assert t['og:title'] and t['og:description']==t['description']
 assert t['og:locale']=='zh_CN' and t['twitter:card']=='summary_large_image'
 for key in ['og:image','twitter:image']:
  assert t[key].startswith(base+'/assets/share/')
  path=t[key].removeprefix(base)
  local=(root/path.lstrip('/')).read_bytes()
  assert local[:2]==b'\xff\xd8' and len(local)>10000
  if args.live:
   with urllib.request.urlopen(t[key]) as response:
    assert response.headers.get_content_type()=='image/jpeg'
    assert response.read()==local
 print(route+' sharing OK')
