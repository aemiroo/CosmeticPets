"""Build an original voxel ghost pack without third-party image/model assets."""
import hashlib, json, pathlib, struct, zlib, zipfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
def png(color):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    raw = b''.join(b'\0' + bytes(color) * 16 for _ in range(16))
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 16,16,8,6,0,0,0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND',b'')
def cube(start, end, texture='white'):
    return {'from': start, 'to': end, 'faces': {face: {'uv':[0,0,16,16], 'texture':'#'+texture} for face in ('north','south','east','west','up','down')}}
def files():
    elements = [cube([3,4,3],[13,13,13]), cube([4,13,4],[12,14,12]),
                cube([3,2,3],[5,4,13]), cube([7,1,3],[9,4,13]), cube([11,2,3],[13,4,13]),
                cube([1,7,6],[3,10,10]), cube([13,7,6],[15,10,10]),
                cube([5,9,2.85],[6.5,11,3],'dark'), cube([9.5,9,2.85],[11,11,3],'dark'),
                cube([7.25,6.5,2.85],[8.75,8,3],'dark'),
                cube([4,7.5,2.8],[5.5,8,3],'pink'), cube([10.5,7.5,2.8],[12,8,3],'pink')]
    model = {'credit':'Original CosmeticPets ghost; no Sketchfab assets used.', 'textures': {x:'cosmeticpets:pet/'+x for x in ('white','dark','pink')}, 'elements':elements,
             'display': {'fixed': {'rotation':[0,0,0], 'translation':[0,0,0], 'scale':[1,1,1]}}, 'gui_light':'front'}
    result = {
        'pack.mcmeta': json.dumps({'pack':{'description':'CosmeticPets - original floating ghost', 'min_format':[97,1], 'max_format':[97,1]}}).encode(),
        'assets/minecraft/atlases/items.json': json.dumps({'sources': [
            {'type':'minecraft:single', 'resource':'cosmeticpets:pet/'+name,
             'sprite':'cosmeticpets:pet/'+name} for name in ('white','dark','pink')
        ]}).encode(),
        'assets/cosmeticpets/items/ghost.json': json.dumps({'model':{'type':'minecraft:model','model':'cosmeticpets:pet/ghost'}}).encode(),
        'assets/cosmeticpets/models/pet/ghost.json':json.dumps(model).encode(),
        'assets/cosmeticpets/textures/pet/white.png':png((236,244,250,255)),
        'assets/cosmeticpets/textures/pet/dark.png':png((31,25,49,255)),
        'assets/cosmeticpets/textures/pet/pink.png':png((214,154,190,255)),
        'LICENSE.txt': b'Original ghost model and textures: MIT License, same as the CosmeticPets repository. No third-party models or textures included.\n'
    }
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
