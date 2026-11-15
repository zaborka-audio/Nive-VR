import re,collections
def tokenize(s):
    return re.findall(r'\(|\)|"[^"]*"|[^\s()]+',s)
def parse(tokens):
    stack=[[]]
    for t in tokens:
        if t=='(':
            stack.append([])
        elif t==')':
            l=stack.pop(); stack[-1].append(l)
        else: stack[-1].append(t)
    return stack[0][0]
def load(path='pcb_v33.dsn'):
    s=open(path,encoding='utf8').read()
    return parse(tokenize(s))
def find(node,name):
    return [n for n in node if isinstance(n,list) and n and n[0]==name]
