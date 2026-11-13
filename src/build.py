import re,base64,os
d=os.path.dirname(os.path.abspath(__file__))
s=open(d+'/index.src.html',encoding='utf-8').read()
def rep(m):
    f=m.group(1); mime={'jpg':'image/jpeg','webp':'image/webp','png':'image/png','woff2':'font/woff2','mp3':'audio/mpeg'}[f.rsplit('.',1)[1]]
    return 'data:%s;base64,%s'%(mime,base64.b64encode(open(d+'/assets/'+f,'rb').read()).decode())
s=re.sub(r'%%([\w.-]+)%%',rep,s)
open(d+'/index.html','w',encoding='utf-8').write(s); print(len(s)//1024,'KB')
