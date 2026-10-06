import importlib.util,json,pathlib,unittest
spec=importlib.util.spec_from_file_location('builder',pathlib.Path(__file__).with_name('build_pack.py'))
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class PackTest(unittest.TestCase):
    def test_model_references_and_bounds(self):
        files=builder.files()
        item=json.loads(files['assets/cosmeticpets/items/ghost.json'])
        self.assertEqual('cosmeticpets:pet/ghost',item['model']['model'])
        model=json.loads(files['assets/cosmeticpets/models/pet/ghost.json'])
        for element in model['elements']:
            self.assertTrue(all(0 <= a < b <= 16 for a,b in zip(element['from'],element['to'])))
            for face in element['faces'].values():
                texture=model['textures'][face['texture'][1:]].replace(':','/textures/')
                self.assertIn('assets/'+texture+'.png',files)
        self.assertEqual([97,1],json.loads(files['pack.mcmeta'])['pack']['min_format'])
    def test_all_ghost_textures_registered_in_item_atlas(self):
        files=builder.files()
        model=json.loads(files['assets/cosmeticpets/models/pet/ghost.json'])
        atlas=json.loads(files['assets/minecraft/atlases/items.json'])
        sprites={}
        for source in atlas['sources']:
            self.assertEqual('minecraft:single',source['type'])
            namespace,path=source['resource'].split(':',1)
            self.assertIn('assets/'+namespace+'/textures/'+path+'.png',files)
            sprites[source['sprite']]=source['resource']
        self.assertEqual(set(model['textures'].values()),set(sprites))
    def test_reproducible_original_assets(self):
        self.assertEqual(builder.files(),builder.files())
        self.assertTrue(builder.files()['assets/cosmeticpets/textures/pet/white.png'].startswith(b'\x89PNG'))
if __name__=='__main__':unittest.main()
