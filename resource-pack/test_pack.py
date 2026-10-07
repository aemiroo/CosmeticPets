import importlib.util,json,pathlib,unittest,struct,zlib
spec=importlib.util.spec_from_file_location('builder',pathlib.Path(__file__).with_name('build_pack.py'))
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class PackTest(unittest.TestCase):
    def test_model_references_and_bounds(self):
        files=builder.legacy_files()
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
        files=builder.legacy_files()
        model=json.loads(files['assets/cosmeticpets/models/pet/ghost.json'])
        atlas=json.loads(files['assets/minecraft/atlases/items.json'])
        sprites={}
        for source in atlas['sources']:
            self.assertEqual('minecraft:single',source['type'])
            namespace,path=source['resource'].split(':',1)
            self.assertIn('assets/'+namespace+'/textures/'+path+'.png',files)
            sprites[source['sprite']]=source['resource']
        self.assertTrue(set(model['textures'].values()).issubset(set(sprites)))
    def test_body_png_has_partial_alpha(self):
        data=builder.legacy_files()['assets/cosmeticpets/textures/pet/white.png']
        offset=8
        compressed=b''
        while offset<len(data):
            length=struct.unpack('>I',data[offset:offset+4])[0]
            kind=data[offset+4:offset+8]
            if kind==b'IDAT':
                compressed+=data[offset+8:offset+8+length]
            offset+=length+12
        raw=zlib.decompress(compressed)
        for row in range(16):
            self.assertEqual(0,raw[row*65])
            for column in range(16):
                self.assertEqual(110,raw[row*65+1+column*4+3])
    def test_fringe_follows_perimeter_instead_of_crossing_underside(self):
        fringe=[element for element in builder.shell() if element['from'][1]<4]
        self.assertTrue(fringe)
        for element in fringe:
            x,y,z=element['from']
            self.assertTrue(x in (3,12) or z in (3,12))
        self.assertTrue(any(element['from'][2]==3 for element in fringe))
        self.assertTrue(any(element['from'][2]==12 for element in fringe))
        self.assertTrue(any(element['from'][0]==3 for element in fringe))
        self.assertTrue(any(element['from'][0]==12 for element in fringe))
    def test_shell_does_not_emit_internal_shared_faces(self):
        faces=set()
        delta={'west':(-1,0,0),'east':(1,0,0),'down':(0,-1,0),'up':(0,1,0),
               'north':(0,0,-1),'south':(0,0,1)}
        opposite={'west':'east','east':'west','down':'up','up':'down','north':'south','south':'north'}
        for element in builder.shell():
            x,y,z=element['from']
            for face in element['faces']:
                faces.add((x,y,z,face))
        for x,y,z,face in faces:
            dx,dy,dz=delta[face]
            self.assertNotIn((x+dx,y+dy,z+dz,opposite[face]),faces)
    def test_pumpkin_assets_atlas_and_bounds(self):
        files=builder.legacy_files()
        model=json.loads(files['assets/cosmeticpets/models/pet/pumpkin.json'])
        item=json.loads(files['assets/cosmeticpets/items/pumpkin.json'])
        self.assertEqual('cosmeticpets:pet/pumpkin',item['model']['model'])
        atlas=json.loads(files['assets/minecraft/atlases/items.json'])
        sprites={source['sprite'] for source in atlas['sources']}
        for texture in model['textures'].values():
            self.assertIn(texture,sprites)
            namespace,path=texture.split(':',1)
            self.assertIn('assets/'+namespace+'/textures/'+path+'.png',files)
        for element in model['elements']:
            self.assertTrue(all(0<=a<b<=16 for a,b in zip(element['from'],element['to'])))
        self.assertEqual([0,6,0],model['display']['fixed']['translation'])
    def test_pumpkin_round_body_narrows_toward_top_and_bottom(self):
        elements=builder.pumpkin_model()['elements']
        body=[e for e in elements if any(f['texture'] in ('#pumpkin_orange','#pumpkin_rib') for f in e['faces'].values())]
        def width(y):
            layer=[e for e in body if e['from'][1]==y]
            return max(e['to'][0] for e in layer)-min(e['from'][0] for e in layer)
        self.assertLess(width(2),width(7))
        self.assertLess(width(12),width(7))
    def test_pumpkin_carved_openings_keep_face_design(self):
        model=builder.pumpkin_model()
        painted={(e['from'][0],e['from'][1]) for e in model['elements']
                 if e['faces'].get('north',{}).get('texture')=='#pumpkin_glow'}
        expected={(5,10),(10,10),(5,9),(6,9),(9,9),(10,9)}
        expected |= {(x,8) for x in (4,5,6,9,10,11)}
        expected |= {(7,7),(8,7),(7,6)}
        expected |= {(x,4) for x in range(4,12) if x not in (6,9)}
        expected |= {(x,3) for x in range(5,11)} | {(4,5),(11,5)}
        self.assertEqual(expected,painted)
        for element in model['elements']:
            for face,definition in element['faces'].items():
                if definition['texture']=='#pumpkin_glow':
                    self.assertEqual('north',face)

    def test_pumpkin_face_follows_rounded_body_without_flat_cut(self):
        elements=builder.pumpkin_model()['elements']
        front={(e['from'][0],e['from'][1]):e['from'][2]
               for e in elements if 'north' in e['faces']}
        back={(e['from'][0],e['from'][1]):e['to'][2]
              for e in elements if 'south' in e['faces']}
        lit={(e['from'][0],e['from'][1]) for e in elements if e.get('light_emission')==15}
        # Only the carved pixels move inward; uncarved rind stays rounded.
        for x in range(4,12):
            for y in range(4,11):
                self.assertEqual(19 if (x,y) in lit else 16,front[x,y]+back[x,y])
        self.assertLess(front[7,9],front[4,9])
        painted=[e for e in elements
                 if e['faces'].get('north',{}).get('texture')=='#pumpkin_glow']
        self.assertGreater(len({e['from'][2] for e in painted}),1)

    def test_carved_face_has_depth_walls_and_emissive_backing(self):
        elements=builder.pumpkin_model()['elements']
        glow=[e for e in elements if e.get('light_emission')==15]
        self.assertTrue(glow)
        occupied={tuple(e['from']) for e in elements}
        for element in glow:
            x,y,z=element['from']
            self.assertEqual({'north'},set(element['faces']))
            self.assertFalse(element['shade'])
            for depth in (1,2,3):
                self.assertNotIn((x,y,z-depth),occupied)
        walls=[e for e in elements if any(f['texture']=='#pumpkin_inner'
                                         for f in e['faces'].values())]
        self.assertTrue(walls)
        self.assertTrue(any(set(e['faces']) & {'up','down','east','west'} for e in walls))
        self.assertTrue(all(not e.get('light_emission') for e in walls))

    def test_pumpkin_union_has_no_duplicate_or_internal_faces(self):
        model=builder.pumpkin_model()
        seen=set()
        delta={'west':(-1,0,0),'east':(1,0,0),'down':(0,-1,0),'up':(0,1,0),
               'north':(0,0,-1),'south':(0,0,1)}
        opposite={'west':'east','east':'west','down':'up','up':'down','north':'south','south':'north'}
        for element in model['elements']:
            x,y,z=element['from']
            self.assertEqual([x+1,y+1,z+1],element['to'])
            for face in element['faces']:
                key=(x,y,z,face)
                self.assertNotIn(key,seen)
                seen.add(key)
        for x,y,z,face in seen:
            dx,dy,dz=delta[face]
            self.assertNotIn((x+dx,y+dy,z+dz,opposite[face]),seen)
        green_tops=[e for e in model['elements'] if e['from'][1]==12
                     and e['faces'].get('up',{}).get('texture')=='#pumpkin_green']
        self.assertTrue(green_tops)

    def test_reproducible_original_assets(self):
        self.assertEqual(builder.legacy_files(),builder.legacy_files())
        self.assertTrue(builder.legacy_files()['assets/cosmeticpets/textures/pet/white.png'].startswith(b'\x89PNG'))
if __name__=='__main__':unittest.main()
