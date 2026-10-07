import json, unittest
from build_pack import files, winter_model, walk_model, limb
from build_bedrock import files as bedrock_files

class CapybaraPackTest(unittest.TestCase):
    def test_capybara_has_four_legs_and_diagonal_gait(self):
        model=walk_model('capybara',3)
        legs={limb('capybara',e['from']):e['rotation'] for e in model['elements'] if 'rotation' in e}
        self.assertEqual(4,len(legs))
        self.assertEqual(legs['leg',0,0]['angle'],legs['leg',1,1]['angle'])
        self.assertEqual(-legs['leg',0,0]['angle'],legs['leg',0,1]['angle'])
        for frame in range(12):
            for e in walk_model('capybara',frame)['elements']:
                if 'rotation' in e:self.assertIn(e['rotation']['angle'],(-22.5,0,22.5))
        self.assertLessEqual(max(e['to'][1] for e in winter_model('capybara')['elements']),11)
    def test_all_capybara_poses_and_locked_icon_resolve_in_both_packs(self):
        java,bedrock=files(),bedrock_files()
        for name in ['capybara','locked']+['capybara_walk_'+str(i) for i in range(12)]:
            model=json.loads(java['assets/cosmeticpets/models/pet/'+name+'.json'])
            for texture in model['textures'].values():
                self.assertIn('assets/'+texture.replace(':','/textures/')+'.png',java)
            self.assertIn('attachables/'+name+'.json',bedrock)
