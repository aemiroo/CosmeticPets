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
            cubes=[cube for b in geometry['bones'] for cube in b['cubes']]
            self.assertEqual(len(original['elements']),len(cubes))
            self.assertEqual(sum(len(e['faces']) for e in original['elements']),sum(len(c['uv']) for c in cubes))
            for cube in cubes:
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
            self.assertTrue(any(attach['textures']['default']+ext in pack for ext in ('.png','.tga')))
            self.assertIn(attach['render_controllers'][0],controller)
            self.assertIn('cosmeticpets.'+pet,icons)

    def test_pumpkin_light_is_separate_emissive_geometry(self):
        pack=files()
        geometry=json.loads(pack['models/entity/pumpkin.geo.json'])['minecraft:geometry'][0]
        light=next(b for b in geometry['bones'] if b['name']=='pet_light')
        self.assertEqual('pet',light['parent'])
        self.assertTrue(light['cubes'])
        self.assertTrue(all(set(c['uv'])=={'north'} for c in light['cubes']))
        attach=json.loads(pack['attachables/pumpkin.json'])['minecraft:attachable']['description']
        self.assertEqual('entity_emissive',attach['materials']['glow'])
        controller=json.loads(pack['render_controllers/cosmeticpets.json'])['render_controllers'][attach['render_controllers'][0]]
        self.assertEqual({'pet_light':'Material.glow'},controller['materials'][-1])
        data=pack['textures/cosmeticpets/pumpkin.tga']
        self.assertEqual(2,data[2])
        self.assertEqual(32,data[16])
        names=list(json.loads(java_files()['assets/cosmeticpets/models/pet/pumpkin.json'])['textures'])
        self.assertEqual(0,data[18+names.index('pumpkin_glow')*16*4+3])

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
