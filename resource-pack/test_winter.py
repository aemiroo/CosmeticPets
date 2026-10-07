import json, unittest
from build_pack import files, winter_model, reindeer_walk_model
from build_bedrock import files as bedrock_files, mappings
class WinterPackTest(unittest.TestCase):
    def test_only_christmas_models_are_published(self):
        java,bedrock=files(),bedrock_files()
        self.assertEqual({'snowman','reindeer','yeti'}|{'reindeer_walk_'+str(i) for i in range(12)},{p.split('/')[-1][:-5] for p in java if p.startswith('assets/cosmeticpets/items/')})
        self.assertEqual({'snowman','reindeer'}|{'reindeer_walk_'+str(i) for i in range(12)},{p.split('/')[-1][:-5] for p in bedrock if p.startswith('attachables/')})
        self.assertEqual(15,len(mappings()['items']['minecraft:paper']))
    def test_gait_moves_only_legs_and_keeps_them_in_collision_bounds(self):
        idle=winter_model('reindeer')
        for frame in range(12):
            pose=reindeer_walk_model(frame)
            self.assertEqual(len(idle['elements']),len(pose['elements']))
            for original,animated in zip(idle['elements'],pose['elements']):
                x,y,z=original['from']
                if not (y<5 and x in (5,10) and z in (7,11)):
                    self.assertEqual(original,animated)
                for bound in ('from','to'):
                    self.assertTrue(all(0<=v<=16 for v in animated[bound]))
        self.assertEqual(idle['elements'],reindeer_walk_model(0)['elements'])
        self.assertNotEqual(reindeer_walk_model(3)['elements'],reindeer_walk_model(9)['elements'])
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
