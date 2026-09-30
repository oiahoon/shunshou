"""Render branded social cards and update public page metadata."""
from pathlib import Path
import base64, html, re, subprocess
ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / 'services/resolver/public'
OUT = PUBLIC / 'assets/share'
OUT.mkdir(exist_ok=True)
PAGES = [
 ('index','home','顺手实验室','把喜欢的事，变得更顺手。',None),
 ('insta-share','insta-share','Insta Share 顺手','保存 Instagram 视频，一键分享到微信。','insta'),
 ('dianping','dianping','大众点评快写','把真实体验整理成点评草稿。','dianping'),
 ('business-trip','business-trip','出差开销','随手记录出差开销。','business-trip'),
 ('avatar-studio','avatar-studio','头像装扮','为头像添加节日装饰或状态符号。','avatar'),
]
def img(icon,x,y,size):
 data=base64.b64encode((PUBLIC/f'assets/product-icon-{icon}.webp').read_bytes()).decode()
 return f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="data:image/webp;base64,{data}"/>'
for page,slug,title,desc,icon in PAGES:
 for shape,w,h in [('square',600,600),('wide',1200,630)]:
  square=shape=='square'
  art=img(icon,170 if square else 740,62 if square else 115,260 if square else 400) if icon else ''.join(img(i, x,y,150 if square else 190) for i,x,y in ([(i,135+(n%2)*190,48+(n//2)*160) for n,i in enumerate(['insta','dianping','business-trip','avatar'])] if square else [(i,730+(n%2)*205,90+(n//2)*205) for n,i in enumerate(['insta','dianping','business-trip','avatar'])]))
  tx=40 if square else 64; ty=402 if square else 282
  svg=f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="#181818"/>{art}<g font-family="PingFang SC, sans-serif"><text x="{tx}" y="{ty}" fill="#f6f3e9" font-size="{40 if square else 54}" font-weight="600">{html.escape(title)}</text><text x="{tx}" y="{ty+53}" fill="#bdbab2" font-size="{23 if square else 26}">{html.escape(desc)}</text><path d="M{tx} {h-70}h36" stroke="#ffdc32" stroke-width="4"/><text x="{tx+50}" y="{h-63}" fill="#ffdc32" font-size="18">顺手实验室</text><text x="{w-40}" y="{h-63}" text-anchor="end" fill="#99978f" font-size="15">shunshou.miaowu.org</text></g></svg>'''
  source=OUT/f'{slug}-{shape}.svg'; source.write_text(svg)
  # librsvg supports embedded PNG more reliably than WebP.
  for i in ['insta','dianping','business-trip','avatar']:
   original=base64.b64encode((PUBLIC/f'assets/product-icon-{i}.webp').read_bytes()).decode()
   png=subprocess.check_output(['magick',str(PUBLIC/f'assets/product-icon-{i}.webp'),'png:-'])
   svg=svg.replace('data:image/webp;base64,'+original,'data:image/png;base64,'+base64.b64encode(png).decode())
  temp=OUT/f'.{slug}.svg'; temp.write_text(svg)
  subprocess.run(['rsvg-convert',str(temp),'-o',str(OUT/f'{slug}-{shape}.png')],check=True)
  subprocess.run(['magick',str(OUT/f'{slug}-{shape}.png'),'-quality','90',str(OUT/f'{slug}-{shape}.jpg')],check=True)
  temp.unlink(); source.unlink(); (OUT/f'{slug}-{shape}.png').unlink()
 url='https://shunshou.miaowu.org'+('/' if page=='index' else '/shortcuts/'+slug)
 image='https://shunshou.miaowu.org/assets/share/'+slug
 fulltitle=title+' · 顺手实验室' if page!='index' else '顺手实验室 · 让喜欢的事更顺手'
 tags={'og:type':'website','og:locale':'zh_CN','og:site_name':'顺手实验室','og:title':fulltitle,'og:description':desc,'og:url':url,'og:image':image+'-square.jpg','og:image:secure_url':image+'-square.jpg','og:image:type':'image/jpeg','og:image:width':'600','og:image:height':'600','og:image:alt':title+'分享预览图'}
 metadata='\n<!-- Social sharing -->\n'+''.join(f'<meta property="{k}" content="{html.escape(v,quote=True)}">\n' for k,v in tags.items())
 metadata+=''.join(f'<meta name="{k}" content="{html.escape(v,quote=True)}">\n' for k,v in {'twitter:card':'summary_large_image','twitter:title':fulltitle,'twitter:description':desc,'twitter:image':image+'-wide.jpg','twitter:image:alt':title+'分享预览图'}.items())
 metadata+=f'<link rel="image_src" href="{image}-square.jpg">\n<!-- /Social sharing -->\n'
 path=PUBLIC/(page+'.html'); content=path.read_text()
 content=re.sub(r'\n?<!-- Social sharing -->.*?<!-- /Social sharing -->\n?', '',content,flags=re.S)
 content=re.sub(r'<meta property="og:[^"]*"[^>]*>','',content)
 content=re.sub(r'<meta name="description"[^>]*>',f'<meta name="description" content="{desc}">',content)
 path.write_text(content.replace('</head>',metadata+'</head>'))
