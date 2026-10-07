import json, unittest
from build_pack import files, winter_model, reindeer_walk_model, yeti_walk_model, limb
from build_bedrock import files as bedrock_files, mappings
class WinterPackTest(unittest.TestCase):
    def test_only_christmas_models_are_published(self):
        java,bedrock=files(),bedrock_files()
        self.assertEqual({'snowman','reindeer','yeti'}|{pet+'_walk_'+str(i) for pet in ('reindeer','yeti') for i in range(12)},{p.split('/')[-1][:-5] for p in java if p.startswith('assets/cosmeticpets/items/')})
        self.assertEqual({'snowman','reindeer','yeti'}|{pet+'_walk_'+str(i) for pet in ('reindeer','yeti') for i in range(12)},{p.split('/')[-1][:-5] for p in bedrock if p.startswith('attachables/')})
        self.assertEqual(27,len(mappings()['items']['minecraft:paper']))
    def test_joint_rotations_preserve_limb_shape_and_opposite_gait(self):
        for pet,builder in (('reindeer',reindeer_walk_model),('yeti',yeti_walk_model)):
            neutral=builder(0)
            for frame in range(12):
                pose=builder(frame)
                if pet=='yeti':
                    arm_angles={limb(pet,e['from']):e['rotation']['angle']
                                for e in pose['elements']
                                if limb(pet,e['from']) in (('arm',0),('arm',1))}
                    self.assertEqual(arm_angles['arm',0],arm_angles['arm',1])
                for old,new in zip(neutral['elements'],pose['elements']):
                    self.assertEqual(old['from'],new['from'])
                    self.assertEqual(old['to'],new['to'])
                    self.assertEqual(old['faces'],new['faces'])
                    if limb(pet,old['from']) is None:
                        self.assertEqual(old,new)
                    else:
                        self.assertEqual('x',new['rotation']['axis'])
                        self.assertLessEqual(abs(new['rotation']['angle']),28)
            angles={limb(pet,e['from']):e['rotation']['angle']
                    for e in builder(3)['elements'] if 'rotation' in e}
            if pet=='yeti':
                self.assertEqual(-angles['leg',0],angles['leg',1])
                self.assertEqual(angles['arm',0],angles['arm',1])
                self.assertLess(angles['arm',0]*angles['leg',0],0)
            else:
                self.assertEqual(angles['leg',5,7],angles['leg',10,11])
                self.assertEqual(-angles['leg',5,7],angles['leg',5,11])
    def test_bedrock_retains_every_joint_pivot_and_rotation(self):
        java,bedrock=files(),bedrock_files()
        for pet in ('yeti_walk_3','reindeer_walk_3'):
            model=json.loads(java['assets/cosmeticpets/models/pet/'+pet+'.json'])
            geo=json.loads(bedrock['models/entity/'+pet+'.geo.json'])
            cubes=geo['minecraft:geometry'][0]['bones'][0]['cubes']
            for element,cube in zip(model['elements'],cubes):
                if 'rotation' not in element:
                    self.assertNotIn('rotation',cube)
                    continue
                r=element['rotation'];x,y,z=r['origin']
                self.assertEqual([8-x,y+8,z-8],cube['pivot'])
                self.assertEqual([-r['angle'],0,0],cube['rotation'])
    def test_yeti_has_flat_face_side_horns_and_patterned_fur(self):
        model=winter_model('yeti')
        cells={tuple(e['from']):e for e in model['elements']}
        face_textures={'#yeti_face','#yeti_blue','#coal','#yeti_nose','#yeti_smile'}
        facial=[e for e in model['elements'] if any(f['texture'] in face_textures for f in e['faces'].values())]
        self.assertTrue(facial)
        self.assertTrue(all(e['from'][2]==4 for e in facial))
        self.assertIn('yeti_fur_shadow',model['textures'])
        self.assertIn('yeti_fur_light',model['textures'])
        self.assertEqual(14,max(e['to'][1] for e in model['elements']))
    def test_yeti_walking_moves_limbs_and_horns_project_forward(self):
        idle=winter_model('yeti')
        self.assertTrue(all(e.get('rotation',{}).get('angle',0)==0 for e in yeti_walk_model(0)['elements']))
        self.assertNotEqual(yeti_walk_model(3)['elements'],yeti_walk_model(9)['elements'])
        for frame in range(12):
            for old,new in zip(yeti_walk_model(0)['elements'],yeti_walk_model(frame)['elements']):
                if any(face['texture']=='#yeti_horn' for face in old['faces'].values()):
                    self.assertEqual(old,new)
        horns=[e for e in idle['elements'] if any(f['texture']=='#yeti_horn' for f in e['faces'].values())]
        self.assertEqual(2,min(e['from'][2] for e in horns))
        self.assertEqual(8,max(e['to'][2] for e in horns))
    def test_surface_union_has_no_internal_or_duplicate_faces(self):
        for pet in ('snowman','reindeer','yeti'):
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
        for pet in ('snowman','reindeer','yeti'):
            self.assertIn('assets/cosmeticpets/items/'+pet+'.json',java)
            attach=json.loads(bedrock['attachables/'+pet+'.json'])['minecraft:attachable']['description']
            self.assertEqual({'default':'entity_alphatest'},attach['materials'])
            self.assertIn('cosmeticpets:'+pet,[m['bedrock_identifier'] for m in mappings()['items']['minecraft:paper']])
