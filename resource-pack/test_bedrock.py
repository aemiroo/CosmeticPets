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



if __name__=='__main__': unittest.main()
