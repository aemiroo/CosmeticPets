import json, unittest, uuid, struct, zlib
from build_bedrock import files, mappings, display_mappings, PETS
from build_pack import files as java_files

class BedrockPackTest(unittest.TestCase):
    def test_models_preserve_surface_faces_and_feet(self):
        pack, java = files(), java_files()
        for pet in PETS:
            original=json.loads(java['assets/cosmeticpets/models/pet/'+pet+'.json'])
            geometry=json.loads(pack['models/entity/'+pet+'.geo.json'])['minecraft:geometry'][0]
            bone=geometry['bones'][0]
            self.assertEqual("'geyser_z'",bone['binding'])
            self.assertEqual(len(original['elements']),len(bone['cubes']))
            self.assertEqual(sum(len(e['faces']) for e in original['elements']),sum(len(c['uv']) for c in bone['cubes']))
            for cube in bone['cubes']:
                for face in cube['uv'].values():
                    self.assertLessEqual(face['uv'][0]+16,geometry['description']['texture_width'])
            if pet=='pumpkin':
                self.assertEqual(8,min(c['origin'][1] for c in bone['cubes']))

    def test_mappings_and_render_references_agree(self):
        pack=files()
        definitions=mappings()['items']['minecraft:paper']
        self.assertEqual(2,mappings()['format_version'])
        controller=json.loads(pack['render_controllers/cosmeticpets.json'])['render_controllers']
        icons=json.loads(pack['textures/item_texture.json'])['texture_data']
        for pet,definition in zip(PETS,definitions):
            attach=json.loads(pack['attachables/'+pet+'.json'])['minecraft:attachable']['description']
            self.assertEqual(definition['bedrock_identifier'],attach['identifier'])
            self.assertEqual('cosmeticpets:'+pet,definition['model'])
            self.assertIn('item-identifier: "'+definition['bedrock_identifier']+'"',display_mappings())
            self.assertIn(attach['textures']['default']+'.png',pack)
            self.assertIn(attach['render_controllers'][0],controller)
            self.assertIn('cosmeticpets.'+pet,icons)

    def test_manifest_and_translucent_texture(self):
        pack=files()
        manifest=json.loads(pack['manifest.json'])
        self.assertNotEqual(uuid.UUID(manifest['header']['uuid']),uuid.UUID(manifest['modules'][0]['uuid']))
        self.assertEqual('resources',manifest['modules'][0]['type'])
        data=pack['textures/cosmeticpets/ghost.png']
        self.assertEqual((64,16),struct.unpack('>II',data[16:24]))
        pos=8
        while data[pos+4:pos+8]!=b'IDAT': pos+=12+struct.unpack('>I',data[pos:pos+4])[0]
        length=struct.unpack('>I',data[pos:pos+4])[0]
        pixels=zlib.decompress(data[pos+8:pos+8+length])
        self.assertEqual(110,pixels[4])
        attach=json.loads(pack['attachables/ghost.json'])['minecraft:attachable']['description']
        self.assertEqual('entity_alphablend',attach['materials']['default'])

if __name__=='__main__': unittest.main()
