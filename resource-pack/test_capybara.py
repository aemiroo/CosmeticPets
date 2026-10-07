import json, unittest
from build_pack import files, winter_model, walk_model, limb
from build_bedrock import files as bedrock_files

class CapybaraPackTest(unittest.TestCase):
    def test_capybara_has_four_legs_and_diagonal_gait(self):
        model=walk_model('capybara',3)
        legs={tuple(e['rotation']['origin']):e['rotation'] for e in model['elements'] if 'rotation' in e and e['rotation']['axis']=='x'}
        self.assertEqual(4,len(legs))
        self.assertEqual(legs[5,3,8]['angle'],legs[11,3,13]['angle'])
        self.assertEqual(-legs[5,3,8]['angle'],legs[5,3,13]['angle'])
        for frame in range(12):
            for e in walk_model('capybara',frame)['elements']:
                if 'rotation' in e:self.assertIn(e['rotation']['angle'],(-22.5,0,22.5))
    def test_idle_closes_only_side_eyes_and_keeps_body_still(self):
        from capybara_model import model
        neutral,closed=model(idle=0),model(idle=2)
        self.assertEqual([e['from'] for e in neutral['elements']],[e['from'] for e in closed['elements']])
        eyes=[e for e in closed['elements'] if any(f['texture']=='#capy_closed' for f in e['faces'].values())]
        self.assertEqual(1,len(eyes))
        self.assertEqual({'east','west'},{s for s,f in eyes[0]['faces'].items() if f['texture']=='#capy_closed'})
    def test_all_capybara_poses_and_locked_icon_resolve_in_both_packs(self):
        java,bedrock=files(),bedrock_files()
        for name in ['capybara','locked']+['capybara_walk_'+str(i) for i in range(12)]+['capybara_idle_'+str(i) for i in range(6)]:
            model=json.loads(java['assets/cosmeticpets/models/pet/'+name+'.json'])
            for texture in model['textures'].values():
                self.assertIn('assets/'+texture.replace(':','/textures/')+'.png',java)
            self.assertIn('attachables/'+name+'.json',bedrock)
