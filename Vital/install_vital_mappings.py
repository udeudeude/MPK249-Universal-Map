#!/usr/bin/env python3
"""Install MPK249 global MIDI learn mapping into an *existing* Vital JSON config.

Source verified against mtytel/vital/src/common/load_save.cpp.
Backs up original. Quits with an error if file missing/ambiguous/malformed.
Does not modify Vital sound presets, launch Vital, or transmit MIDI.
"""
from pathlib import Path
import argparse,datetime,json,os,shutil,sys
FOLDER=Path(__file__).parent

def candidates():
    home=Path.home()
    dirs=[home/'Library/Application Support/vital',home/'Library/Application Support/Vital',home/'Library/Preferences',home/'.config/vital']
    paths=[]
    for d in dirs:
        if d.exists():
            for g in ['*.config','*.json','*vital*config*','*Vial*config*']:
                for p in d.glob(g):
                    if p.is_file() and p.stat().st_size<5_000_000:
                        try:
                            j=json.loads(p.read_text())
                        except (UnicodeError,ValueError,OSError):continue
                        if isinstance(j,dict) and ('midi_learn' in j or 'data_directory' in j or p.name.lower() in ('vial.config','vital.config')):
                            paths.append(p)
    return sorted(set(paths))

def update(doc, mapping):
    if not isinstance(doc,dict):raise ValueError('Vital config must be a JSON object')
    old=doc.get('midi_learn') or []
    if not isinstance(old,list):raise ValueError('midi_learn config is not an array')
    proposed={v['source']:v['destinations'] for v in mapping}
    # Don't leave a parameter controlled by both old CC and new CC, unless it is intentionally a distinct destination.
    targets={d['destination'] for ds in proposed.values() for d in ds}
    untouched=[];removed=[]
    for o in old:
        if not isinstance(o,dict) or 'source' not in o or not isinstance(o.get('destinations'),list):
            raise ValueError('Unknown midi_learn entry schema; refuse to alter it')
        rest=[d for d in o['destinations'] if not (isinstance(d,dict) and d.get('destination') in targets)]
        if o['source'] in proposed:removed.append(o)
        elif rest:
            untouched.append(dict(o,destinations=rest))
            if len(rest)!=len(o['destinations']):removed.append(o)
        else:removed.append(o)
    # Min/max fields are metadata; Vital actually reads only source/destination strings.
    doc['midi_learn']=sorted(untouched+mapping,key=lambda x:x['source'])
    return doc,removed

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config',type=Path,help='Exact existing Vital config (use when discovery is ambiguous)')
    ap.add_argument('--install',action='store_true',help='Actually write settings; default: dry run')
    ns=ap.parse_args()
    opts=[ns.config] if ns.config else candidates()
    if len(opts)!=1:
        print('Vital config candidates:')
        for p in opts:print('  ',p)
        ap.error('Expected exactly one existing Vital JSON config. Start Vital once, quit it, and provide --config PATH if needed.')
    path=opts[0].expanduser().resolve()
    try:
        doc=json.loads(path.read_text()); desired=json.loads((FOLDER/'desired_midi_learn.json').read_text()); result,replaced=update(doc,desired)
    except (ValueError,UnicodeError,OSError,KeyError) as e:ap.error(str(e))
    print('Config:',path)
    print('New/updated MPK249 control bindings:',len(desired))
    print('Previously mapped entries affected:',len(replaced))
    print('Unrelated MIDI assignments preserved.')
    if not ns.install:
        print('DRY RUN. Re-run with --install once Vital is completely closed.')
        return
    backup=path.with_name(path.name+'.MPK249-backup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    shutil.copy2(path,backup)
    # Atomic replacement after backup.
    output=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    tmp=path.with_name(path.name+'.mpk249-temporary')
    try:
        tmp.write_text(output)
        json.loads(tmp.read_text())
        os.replace(tmp,path)
    finally:
        if tmp.exists():tmp.unlink()
    print('INSTALLED. Backup:',backup)
    print('Restart Vital; controls should work on patches exposing these parameters.')
if __name__=='__main__':main()