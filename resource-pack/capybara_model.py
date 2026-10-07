"""Original block capybara inspired by the owner's reference images."""
import math, struct, zlib
PALETTE={'capy_body':(151,109,67),'capy_head':(157,112,71),'capy_side':(157,112,71),
 'capy_half':(157,112,71),'capy_closed':(157,112,71),'capy_muzzle':(76,64,49),
 'capy_ear':(80,67,51),'capy_foot':(73,62,48)}
def color(name,x,y):
 base=PALETTE[name];noise=((x//2*13+y//2*7+x//2*y//2*3)%11-5)*3
 if name in ('capy_side','capy_half','capy_closed'):
  if 3<=x<=6 and (y==9 or (name=='capy_side' and y==10)):
   return (25,22,17)
  if name=='capy_closed' and 2<=x<=7 and y==9:return (25,22,17)
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
 box([4,3,6],[12,10,15],'capy_body')
 head=box([4,7,0],[12,13,6],'capy_head')
 eye='capy_side' if idle in (None,0,5) else 'capy_half' if idle in (1,4) else 'capy_closed'
 for side in ('east','west'):head['faces'][side]['texture']='#'+eye
 head['faces']['north']['texture']='#capy_muzzle'
 for x in (4,10):
  ear=box([x,13,4],[x+2,15,6],'capy_ear')
  ear['rotation']={'origin':[x+1,13,5],'axis':'z','angle':-22.5 if x==4 else 22.5,'rescale':False}
 for x in (4,10):
  for z in (7,12):
   sign=1 if (x,z) in ((4,7),(10,12)) else -1
   angle=round(math.sin(2*math.pi*(walk or 0)/12)*sign)*22.5 if walk is not None else 0
   for a,b,mat in [([x,1,z],[x+2,3,z+2],'capy_body'),([x,0,z],[x+2,1,z+2],'capy_foot')]:
    e=box(a,b,mat)
    if walk is not None:e['rotation']={'origin':[x+1,3,z+1],'axis':'x','angle':angle,'rescale':False}
 return {'credit':'Original CosmeticPets block capybara','textures':{n:'cosmeticpets:pet/'+n for n in PALETTE},'elements':elements,
  'display':{'fixed':{'rotation':[0,0,0],'translation':[0,8,0],'scale':[1,1,1]}}}
