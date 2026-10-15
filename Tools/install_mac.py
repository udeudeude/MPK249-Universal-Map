#!/usr/bin/env python3
"""One-time Mac setup for supported MPK249 universal companion mappings.

No external packages, no network, no MIDI, and no application launches.
Always backup before replacement. Run without --install to preview first.
"""
from pathlib import Path
import argparse,datetime,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Vital'))
from install_vital_mappings import candidates,update
import json,os

def copy_if_changed(src,dst):
    if dst.exists() and dst.read_bytes()==src.read_bytes():
        print('ALREADY INSTALLED:',dst);return
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():
        stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        backup=dst.with_name(dst.name+'.MPK249-backup-'+stamp)
        shutil.copy2(dst,backup)
        print('BACKUP:',backup)
    shutil.copy2(src,dst)
    print('INSTALLED:',dst)

def is_running(appname):
    if sys.platform!='darwin':return False
    try:
        p=subprocess.run(['pgrep','-ix',appname],capture_output=True,timeout=3)
        return p.returncode==0
    except (OSError,subprocess.TimeoutExpired):return False

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--install',action='store_true',help='Install Vital, Bespoke, and VCV starting patch')
    ap.add_argument('--vital-config',type=Path,help='Override autodetected Vital .config JSON path')
    ap.add_argument('--set-vcv-default',action='store_true',help='Also REPLACE your Rack2 default template, backed up; requires --install')
    ns=ap.parse_args()
    home=Path.home()
    bsp=home/'Documents/BespokeSynth/controllers/MPK249_Universal_v2.json'
    patch=home/'Documents/MPK249/MPK249_Play_Now_legacy.vcv'
    rack=home/'Documents/Rack2/template.vcv'
    cs=[ns.vital_config] if ns.vital_config else candidates()
    print('MAC SETUP | MPK249 UNIVERSAL v2')
    print('Vital candidates:',*[str(x) for x in cs] or ['none found'],sep='\n  ')
    print('Bespoke controller:',bsp)
    print('VCV patch:',patch)
    if ns.set_vcv_default:print('VCV DEFAULT TEMPLATE:',rack)
    if not ns.install:
        print('PREVIEW ONLY. Close Vital/VCV/Bespoke and run this program with --install.')
        return
    if ns.set_vcv_default and not (home/'Documents/Rack2').exists():
        ap.error('No Rack2 directory found. Install and launch VCV Rack once before setting template.')
    running=[name for name in ['Vital','Rack','BespokeSynth'] if is_running(name)]
    if running:ap.error('Quit these applications first: '+', '.join(running))
    if len(cs)!=1:
        print('SKIPPED Vital (ambiguous or missing config). You can install later using --vital-config PATH.')
    else:
        vp=cs[0].expanduser().resolve()
        try:
            old=json.loads(vp.read_text())
            maps=json.loads((ROOT/'Vital/desired_midi_learn.json').read_text())
            new,replaced=update(old,maps)
            stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            backup=vp.with_name(vp.name+'.MPK249-backup-'+stamp)
            shutil.copy2(vp,backup)
            tmp=vp.with_name(vp.name+'.MPK249-tmp')
            try:
                tmp.write_text(json.dumps(new,indent=2)+'\n')
                json.loads(tmp.read_text())
                os.replace(tmp,vp)
            finally:
                if tmp.exists():tmp.unlink()
            print(f'INSTALLED Vital: {len(maps)} MIDI assignments, {len(replaced)} prior mappings modified; backup {backup}')
        except (ValueError,OSError,KeyError,TypeError) as e:
            print('SKIPPED Vital due to error:',e)
    copy_if_changed(ROOT/'Bespoke/MPK249_Universal_v2.controller.json',bsp)
    copy_if_changed(ROOT/'VCV_Rack/MPK249_Play_Now_legacy.vcv',patch)
    if ns.set_vcv_default:copy_if_changed(ROOT/'VCV_Rack/MPK249_Play_Now_legacy.vcv',rack)
    print('\nDONE. Bespoke: choose new layout in midicontroller module once; VCV: choose MIDI and AUDIO devices once.')
    print('No MPK249 preset was transmitted; hardware SysEx import remains a separate, backed-up step.')
if __name__=='__main__':main()