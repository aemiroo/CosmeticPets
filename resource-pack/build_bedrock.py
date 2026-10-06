"""Port our Java surface models to Bedrock attachables for GeyserDisplayEntity.

The extension and its own resource pack are installed separately; neither is
bundled here. All generated model/texture content remains original MIT content.
"""
import json, struct, zlib, zipfile
from build_pack import ROOT, files as java_files

PETS = ('ghost', 'pumpkin')

def encoded(value):
    return json.dumps(value, indent=2).encode()

def color(data):
    # build_pack emits solid RGBA PNGs with a single IDAT and filter-zero rows.
    pos = 8
    while pos < len(data):
        length = struct.unpack('>I', data[pos:pos+4])[0]
        if data[pos+4:pos+8] == b'IDAT':
            return zlib.decompress(data[pos+8:pos+8+length])[1:5]
        pos += 12 + length
    raise ValueError('Missing PNG pixels')

def atlas(colors):
    def chunk(kind, data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    width = 16 * len(colors)
    row = b''.join(c*16 for c in colors)
    raw = b''.join(b'\0'+row for _ in range(16))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,16,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')

def geometry(pet, model, names):
    cubes = []
    translate = model['display']['fixed']['translation']
    for element in model['elements']:
        a, b = element['from'], element['to']
        uv = {}
        for face, definition in element['faces'].items():
            # Mirroring Java's X axis swaps east and west; north stays -Z.
            bedrock_face = {'east':'west','west':'east'}.get(face,face)
            tile = names.index(definition['texture'][1:])
            uv[bedrock_face] = {'uv':[tile*16,0], 'uv_size':[16,16]}
        cubes.append({'origin':[8-b[0]-translate[0],a[1]+translate[1],a[2]-8+translate[2]],
                      'size':[b[i]-a[i] for i in range(3)],'uv':uv})
    # The extension's geyser_z bone is at Y=8, with mapping y-offset=-0.5.
    # This keeps Java's item centre (and pumpkin's fixed translation) aligned.
    return {'format_version':'1.16.0','minecraft:geometry':[{
        'description':{'identifier':'geometry.cosmeticpets.'+pet,
                       'texture_width':16*len(names),'texture_height':16,
                       'visible_bounds_width':3,'visible_bounds_height':3,
                       'visible_bounds_offset':[0,0.5,0]},
        'bones':[{'name':'pet','binding':"'geyser_z'",'pivot':[0,8,0],'cubes':cubes}]}]}

def files():
    source = java_files()
    result = {'manifest.json':encoded({'format_version':2,
        'header':{'name':'CosmeticPets Bedrock','description':'Original ghost and bouncing pumpkin companions',
                  'uuid':'507ee74f-7d83-4f1d-8bdb-85b28f28796f','version':[1,2,3],'min_engine_version':[1,21,0]},
        'modules':[{'type':'resources','uuid':'ea7e3a8b-f04e-4423-ae3c-8f79a89ad251','version':[1,2,3]}]}),
        'LICENSE.txt':source['LICENSE.txt'],
        'render_controllers/cosmeticpets.json':encoded({'format_version':'1.8.0','render_controllers':{
            'controller.render.cosmeticpets':{'geometry':'Geometry.default',
                'materials':[{'*':'Material.default'}],'textures':['Texture.default']}}})}
    texture_data = {}
    for pet in PETS:
        model = json.loads(source['assets/cosmeticpets/models/pet/'+pet+'.json'])
        names = list(model['textures'])
        colors = [color(source['assets/'+model['textures'][n].replace(':','/textures/')+'.png']) for n in names]
        result['textures/cosmeticpets/'+pet+'.png'] = atlas(colors)
        result['models/entity/'+pet+'.geo.json'] = encoded(geometry(pet,model,names))
        result['attachables/'+pet+'.json'] = encoded({'format_version':'1.10.0','minecraft:attachable':{
            'description':{'identifier':'cosmeticpets:'+pet,
                'materials':{'default':'entity_alphablend' if pet=='ghost' else 'entity_alphatest'},
                'textures':{'default':'textures/cosmeticpets/'+pet},
                'geometry':{'default':'geometry.cosmeticpets.'+pet},
                'render_controllers':['controller.render.cosmeticpets']}}})
        texture_data['cosmeticpets.'+pet] = {'textures':'textures/cosmeticpets/'+pet}
    result['textures/item_texture.json'] = encoded({'resource_pack_name':'CosmeticPets','texture_name':'atlas.items','texture_data':texture_data})
    return result

def mappings():
    return {'format_version':2,'items':{'minecraft:paper':[
        {'type':'definition','model':'cosmeticpets:'+pet,'bedrock_identifier':'cosmeticpets:'+pet,
         'display_name':pet.title()+' Companion'} for pet in PETS]}}

def display_mappings():
    return 'mappings:\n'+''.join('  cosmeticpets_'+pet+':\n    type: "minecraft:paper"\n    item-identifier: "cosmeticpets:'+pet+'"\n    displayentityoptions:\n      y-offset: -0.5\n      vanilla-scale: false\n      vanilla-scale-multiplier: 1\n      hand: false\n' for pet in PETS)

if __name__ == '__main__':
    target = ROOT/'target'
    target.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(target/'CosmeticPets-Bedrock.mcpack','w',zipfile.ZIP_DEFLATED) as archive:
        for name,data in sorted(files().items()):
            info=zipfile.ZipInfo(name,(2026,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,data)
    (target/'cosmeticpets-geyser-mappings.json').write_bytes(encoded(mappings()))
    (target/'cosmeticpets-display-mappings.yml').write_text(display_mappings())
    print('Built Bedrock pack and both Geyser mapping files')
