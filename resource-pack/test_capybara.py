import json, unittest
from build_pack import files, winter_model, walk_model, limb
from build_bedrock import files as bedrock_files

class CapybaraPackTest(unittest.TestCase):
    def test_capybara_has_four_legs_and_diagonal_gait(self):
        model=walk_model('capybara',6)
        legs={tuple(e['rotation']['origin']):e['rotation'] for e in model['elements'] if 'rotation' in e and e['rotation']['axis']=='x' and e['rotation']['origin'][1]==5}
        self.assertEqual(4,len(legs))
        self.assertEqual(legs[5,5,8]['angle'],legs[11,5,13]['angle'])
        self.assertEqual(-legs[5,5,8]['angle'],legs[5,5,13]['angle'])
        for frame in range(24):
            for e in walk_model('capybara',frame)['elements']:
                if 'rotation' in e:self.assertLessEqual(abs(e['rotation']['angle']),22.5)
    def test_gait_has_small_steps_and_keeps_body_still(self):
        from capybara_model import model
        poses=[model(walk=i) for i in range(24)]
        for a,b in zip(poses,poses[1:]+poses[:1]):
            self.assertEqual(a['elements'][:7],b['elements'][:7])
            for old,new in zip(a['elements'],b['elements']):
                if old.get('rotation',{}).get('axis')=='x':
                    self.assertLess(abs(old['rotation']['angle']-new['rotation']['angle']),5)
    def test_reference_proportions_and_rare_blink(self):
        from capybara_model import model
        neutral,closed=model(idle=0),model(idle=2)
        body=neutral['elements'][0]
        self.assertEqual(13,body['to'][1])
        self.assertEqual(14,neutral['elements'][1]['to'][1])
        def eyes(m):return [e for e in m['elements'] if any(f['texture'] in ('#capy_eye','#capy_white') for f in e['faces'].values())]
        self.assertEqual(4,len(eyes(neutral)))
        for a,b in zip(eyes(neutral),eyes(closed)):
            self.assertEqual(a['from'],b['from'])
            self.assertLess(b['to'][1]-b['from'][1],a['to'][1]-a['from'][1])
        self.assertEqual(neutral['elements'][:3],closed['elements'][:3])
        self.assertEqual('#capy_muzzle',neutral['elements'][2]['faces']['up']['texture'])
    def test_all_capybara_poses_and_locked_icon_resolve_in_both_packs(self):
        java,bedrock=files(),bedrock_files()
        for name in ['capybara','locked']+['capybara_walk_'+str(i) for i in range(24)]+['capybara_idle_'+str(i) for i in range(6)]:
            model=json.loads(java['assets/cosmeticpets/models/pet/'+name+'.json'])
            for texture in model['textures'].values():
                self.assertIn('assets/'+texture.replace(':','/textures/')+'.png',java)
            self.assertIn('attachables/'+name+'.json',bedrock)
