#!/usr/bin/env python3
"""Offline package QA. `python3 -m unittest discover -s Tests -v` from root."""
import csv,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'Hardware'),str(ROOT/'Vital')]
from apply_to_mpk249_dump import apply,validate
from install_vital_mappings import update

class TestZeroRepetitiveMapping(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.hardware=json.loads((ROOT/'Hardware/MPKUNIV2.mapping.json').read_text())
  cls.controls=cls.hardware['assignments']
  cls.vital=json.loads((ROOT/'Vital/desired_midi_learn.json').read_text())
  cls.vcv=json.loads((ROOT/'VCV_Rack/MPK249_Play_Now_legacy.vcv').read_text())
  cls.bespoke=json.loads((ROOT/'Bespoke/MPK249_Universal_v2.controller.json').read_text())
 def test_hardware_complete(self):
  self.assertEqual(len(self.controls),141)
  self.assertEqual(len([x for x in self.controls if x['type']=='Pad']),64)
  self.assertEqual(len([x for x in self.controls if x['type']=='Switch']),24)
  self.assertEqual(len([x for x in self.controls if x['type']=='Knob']),24)
  self.assertEqual(len([x for x in self.controls if x['type']=='Fader']),24)
  self.assertEqual(len([x for x in self.controls if x['type']=='Navigation']),5)
  ccs=[c['cc'] for c in self.controls if 'cc' in c]
  self.assertEqual(len(set(ccs)),77)
  self.assertTrue(all(c['channel']==2 for c in self.controls if c['type'] not in ('Pad',)))
  self.assertFalse(set(ccs)&set(range(32,40)))
 def test_synth_one_defaults(self):
  knobs={a['index']:a['cc'] for a in self.controls if a['bank']=='A' and a['type']=='Knob'}
  self.assertEqual(knobs[1],74);self.assertEqual(knobs[2],71)
  pads={a['channel'] for a in self.controls if a['bank']=='A' and a['type']=='Pad'}
  self.assertEqual(pads,{1})
 def test_hardware_dump_patcher(self):
  fixture=bytearray(1550);fixture[:4]=bytes((240,71,0,36));fixture[7]=29;fixture[-1]=247
  output=apply(bytes(fixture),self.hardware,slot=30)
  self.assertEqual(len(output),len(fixture));self.assertEqual(output[8:16],b'MPKUNIV2')
  self.assertEqual(output[0x2FD+2],74)
  self.assertEqual(output[0x2FD+9+2],71)
  self.assertEqual(output[0x2FD+23*9+2],117)
  self.assertEqual(output[0x3D5+23*6+2],47)
  self.assertEqual(output[0x465+23*13+2],55)
  self.assertEqual(output[0x59D+4*13+2],60)
  self.assertEqual(output[0x3D+63*11+2],75)
  self.assertEqual(output[7],29);self.assertEqual(fixture[8:16],b'\0'*8)
  bad=bytearray(fixture);bad[3]=0x25
  with self.assertRaises(ValueError):validate(bad)
 def test_vital_unique_mapping_and_merge(self):
  self.assertGreaterEqual(len(self.vital),40)
  sources=[m['source'] for m in self.vital]
  dests=[x['destination'] for m in self.vital for x in m['destinations']]
  self.assertEqual(len(set(sources)),len(sources))
  self.assertEqual(len(set(dests)),len(dests))
  old={'author':'tester','midi_learn':[{'source':2,'destinations':[{'destination':'filter_1_cutoff'},{'destination':'other_custom'}]},{'source':99,'destinations':[{'destination':'unrelated'}]}]}
  result,replaced=update(old,self.vital)
  self.assertEqual(result['author'],'tester')
  self.assertTrue(any(m['source']==99 for m in result['midi_learn']))
  self.assertTrue(any(m['source']==2 and m['destinations']==[{'destination':'other_custom'}] for m in result['midi_learn']))
  self.assertEqual(sum(m['source']==74 for m in result['midi_learn']),1)
  self.assertTrue(replaced)
 def test_vcv_playable_and_mapped(self):
  modules={m['id']:m for m in self.vcv['modules']}
  self.assertGreaterEqual(len(modules),10)
  self.assertGreaterEqual(len(self.vcv['cables']),12)
  for c in self.vcv['cables']:
   self.assertIn(c['inputModuleId'],modules);self.assertIn(c['outputModuleId'],modules)
  ccmap=[m for m in modules.values() if m['model']=='MIDI-Map'][0]['data']['maps']
  self.assertEqual(len([x for x in ccmap if x['cc']>=0]),16)
  self.assertEqual({x['cc'] for x in ccmap if x['cc']>=0},{74,71,18,19,20,21,22,23,24,25,26,27,28,29,30,31})
  self.assertEqual(len([x for x in modules.values() if x['plugin']=='Core' and 'midi' in x.get('data',{})]),2)
 def test_bespoke_graphics_and_batch(self):
  self.assertEqual(len(self.bespoke['groups']),11)
  script=(ROOT/'Bespoke/One_Click_Bindings.py').read_text()
  compile(script,'Bespoke/One_Click_Bindings.py','exec')
  self.assertIn('controller.set_connection',script)
  self.assertIn("(74,  'fmax'",script)
 def test_supercollider_live_controls(self):
  t=(ROOT/'SuperCollider/MPK249_Play_Now.scd').read_text()
  for name in ['MIDIdef.cc','MIDIdef.noteOn','MIDIdef.noteOff','SynthDef(','[74,\\cutoff','[71,\\resonance','[110,\\cutoff']:
   self.assertIn(name,t)
 def test_installer_non_destructive_dry_run(self):
  with tempfile.TemporaryDirectory() as d:
   env=dict(os.environ, HOME=d)
   p=subprocess.run([sys.executable,str(ROOT/'Tools/install_mac.py')],capture_output=True,text=True,env=env,check=True)
   self.assertIn('PREVIEW ONLY',p.stdout)
   self.assertEqual(list(Path(d).rglob('*')),[])
 def test_end_to_end_cli_in_temp(self):
  with tempfile.TemporaryDirectory() as d:
   temp=Path(d);orig=temp/'source.syx';dat=bytearray(1550);dat[:4]=bytes((240,71,0,36));dat[7]=20;dat[-1]=247;orig.write_bytes(dat)
   p=subprocess.run([sys.executable,str(ROOT/'Hardware/apply_to_mpk249_dump.py'),str(orig),'--slot','30'],capture_output=True,text=True,check=True)
   out=temp/'source_MPKUNIV2.syx'
   self.assertTrue(out.exists());self.assertEqual(out.read_bytes()[7],29)
   self.assertEqual(orig.read_bytes()[7],20)
   self.assertIn('NO changes were transmitted',p.stdout)

if __name__=='__main__':unittest.main()