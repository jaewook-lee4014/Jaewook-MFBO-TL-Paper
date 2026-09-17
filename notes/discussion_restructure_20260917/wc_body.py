import re,sys
src=open('main.tex').read()
def body(sec_start, sec_end):
    s=src.index(sec_start); e=src.index(sec_end, s)
    t=src[s:e]
    t=re.sub(r'\\begin\{figure\*?\}.*?\\end\{figure\*?\}', '', t, flags=re.S)
    t=re.sub(r'\\begin\{table\*?\}.*?\\end\{table\*?\}', '', t, flags=re.S)
    t=re.sub(r'\\storyline\{[^}]*\}', '', t)
    t=re.sub(r'%.*', '', t)
    t=re.sub(r'\\cite[pt]?\{[^}]*\}', '', t)
    t=re.sub(r'\\(?:ref|label)\{[^}]*\}', 'X', t)
    t=re.sub(r'\\[a-zA-Z]+\*?', ' ', t)
    t=re.sub(r'[{}$]', ' ', t)
    return len(t.split())
for name,a,b in [('Intro','\\section{Introduction}','\\section{Results}'),('Results','\\section{Results}','\\section{Discussion}'),('Discussion','\\section{Discussion}','\\section{Methods}')]:
    print(name, body(a,b))
