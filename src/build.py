import re,base64,os
d=os.path.dirname(os.path.abspath(__file__))
s=open(d+'/index.src.html',encoding='utf-8').read()
def rep(m):
    f=m.group(1); mime={'jpg':'image/jpeg','webp':'image/webp','png':'image/png','woff2':'font/woff2','mp3':'audio/mpeg'}[f.rsplit('.',1)[1]]
    return 'data:%s;base64,%s'%(mime,base64.b64encode(open(d+'/assets/'+f,'rb').read()).decode())
import json,glob,subprocess
a=s.index('<script>')+8;b=s.index('</script>',a)
open('/tmp/_b_in.js','w',encoding='utf-8').write(s[a:b])
subprocess.run(['node',d+'/tools/i18n.js','/tmp/_b_in.js','/tmp/_b_out.js','/tmp/_b_keys.json'],check=True)
keys=json.load(open(d+'/i18n/keys_ru.json',encoding='utf-8'))
en={}
for f in sorted(glob.glob(d+'/i18n/en_*.txt')):
    for l in open(f,encoding='utf-8').read().rstrip('\n').split('\n'):
        i,t=l.split('|',1); en[int(i)]=t
D={keys[i]:en[i] for i in range(len(keys)) if i in en}
need=set(json.load(open('/tmp/_b_keys.json',encoding='utf-8')))
miss=[k for k in need if k not in D]
print('i18n: dict',len(D),'missing',len(miss)); [print('  MISS',m[:70]) for m in miss[:20]]
rt=open(d+'/parts/i18n_rt.js',encoding='utf-8').read().replace('/*%%I18N%%*/{}',json.dumps(D,ensure_ascii=False))
s=s[:a]+'\nwindow.__TITLE_EN="%%title_top_en.jpg%%";\n'+rt+open('/tmp/_b_out.js',encoding='utf-8').read()+s[b:]
s=re.sub(r'%%([\w.-]+)%%',rep,s)
open(d+'/index.html','w',encoding='utf-8').write(s); print(len(s)//1024,'KB')
