import json, unittest
from build_pack import files, winter_model
from build_bedrock import files as bedrock_files, mappings
class WinterPackTest(unittest.TestCase):
    def test_surface_union_has_no_internal_or_duplicate_faces(self):
        for pet in ('snowman','reindeer'):
            model=winter_model(pet)
            origins={tuple(e['from']) for e in model['elements']}
            self.assertEqual(len(origins),len(model['elements']))
            directions={'west':(-1,0,0),'east':(1,0,0),'down':(0,-1,0),'up':(0,1,0),'north':(0,0,-1),'south':(0,0,1)}
            for e in model['elements']:
                for face in e['faces']:
                    neighbor=tuple(v+d for v,d in zip(e['from'],directions[face]))
                    self.assertNotIn(neighbor,origins)
            self.assertEqual(0,min(e['from'][1] for e in model['elements']))
            self.assertTrue(all(0<=v<=16 for e in model['elements'] for bound in ('from','to') for v in e[bound]))
    def test_winter_models_exist_in_both_packs_and_mappings(self):
        java,bedrock=files(),bedrock_files()
        for pet in ('snowman','reindeer'):
            self.assertIn('assets/cosmeticpets/items/'+pet+'.json',java)
            attach=json.loads(bedrock['attachables/'+pet+'.json'])['minecraft:attachable']['description']
            self.assertEqual({'default':'entity_alphatest'},attach['materials'])
            self.assertIn('cosmeticpets:'+pet,[m['bedrock_identifier'] for m in mappings()['items']['minecraft:paper']])
