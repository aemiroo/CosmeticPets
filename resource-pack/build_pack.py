"""Build an original voxel ghost pack without third-party image/model assets."""
import hashlib, json, pathlib, struct, zlib, zipfile, math
ROOT = pathlib.Path(__file__).resolve().parents[1]
def png(color):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    raw = b''.join(b'\0' + bytes(color) * 16 for _ in range(16))
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 16,16,8,6,0,0,0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND',b'')
def cube(start, end, texture='white'):
    return {'from': start, 'to': end, 'faces': {face: {'uv':[0,0,16,16], 'texture':'#'+texture} for face in ('north','south','east','west','up','down')}}
def shell():
    # Unite the body, cap, arms and perimeter fringe before emitting faces.
    # Interior faces would show distracting seams through a translucent body.
    volumes = [([3,4,3],[13,13,13]), ([4,13,4],[12,14,12]),
               ([1,7,6],[3,10,10]), ([13,7,6],[15,10,10])]
    for i, bottom in enumerate((2,3,1,3,2)):
        x=3+i*2
        volumes.extend([([x,bottom,3],[x+2,4,4]), ([x,bottom,12],[x+2,4,13])])
    for i, bottom in enumerate((3,1,3,2)):
        z=4+i*2
        volumes.extend([([3,bottom,z],[4,4,z+2]), ([12,bottom,z],[13,4,z+2])])
    cells=set()
    for start,end in volumes:
        for x in range(start[0],end[0]):
            for y in range(start[1],end[1]):
                for z in range(start[2],end[2]):
                    cells.add((x,y,z))
    directions={'west':(-1,0,0),'east':(1,0,0),'down':(0,-1,0),
                'up':(0,1,0),'north':(0,0,-1),'south':(0,0,1)}
    elements=[]
    for x,y,z in sorted(cells):
        faces={}
        for face,(dx,dy,dz) in directions.items():
            if (x+dx,y+dy,z+dz) not in cells:
                faces[face]={'uv':[0,0,16,16],
                             'texture':'#underside' if face=='down' else '#white'}
        if faces:
            elements.append({'from':[x,y,z],'to':[x+1,y+1,z+1],'faces':faces})
    return elements
def winter_model(pet):
    # Unite solid voxels first: only external faces are emitted, avoiding seams.
    cells={}
    def box(a,b,material):
        for x in range(a[0],b[0]):
            for y in range(a[1],b[1]):
                for z in range(a[2],b[2]): cells[x,y,z]=material
    def ball(center,radii,material):
        for x in range(16):
            for y in range(16):
                for z in range(16):
                    if sum(((v+.5-c)/d)**2 for v,c,d in zip((x,y,z),center,radii))<=1:
                        cells[x,y,z]=material
    if pet=='snowman':
        ball((8,4,8),(4,4,4),'snow')
        ball((8,8,8),(3,3,3),'snow')
        ball((8,11,8),(2.5,2.5,2.5),'snow')
        box((5,13,5),(11,14,11),'coal')
        box((6,14,6),(10,16,10),'coal')
        box((5,8,5),(11,9,11),'scarf')
        box((5,6,4),(7,9,5),'scarf')
        box((6,11,5),(7,12,6),'coal'); box((9,11,5),(10,12,6),'coal')
        box((7,10,3),(9,11,6),'carrot')
        box((7,4,4),(8,5,5),'coal'); box((7,6,5),(8,7,6),'coal')
        box((1,7,7),(5,8,8),'wood'); box((11,7,7),(15,8,8),'wood')
        box((1,8,7),(2,10,8),'wood'); box((14,8,7),(15,10,8),'wood')
    else:
        ball((8,6,9),(4,3,4),'fur')
        box((6,6,4),(10,10,7),'fur')
        ball((8,10,5),(3,2.5,3),'fur')
        box((6,9,1),(10,11,4),'muzzle')
        box((7,10,0),(9,11,1),'red_nose')
        box((5,11,2),(6,12,3),'coal'); box((10,11,2),(11,12,3),'coal')
        box((3,11,5),(5,13,7),'fur'); box((11,11,5),(13,13,7),'fur')
        for x in (5,10):
            for z in (7,11):
                box((x,1,z),(x+1,5,z+1),'fur'); box((x,0,z),(x+1,1,z+1),'coal')
        box((7,6,13),(9,8,15),'muzzle')
        box((5,7,4),(11,8,7),'scarf')
        for x in (5,10):
            box((x,12,5),(x+1,16,6),'antler')
        box((3,14,5),(6,15,6),'antler'); box((10,14,5),(13,15,6),'antler')
        box((3,15,5),(4,16,6),'antler'); box((12,15,5),(13,16,6),'antler')
    directions={'west':(-1,0,0),'east':(1,0,0),'down':(0,-1,0),
                'up':(0,1,0),'north':(0,0,-1),'south':(0,0,1)}
    elements=[]
    for (x,y,z),material in sorted(cells.items()):
        faces={f:{'uv':[0,0,16,16],'texture':'#'+material}
               for f,(dx,dy,dz) in directions.items() if (x+dx,y+dy,z+dz) not in cells}
        if faces: elements.append({'from':[x,y,z],'to':[x+1,y+1,z+1],'faces':faces})
    names=sorted({e['texture'][1:] for c in elements for e in c['faces'].values()})
    return {'credit':'Original CosmeticPets Christmas companion.',
            'textures':{n:'cosmeticpets:pet/'+n for n in names},'elements':elements,
            'display':{'fixed':{'rotation':[0,0,0],'translation':[0,8,0],'scale':[1,1,1]}}}

