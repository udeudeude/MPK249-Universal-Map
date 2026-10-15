#!/usr/bin/env python3
"""Generate consistent MPK249 universal assignments and companion files.

No device access or dependencies. From verified third party model source structures.
"""
from pathlib import Path
import json,csv
ROOT=Path(__file__).resolve().parent
B={'A':{'Knob':[74,71,18,19,20,21,22,23],'Fader':list(range(24,32)),'Switch':[70,72,73,75,76,77,118,119]},
   'B':{'Knob':list(range(78,86)),'Fader':list(range(86,94)),'Switch':list(range(102,110))},
   'C':{'Knob':list(range(110,118)),'Fader':list(range(40,48)),'Switch':list(range(48,56))}}
ROLE={
 'A':{'Knob':['Cutoff','Resonance','Wavetable/Pulse width','Timbre/Warp','Attack','Decay','Sustain','Release'],
      'Fader':['Master level','Osc 1 level','Osc 2 level','Noise/second-osc','Filter drive','Mod depth','Effects mix','Output/mix'],
      'Switch':['Osc 1 enable','Osc 2 enable','Noise enable','Filter enable','LFO sync','Delay enable','Reverb enable','Reset/trigger']},
 'B':{'Knob':['LFO 1 speed','LFO 1 depth','LFO 2 speed','LFO 2 depth','Envelope 2 attack','Envelope 2 decay','Envelope 2 sustain','Envelope 2 release'],
      'Fader':['Pan','Osc detune','Filter blend','Filter 2 cutoff','Delay time','Delay feedback','Reverb size','Reverb wet'],
      'Switch':['LFO 1 sync','LFO 2 sync','Arp toggler','Delay on','Reverb on','Distortion on','Chorus on','Trigger']},
 'C':{'Knob':['Macro 1','Macro 2','Macro 3','Macro 4','Macro 5','Macro 6','Macro 7','Macro 8'],
      'Fader':['Macro 9','Macro 10','Macro 11','Macro 12','Macro 13','Macro 14','Macro 15','Macro 16'],
      'Switch':['Gate 1','Gate 2','Gate 3','Gate 4','Gate 5','Gate 6','Gate 7','Gate 8']}}
assign=[]
for bank,grp in B.items():
 for kind,ccs in grp.items():
  for i,cc in enumerate(ccs):
   assign.append(dict(type=kind,bank=bank,index=i+1,channel=2,cc=cc,label=ROLE[bank][kind][i],mode='toggle' if kind=='Switch' and i<7 else 'momentary' if kind=='Switch' else 'absolute'))
for bank,ch,first,role in [('A',1,60,'Chromatic notes'),('B',10,36,'GM percussion range'),('C',2,36,'Low triggers'),('D',2,60,'High triggers')]:
 for i in range(16):
  assign.append(dict(type='Pad',bank=bank,index=i+1,channel=ch,note=first+i,label=role,mode='momentary'))
for i,name in enumerate(['Enter','Left','Right','Up','Down']):
 assign.append(dict(type='Navigation',bank='-',index=i+1,name=name,channel=2,cc=56+i,label='Navigation / utility',mode='momentary'))
