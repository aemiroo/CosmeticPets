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
def limb(pet, cell):
    x,y,z=cell
    if pet=='reindeer' and y<5 and x in (5,10) and z in (7,11):
        return ('leg',x,z)
    if pet=='capybara' and y<3 and x in (4,5,10,11) and z in (5,6,11,12):
        return ('leg',0 if x<8 else 1,0 if z<9 else 1)
    if pet=='yeti':
        if y<3 and x in (5,6,9,10) and 5<=z<10:
            return ('leg',0 if x<8 else 1)
        if (1<=x<4 or 12<=x<15) and 1<=y<10 and 6<=z<11:
            return ('arm',0 if x<8 else 1)
    return None

def winter_model(pet, articulated=False):
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
    if pet=='capybara':
        # Low, broad barrel body, blunt muzzle and small rounded ears.
        ball((8,5.5,9),(4.5,3.5,6),'capy_fur')
        box((4,4,1),(12,9,7),'capy_fur')
        box((5,3,0),(11,6,2),'capy_muzzle')
        box((4,9,5),(6,11,7),'capy_fur');box((10,9,5),(12,11,7),'capy_fur')
        box((4,7,2),(5,8,3),'coal');box((11,7,2),(12,8,3),'coal')
        box((6,5,0),(7,6,1),'capy_nose');box((9,5,0),(10,6,1),'capy_nose')
        for x in (4,10):
            for z in (5,11):
                box((x,0,z),(x+2,3,z+2),'capy_fur')
                box((x,0,z),(x+2,1,z+2),'capy_muzzle')
    elif pet=='yeti':
        # Original baby silhouette inspired by the supplied long-armed reference.
        box((4,2,5),(12,10,12),'yeti_cream')
        box((4,9,4),(12,14,11),'yeti_cream')
        box((1,1,6),(4,10,11),'yeti_cream')
        box((12,1,6),(15,10,11),'yeti_cream')
        box((5,0,5),(7,3,10),'yeti_cream')
        box((9,0,5),(11,3,10),'yeti_cream')
        # Small horns wrap down the sides, rather than projecting above the head.
        # Thick side roots taper forward and down into a curved three-dimensional tip.
        box((2,12,4),(5,14,8),'yeti_horn')
        box((2,11,3),(4,13,5),'yeti_horn')
        box((3,10,2),(4,12,4),'yeti_horn')
        box((11,12,4),(14,14,8),'yeti_horn')
        box((12,11,3),(14,13,5),'yeti_horn')
        box((12,10,2),(13,12,4),'yeti_horn')
        # Flat face: all facial colours occupy the same surface plane.
        box((5,9,4),(11,12,5),'yeti_face')
        box((5,11,4),(7,12,5),'yeti_blue')
        box((9,11,4),(11,12,5),'yeti_blue')
        box((6,11,4),(7,12,5),'coal')
        box((9,11,4),(10,12,5),'coal')
        box((7,10,4),(9,11,5),'yeti_nose')
        box((6,9,4),(10,10,5),'yeti_smile')
        # A repeatable voxel fur pattern is preserved in both pack formats.
        for (x,y,z),material in list(cells.items()):
            if material=='yeti_cream':
                stripe=(x*7+z*11+(y//2)*3)%17
                cells[x,y,z]='yeti_fur_shadow' if stripe<3 else ('yeti_fur_light' if stripe==5 else material)
    elif pet=='snowman':
        ball((8,4,8),(4,4,4),'snow')
        ball((8,8,8),(3,3,3),'snow')
        ball((8,11,8),(2.5,2.5,2.5),'snow')
        box((6,13,6),(10,14,10),'coal')
        box((7,14,7),(9,16,9),'coal')
        box((5,8,5),(11,9,11),'scarf')
        box((5,6,4),(7,9,5),'scarf')
        box((6,11,5),(7,12,6),'coal'); box((9,11,5),(10,12,6),'coal')
        box((7,10,3),(9,11,6),'carrot')
        box((7,4,4),(8,5,5),'coal'); box((7,6,5),(8,7,6),'coal')
        box((3,6,7),(5,7,8),'wood'); box((11,6,7),(13,7,8),'wood')
        box((3,4,7),(4,6,8),'wood'); box((12,4,7),(13,6,8),'wood')
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
               for f,(dx,dy,dz) in directions.items()
               if (x+dx,y+dy,z+dz) not in cells or
               (articulated and limb(pet,(x,y,z))!=limb(pet,(x+dx,y+dy,z+dz)))}
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
def legacy_files():
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
            'pumpkin_inner':(140,58,14,255),'pumpkin_glow':(255,197,74,255), 'yeti_cream':(235,235,216,255),'yeti_fur_shadow':(204,209,185,255),
            'yeti_fur_light':(249,249,237,255),'yeti_horn':(155,162,132,255),
            'yeti_face':(117,153,168,255),'yeti_nose':(74,105,119,255),
            'yeti_smile':(48,78,90,255),'yeti_blue':(109,204,229,255), 'snow':(240,248,255,255),
            'coal':(35,30,32,255),'scarf':(190,32,43,255),'carrot':(245,130,28,255),
            'wood':(105,70,38,255),'fur':(135,82,44,255),'muzzle':(211,166,112,255),
            'red_nose':(242,54,54,255),'antler':(193,153,101,255)}
    for pet in ('snowman','reindeer','yeti'):
        result['assets/cosmeticpets/items/'+pet+'.json']=json.dumps({'model':{'type':'minecraft:model','model':'cosmeticpets:pet/'+pet}}).encode()
        result['assets/cosmeticpets/models/pet/'+pet+'.json']=json.dumps(winter_model(pet)).encode()
    atlas=json.loads(result['assets/minecraft/atlases/items.json'])
    for name,color in colors.items():
        result['assets/cosmeticpets/textures/pet/'+name+'.png']=png(color)
        atlas['sources'].append({'type':'minecraft:single','resource':'cosmeticpets:pet/'+name,
                                 'sprite':'cosmeticpets:pet/'+name})
    result['assets/minecraft/atlases/items.json']=json.dumps(atlas).encode()
    return result
