import json,sys,os
d=os.path.dirname(os.path.abspath(__file__))
s=open(d+'/scene.src.html').read()
s=s.replace('__FONT__',open(sys.argv[1]).read().strip())
s=s.replace('__DURS__',json.dumps(json.load(open(d+'/audio/durs.json'))))
s=s.replace('__SCRIPT__',json.dumps(json.load(open(d+'/script.json'))))
open(d+'/scene.html','w').write(s)