assert len(assign)==141
used=[a['cc'] for a in assign if 'cc' in a]
assert len(used)==len(set(used))==77
assert not set(used)&set(list(range(32,40))+list(range(64,70))+list(range(96,102))+list(range(120,128)))
(ROOT/'Hardware/MPKUNIV2.mapping.json').write_text(json.dumps({'name':'MPKUNIV2','mapping_version':'2.0','keyboard_channel':1,'midi_controls_channel':2,'assignments':assign,'unchanged':['keyboard pitch/mod/pedal','transport','arpeggiator','global settings']},indent=2)+'\n')
with (ROOT/'Hardware/MPKUNIV2.mapping.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=['type','bank','index','name','channel','cc','note','label','mode']);writer.writeheader();writer.writerows(assign)

# Vital MIDI learn destinations, sourced from mtytel/vital/src/common/synth_parameters.cpp.
# User may retain custom mapping to any of these as desired.
vital={
 74:'filter_1_cutoff',71:'filter_1_resonance',18:'osc_1_wave_frame',19:'osc_1_spectral_morph_amount',
 20:'env_1_attack',21:'env_1_decay',22:'env_1_sustain',23:'env_1_release',
 24:'voice_amplitude',25:'osc_1_level',26:'osc_2_level',27:'filter_1_mix',28:'filter_1_drive',
 29:'osc_1_unison_detune',30:'delay_dry_wet',31:'reverb_dry_wet',
 70:'osc_1_on',72:'osc_2_on',73:'filter_1_osc1_input',75:'filter_1_on',
 76:'lfo_1_sync',77:'delay_on',118:'reverb_on',119:'portamento_force',
 78:'lfo_1_frequency',79:'modulation_1_amount',80:'lfo_2_frequency',81:'modulation_2_amount',
 82:'env_2_attack',83:'env_2_decay',84:'env_2_sustain',85:'env_2_release',
 86:'osc_1_pan',87:'osc_1_tune',88:'filter_1_blend',89:'filter_2_cutoff',
 90:'delay_frequency',91:'delay_feedback',92:'reverb_decay_time',93:'reverb_dry_wet',
 102:'lfo_1_sync',103:'lfo_2_sync',104:'legato',105:'delay_on',
 106:'reverb_on',107:'distortion_on',108:'chorus_on',109:'portamento_force',
 110:'macro_control_1',111:'macro_control_2',112:'macro_control_3',113:'macro_control_4'}
# Disallow duplicate target parameters; globally mapping multiple CC to a parameter
# is possible in Vital but confusing; choose one canonical CC, keep others for SC / Rack.
seen=set();vital_unique={}
for cc,d in vital.items():
 if d not in seen: vital_unique[cc]=d;seen.add(d)
(ROOT/'Vital/desired_midi_learn.json').write_text(json.dumps([{'source':cc,'destinations':[{'destination':dest}]} for cc,dest in vital_unique.items()],indent=2)+'\n')

# Bespoke synth visual MIDI controller geometry, based on Bespoke's shipped controllers/*.json layout contract.
groups=[]
for i,bank in enumerate('ABC'):
 x=0;y=i*160
 for kind,dy,shape in [('Knob',0,'knob'),('Switch',44,'button'),('Fader',71,'slider')]:
  group={'rows':1,'cols':8,'position':[x,y+dy], 'dimensions':[29,44 if kind=='Fader' else 27], 'spacing':[34,48], 'controls':B[bank][kind], 'messageType':'control','drawType':shape}
  groups.append(group)
for i,bank in enumerate('AB'):
 groups.append({'rows':4,'cols':4,'position':[300,i*155],
                'dimensions':[26,26],'spacing':[34,34],
                'controls':list(range((60,36,36,60)[i],(60,36,36,60)[i]+16)),
                'messageType':'note','drawType':'button','colors':[0,127]})
# Bespoke has optional channelfilter but note bank B and C have different channels; leave omni.
(ROOT/'Bespoke/MPK249_Universal_v2.controller.json').write_text(json.dumps({'groups':groups},indent=2)+'\n')

# VCV Rack 2 supports legacy uncompressed JSON .vcv files as a compatibility load path.
# Generator builds a working mono subtractive synthesizer with preprogrammed Core MIDI-Map and free Fundamental modules.
modules=[]
def module(mid,plug,model,pos,params=None,data=None):
 d={'id':mid,'plugin':plug,'model':model,'version':'2.0.0','params':[], 'pos':list(pos)}
 if params: d['params']=[{'id':idx,'value':val} for idx,val in sorted(params.items())]
 if data is not None:d['data']=data
 modules.append(d)
module(1,'Core','MIDIToCVInterface',(0,0),data={'midi':{'driver':-1,'deviceName':'','channel':0}})
module(2,'Fundamental','VCO',(8,0),{2:0,5:0.5,6:0.3})
module(3,'Fundamental','VCO',(20,0),{2:-12,5:0.45})
module(4,'Fundamental','Mixer',(32,0),{0:0.28})
module(5,'Fundamental','VCF',(40,0),{0:0.67,2:0.2,4:0.0})
module(6,'Fundamental','ADSR',(50,0),{0:0.18,1:0.36,2:0.75,3:0.3})
module(7,'Fundamental','VCA-1',(59,0),{0:0.7,1:1})
module(8,'Core','AudioInterface2',(66,0),data={})
module(9,'Fundamental','LFO',(77,0),data={})
map1=[(74,5,0),(71,5,2),(18,2,5),(19,3,5),(20,6,0),(21,6,1),(22,6,2),(23,6,3),(24,7,0),(25,4,0),(26,3,2),(27,2,2),(28,5,4),(29,5,3),(30,2,6),(31,9,2)]
# Keep mappings within supported source; at least 16 controls directly available for play.
module(10,'Core','MIDI-Map',(84,0),data={'maps':[{'cc':cc,'moduleId':mid,'paramId':pid} for cc,mid,pid in map1]+[{'cc':-1,'moduleId':-1,'paramId':0}], 'smooth':True,'midi':{'driver':-1,'deviceName':'','channel':1}})
cables=[]
def cab(outmod,outid,inmod,inid):
 cables.append({'id':1000+len(cables),'outputModuleId':outmod,'outputId':outid,'inputModuleId':inmod,'inputId':inid,'color':'#e3b547'})
cab(1,0,2,0);cab(1,0,3,0);cab(2,2,4,0);cab(3,1,4,1)
cab(4,0,5,3);cab(5,0,7,1);cab(1,1,6,4);cab(6,0,7,0);cab(7,0,8,0);cab(7,0,8,1);cab(9,0,5,0);cab(9,0,2,3)
# No instruments or output connections reference the MIDI-Map, it drives parameters directly.
patch={'version':'2.0.0','modules':modules,'cables':cables}
(ROOT/'VCV_Rack/MPK249_Play_Now_legacy.vcv').write_text(json.dumps(patch,indent=2)+'\n')
# Sanity checks on module and mapping references
idmap={m['id']:m for m in modules}
assert all(c['outputModuleId'] in idmap and c['inputModuleId'] in idmap for c in cables)
assert all(m['moduleId'] in idmap for m in patch['modules'][-1]['data']['maps'] if m['cc']>=0)
print('Generated',len(assign),'hardware assignments;',len(vital_unique),'Vital destinations;',len(groups),'Bespoke visual banks;',len(modules),'VCV modules')