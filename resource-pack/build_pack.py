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
def pumpkin_model():
    cells=set()
    for x in range(1,15):
        for y in range(2,13):
            for z in range(1,15):
                dx=x+0.5-8; dy=y+0.5-7.5; dz=z+0.5-8
                angle=math.atan2(dz,dx)
                radius=6.5*(1+0.06*math.cos(8*angle))
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
    eyes = {(x,y) for x in (4,5,10,11) for y in (8,9)}
    smile = {(x,5) for x in range(6,10)} | {(5,6),(10,6)}
    directions={'west':(-1,0,0),'east':(1,0,0),'down':(0,-1,0),
                'up':(0,1,0),'north':(0,0,-1),'south':(0,0,1)}
    elements=[]
    for x,y,z in sorted(cells):
        shade=materials[x,y,z]
        faces={face:{'uv':[0,0,16,16],'texture':'#'+(
                   'pumpkin_face' if face=='north' and (x,y) in eyes | smile else shade)}
               for face,(dx,dy,dz) in directions.items() if (x+dx,y+dy,z+dz) not in cells}
        if faces:
            elements.append({'from':[x,y,z],'to':[x+1,y+1,z+1],'faces':faces})
    return {'credit':'Original round ribbed pumpkin companion.',
            'textures':{name:'cosmeticpets:pet/'+name for name in
                        ('pumpkin_orange','pumpkin_rib','pumpkin_green','pumpkin_stem','pumpkin_face')},
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
        'pack.mcmeta': json.dumps({'pack':{'description':'CosmeticPets - ghost and bouncing pumpkin', 'min_format':[97,1], 'max_format':[97,1]}}).encode(),
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
    colors={'pumpkin_orange':(238,123,24,255),'pumpkin_rib':(187,77,13,255),
            'pumpkin_green':(74,101,32,255),'pumpkin_stem':(86,65,33,255),
            'pumpkin_face':(49,27,19,255)}
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