def walk_model(pet, frame):
    if pet=="capybara":
        from capybara_model import model
        return model(walk=frame)
    # Closed surfaces at each joint prevent holes when limbs rotate away.
    model=winter_model(pet, articulated=True)
    swing=math.sin(2*math.pi*frame/12)
    for element in model['elements']:
        part=limb(pet, element['from'])
        if part is None: continue
        if pet=='capybara':
            _,x,z=part
            pivot=[5 if x==0 else 11,3,6 if z==0 else 12]
            angle=round(swing*(1 if x==z else -1))*22.5
        elif pet=='reindeer':
            _,x,z=part
            # Vanilla quadruped gait: diagonal legs swing together.
            sign=1 if (x,z) in ((5,7),(10,11)) else -1
            pivot=[x+.5,5,z+.5]
            angle=28*swing*sign
        else:
            kind,side=part
            sign=1 if side==0 else -1
            if kind=='arm':
                pivot=[2.5 if side==0 else 13.5,9,8.5]
                # Iron golem arms swing together, using a triangular cycle.
                golem_swing=1-4*abs((frame/12+.25)%1-.5)
                angle=-18*golem_swing
            else:
                pivot=[6 if side==0 else 10,3,7.5]
                angle=25*swing*sign
        element['rotation']={'origin':pivot,'axis':'x',
                             'angle':round(angle,6),'rescale':False}
    return model

def reindeer_walk_model(frame):
    return walk_model('reindeer',frame)

def yeti_walk_model(frame):
    return walk_model('yeti',frame)

