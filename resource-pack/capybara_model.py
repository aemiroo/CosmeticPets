"""Original block capybara inspired by the owner's reference images."""
import math, struct, zlib
PALETTE={'capy_body':(161,116,65),'capy_head':(166,121,73),'capy_side':(166,121,73),
 'capy_half':(166,121,73),'capy_closed':(166,121,73),'capy_muzzle':(76,64,49),
 'capy_white':(218,224,215),'capy_eye':(25,22,17),'capy_ear':(80,67,51),'capy_foot':(73,62,48)}
def color(name,x,y):
 base=PALETTE[name];noise=((x//3*13+y//3*7+x//3*y//3*3)%11-5)*5
 if name in ('capy_eye','capy_white'):return PALETTE[name]
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
 box([4,5,6],[12,13,15],'capy_body')
 head=box([4,8,2],[12,14,6],'capy_head')
 del head['faces']['north']
 snout=box([4,8,0],[12,14,2],'capy_muzzle')
 del snout['faces']['south']
 eye_height=.75 if idle in (None,0,5) else .4 if idle in (1,4) else .15
 for x in (3.98,12):
  box([x,11,4],[x+.02,11+eye_height,4.75],'capy_eye')
  box([x,11,4.75],[x+.02,11+eye_height,5.5],
      'capy_white' if idle not in (2,3) else 'capy_eye')
 for x in (4,10):
  box([x,14,4],[x+2,16,6],'capy_ear')
 # The references carry the snout slightly below the back of the head.
 for e in elements[1:]:
  e['rotation']={'origin':[8,11,6],'axis':'x','angle':-10,'rescale':False}
 tail=box([7,8,15],[9,10,17],'capy_body')
 tail['rotation']={'origin':[8,9,15],'axis':'x','angle':-22.5,'rescale':False}
 for x in (4,10):
  for z in (7,12):
   sign=1 if (x,z) in ((4,7),(10,12)) else -1
   angle=round(math.sin(2*math.pi*(walk or 0)/24)*sign*18,6) if walk is not None else 0
   for a,b,mat in [([x,3,z],[x+2,5,z+2],'capy_body'),([x,0,z],[x+2,3,z+2],'capy_foot')]:
    e=box(a,b,mat)
    if walk is not None:e['rotation']={'origin':[x+1,5,z+1],'axis':'x','angle':angle,'rescale':False}
 return {'credit':'Original CosmeticPets block capybara','textures':{n:'cosmeticpets:pet/'+n for n in PALETTE},'elements':elements,
  'display':{'fixed':{'rotation':[0,0,0],'translation':[0,8,0],'scale':[1,1,1]}}}