def pumpkin_model():
    cells=set()
    for x in range(1,15):
        for y in range(2,13):
            for z in range(1,15):
                dx=x+0.5-8; dy=y+0.5-7.5; dz=z+0.5-8
                angle=math.atan2(dz,dx)
                radius=6.5*(1+0.025*math.cos(8*angle))
                if (dx*dx+dz*dz)/(radius*radius)+(dy/5.5)**2 <= 1:
                    cells.add((x,y,z))
    # One solid union: the green cap intersects the orange body at Y=12.
    # Emitting those as separate boxes produces coplanar top faces and flicker.
    materials = {cell: ('pumpkin_rib'
                 if math.cos(8*math.atan2(cell[2]+0.5-8,cell[0]+0.5-8)) < -0.25
                 else 'pumpkin_orange') for cell in cells}
    for start,end,material in (
            ([6,12,6],[10,13,10],'pumpkin_green'),
            ([7,13,7],[9,15,9],'pumpkin_stem'),
            ([8,15,7],[10,16,9],'pumpkin_stem')):
        for x in range(start[0],end[0]):
            for y in range(start[1],end[1]):
                for z in range(start[2],end[2]):
                    materials[x,y,z] = material
    cells = set(materials)
    # Paint the exposed front faces, following the pumpkin's curved surface.
    # No thin overlay planes: the eyes and smile cannot z-fight with the rind.
    # Stepped triangular eyes, a small inverted nose and a toothy grin.
    eyes = {(5,10),(10,10),(5,9),(6,9),(9,9),(10,9)}
    eyes |= {(x,8) for x in (4,5,6,9,10,11)}
    nose = {(7,7),(8,7),(7,6)}
    smile = {(x,4) for x in range(4,12) if x not in (6,9)}
    smile |= {(x,3) for x in range(5,11)} | {(4,5),(11,5)}
    face_pixels = eyes | nose | smile
    # Remove three voxels of rind at every face pixel, preserving the outer
    # silhouette everywhere else. The lit back walls sit inside these openings.
    removed=set()
    light_stops=set()
    for x,y in face_pixels:
        front=min(z for cx,cy,z in cells if (cx,cy)==(x,y))
        stop=front+3
        light_stops.add((x,y,stop))
        for z in range(front,stop):
            removed.add((x,y,z))
            materials.pop((x,y,z),None)
    cells=set(materials)
    directions={'west':(-1,0,0),'east':(1,0,0),'down':(0,-1,0),
                'up':(0,1,0),'north':(0,0,-1),'south':(0,0,1)}
    elements=[]
    for x,y,z in sorted(cells):
        shade=materials[x,y,z]
        faces={}
        for face,(dx,dy,dz) in directions.items():
            neighbour=(x+dx,y+dy,z+dz)
            if neighbour in cells:
                continue
            texture='pumpkin_inner' if neighbour in removed else shade
            faces[face]={'uv':[0,0,16,16],'texture':'#'+texture}
        if (x,y,z) in light_stops:
            # Separate the emitting front face from the normally lit rind.
            faces.pop('north',None)
            elements.append({'from':[x,y,z],'to':[x+1,y+1,z+1],
                             'faces':{'north':{'uv':[0,0,16,16],'texture':'#pumpkin_glow'}},
                             'light_emission':15,'shade':False})
        if faces:
            elements.append({'from':[x,y,z],'to':[x+1,y+1,z+1],'faces':faces})
    return {'credit':'Original round ribbed pumpkin companion.',
            'textures':{name:'cosmeticpets:pet/'+name for name in
                        ('pumpkin_orange','pumpkin_rib','pumpkin_green','pumpkin_stem','pumpkin_inner','pumpkin_glow')},
            'elements':elements,
            'display':{'fixed':{'rotation':[0,0,0],'translation':[0,6,0],'scale':[1,1,1]}},
            'gui_light':'front'}