def files():
    source=legacy_files()
    keep={'snowman','reindeer','yeti','ghost','pumpkin','capybara'}
    from capybara_model import model as capy_model, texture as capy_texture, PALETTE
    source['assets/cosmeticpets/models/pet/capybara.json']=json.dumps(capy_model()).encode()
    source['assets/cosmeticpets/items/capybara.json']=json.dumps({'model':{'type':'minecraft:model','model':'cosmeticpets:pet/capybara'}}).encode()
    for name in PALETTE:source['assets/cosmeticpets/textures/pet/'+name+'.png']=capy_texture(name)
    models={p:json.loads(source['assets/cosmeticpets/models/pet/'+p+'.json']) for p in keep}
    textures={t for m in models.values() for t in m['textures'].values()}
    result={'pack.mcmeta':json.dumps({'pack':{'description':'CosmeticPets - Companions and Halloween Legacy','min_format':[97,1],'max_format':[97,1]}}).encode(),
            'LICENSE.txt':b'Original CosmeticPets Christmas models and textures: MIT License.\n'}
    for pet in sorted(keep):
        for path in ('assets/cosmeticpets/items/'+pet+'.json','assets/cosmeticpets/models/pet/'+pet+'.json'):
            result[path]=source[path]
    for species,builder in (('reindeer',reindeer_walk_model),('yeti',yeti_walk_model),('capybara',lambda f:capy_model(walk=f))):
        for frame in range(24 if species=="capybara" else 12):
            pet=species+'_walk_'+str(frame)
            result['assets/cosmeticpets/items/'+pet+'.json']=json.dumps({'model':{'type':'minecraft:model','model':'cosmeticpets:pet/'+pet}}).encode()
            result['assets/cosmeticpets/models/pet/'+pet+'.json']=json.dumps(builder(frame)).encode()
    for texture in sorted(textures):
        path='assets/'+texture.replace(':','/textures/')+'.png'
        result[path]=source[path]
    result['assets/minecraft/atlases/items.json']=json.dumps({'sources':[
        {'type':'minecraft:single','resource':t,'sprite':t} for t in sorted(textures)]}).encode()
    for frame in range(6):
        name='capybara_idle_'+str(frame)
        result['assets/cosmeticpets/items/'+name+'.json']=json.dumps({'model':{'type':'minecraft:model','model':'cosmeticpets:pet/'+name}}).encode()
        result['assets/cosmeticpets/models/pet/'+name+'.json']=json.dumps(capy_model(idle=frame)).encode()
    # A literal black question mark for locked menu entries, without custom fonts.
    question=[]
    for a,b in [([5,12,7],[11,14,9]),([9,9,7],[11,12,9]),([7,7,7],[11,9,9]),([7,5,7],[9,7,9]),([7,1,7],[9,3,9])]:
        question.append(cube(a,b,'black'))
    result['assets/cosmeticpets/models/pet/locked.json']=json.dumps({'textures':{'black':'cosmeticpets:pet/locked_black'},'elements':question,'display':{'fixed':{'rotation':[0,0,0],'translation':[0,8,0],'scale':[1,1,1]},'gui':{'rotation':[0,0,0],'translation':[0,0,0],'scale':[1,1,1]}}}).encode()
    result['assets/cosmeticpets/items/locked.json']=json.dumps({'model':{'type':'minecraft:model','model':'cosmeticpets:pet/locked'}}).encode()
    result['assets/cosmeticpets/textures/pet/locked_black.png']=png((0,0,0,255))
    atlas=json.loads(result['assets/minecraft/atlases/items.json'])
    atlas['sources'].append({'type':'minecraft:single','resource':'cosmeticpets:pet/locked_black','sprite':'cosmeticpets:pet/locked_black'})
    result['assets/minecraft/atlases/items.json']=json.dumps(atlas).encode()
    for path,data in list(result.items()):
        if path.startswith('assets/cosmeticpets/models/pet/') and path.endswith('.json') and not path.endswith('/locked.json'):
            model=json.loads(data)
            model.setdefault('display',{})['gui']={'rotation':[20,-35,0],'translation':[0,-1,0],'scale':[.8,.8,.8]}
            result[path]=json.dumps(model).encode()
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
