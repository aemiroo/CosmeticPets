"""Original block capybara inspired by the owner's reference images."""
import math, struct, zlib
PALETTE={'capy_body':(161,116,65),'capy_head':(166,121,73),'capy_side':(166,121,73),
 'capy_half':(166,121,73),'capy_closed':(166,121,73),'capy_muzzle':(76,64,49),
 'capy_eye':(25,22,17),'capy_ear':(80,67,51),'capy_foot':(73,62,48)}
def color(name,x,y):
 base=PALETTE[name];noise=((x//2*13+y//2*7+x//2*y//2*3)%11-5)*3
 if name=='capy_eye':return PALETTE[name]
 if name=='capy_muzzle' and y in (7,8) and x in (4,5,10,11):return (29,25,20)
 return tuple(max(0,min(255,v+noise)) for v in base)
def texture(name):
 def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
 raw=b''.join(b'\0'+b''.join(bytes(color(name,x,15-y)) + b'\xff' for x in range(16)) for y in range(16))
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',16,16,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
def model(walk=None,idle=None):
 elements=[]
 def box(a,b,mat):
  e={'from':a,'to':b,'faces':{f:{'uv':[0,0,16,16],'texture':'#'+mat} for f in ('north','south','east','west','up','down')}}
  elements.append(e);return e
 box([4,3,6],[12,12,15],'capy_body')
 head=box([4,7,2],[12,13,6],'capy_head')
 del head['faces']['north']
 snout=box([4,7,0],[12,13,2],'capy_muzzle')
 del snout['faces']['south']
 # Put both eyes beside the ears instead of mapping an eye onto the snout.
 eye_height=.6 if idle in (None,0,5) else .35 if idle in (1,4) else .15
 for x in (3.98,12):
  box([x,10.5,4],[x+.02,10.5+eye_height,5.5],'capy_eye')
 for x in (4,10):
  ear=box([x,13,4],[x+2,15,6],'capy_ear')
  ear['rotation']={'origin':[x+1,13,5],'axis':'z','angle':-22.5 if x==4 else 22.5,'rescale':False}
 for x in (4,10):
  for z in (7,12):
   sign=1 if (x,z) in ((4,7),(10,12)) else -1
   angle=round(math.sin(2*math.pi*(walk or 0)/24)*sign*18,6) if walk is not None else 0
   for a,b,mat in [([x,1,z],[x+2,3,z+2],'capy_foot'),([x,0,z],[x+2,1,z+2],'capy_foot')]:
    e=box(a,b,mat)
    if walk is not None:e['rotation']={'origin':[x+1,3,z+1],'axis':'x','angle':angle,'rescale':False}
 return {'credit':'Original CosmeticPets block capybara','textures':{n:'cosmeticpets:pet/'+n for n in PALETTE},'elements':elements,
  'display':{'fixed':{'rotation':[0,0,0],'translation':[0,8,0],'scale':[1,1,1]}}}
