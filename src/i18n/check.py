import re,sys,glob
def load(f):
    d={}
    for l in open(f,encoding='utf8').read().rstrip('\n').split('\n'):
        i,t=l.split('|',1); d[int(i)]=t
    return d
bad=0
for ruf in sorted(glob.glob('ru_*.txt')):
    enf=ruf.replace('ru_','en_')
    try: en=load(enf)
    except FileNotFoundError: continue
    ru=load(ruf)
    if set(ru)!=set(en): print(enf,'ids differ',sorted(set(ru)^set(en))[:10]); bad+=1
    for i in ru:
        if i not in en: continue
        a,b=ru[i],en[i]
        if sorted(re.findall(r'\{\d+\}',a))!=sorted(re.findall(r'\{\d+\}',b)): print('PH',i,a[:60],'|',b[:60]); bad+=1
        na=sorted(re.findall(r'\d+',re.sub(r'\{\d+\}','',a))); nb=sorted(re.findall(r'\d+',re.sub(r'\{\d+\}','',b)))
        if na!=nb: print('NUM',i,na,nb,'|',a[:50],'|',b[:50])
        if re.search('[А-Яа-яЁё]',b): print('CYR',i,b[:60])
print('bad',bad)