def files():
    elements = shell() + [
                cube([5,9,2.85],[6.5,11,3],'dark'), cube([9.5,9,2.85],[11,11,3],'dark'),
                cube([7.25,6.5,2.85],[8.75,8,3],'dark'),
                cube([4,7.5,2.8],[5.5,8,3],'pink'), cube([10.5,7.5,2.8],[12,8,3],'pink')]
    model = {'credit':'Original CosmeticPets ghost; no Sketchfab assets used.', 'textures': {x:'cosmeticpets:pet/'+x for x in ('white','dark','pink','underside')}, 'elements':elements,
             'display': {'fixed': {'rotation':[0,0,0], 'translation':[0,0,0], 'scale':[1,1,1]}}, 'gui_light':'front'}
    result = {
        'pack.mcmeta': json.dumps({'pack':{'description':'CosmeticPets - Halloween and Christmas companions', 'min_format':[97,1], 'max_format':[97,1]}}).encode(),
        'assets/minecraft/atlases/items.json': json.dumps({'sources': [
            {'type':'minecraft:single', 'resource':'cosmeticpets:pet/'+name,
             'sprite':'cosmeticpets:pet/'+name} for name in ('white','dark','pink','underside')
        ]}).encode(),
        'assets/cosmeticpets/items/ghost.json': json.dumps({'model':{'type':'minecraft:model','model':'cosmeticpets:pet/ghost'}}).encode(),
        'assets/cosmeticpets/models/pet/ghost.json':json.dumps(model).encode(),
        'assets/cosmeticpets/textures/pet/white.png':png((236,244,250,110)),
        'assets/cosmeticpets/textures/pet/dark.png':png((31,25,49,235)),
        'assets/cosmeticpets/textures/pet/pink.png':png((214,154,190,190)),
        'assets/cosmeticpets/textures/pet/underside.png':png((205,216,229,110)),
        'LICENSE.txt': b'Original ghost model and textures: MIT License, same as the CosmeticPets repository. No third-party models or textures included.\n'
    }
    result['assets/cosmeticpets/items/pumpkin.json']=json.dumps(
        {'model':{'type':'minecraft:model','model':'cosmeticpets:pet/pumpkin'}}).encode()
    result['assets/cosmeticpets/models/pet/pumpkin.json']=json.dumps(pumpkin_model()).encode()
    colors={'pumpkin_orange':(238,123,24,255),'pumpkin_rib':(213,98,18,255),
            'pumpkin_green':(74,101,32,255),'pumpkin_stem':(86,65,33,255),
            'pumpkin_inner':(140,58,14,255),'pumpkin_glow':(255,197,74,255), 'snow':(240,248,255,255),
            'coal':(35,30,32,255),'scarf':(190,32,43,255),'carrot':(245,130,28,255),
            'wood':(105,70,38,255),'fur':(135,82,44,255),'muzzle':(211,166,112,255),
            'red_nose':(242,54,54,255),'antler':(193,153,101,255)}
    for pet in ('snowman','reindeer'):
        result['assets/cosmeticpets/items/'+pet+'.json']=json.dumps({'model':{'type':'minecraft:model','model':'cosmeticpets:pet/'+pet}}).encode()
        result['assets/cosmeticpets/models/pet/'+pet+'.json']=json.dumps(winter_model(pet)).encode()
    atlas=json.loads(result['assets/minecraft/atlases/items.json'])
    for name,color in colors.items():
        result['assets/cosmeticpets/textures/pet/'+name+'.png']=png(color)
        atlas['sources'].append({'type':'minecraft:single','resource':'cosmeticpets:pet/'+name,
                                 'sprite':'cosmeticpets:pet/'+name})
    result['assets/minecraft/atlases/items.json']=json.dumps(atlas).encode()
    return result
if __name__ == '__main__':
    output = ROOT / 'target' / 'CosmeticPets-Ghost-Pack.zip'
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files().items()):
            info = zipfile.ZipInfo(name, (2026,1,1,0,0,0)); info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info,data)
    digest = hashlib.sha1(output.read_bytes()).hexdigest()
    (output.parent / 'ghost-pack.sha1').write_text(digest+'\n')
    resources = ROOT/'src/main/resources'
    (resources/'ghost-pack.sha1').write_text(digest+'\n')
    print('Built',output.name,'SHA-1:',digest)
