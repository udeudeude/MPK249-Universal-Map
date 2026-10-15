#!/usr/bin/env python3
"""Offline single-preset SysEx editor for Akai MPK249, using dobemad/MPK249 offsets.

Requires a real *single-preset* .syx backup exported from the device.
Does NOT communicate with hardware. Never overwrites source.
"""
import argparse,json
from pathlib import Path
P=Path(__file__).resolve().parent
HEADER=b'\xf0\x47\x00\x24'
MINIMUM=0x59d+5*13+1
COLORS={'A':(0x09,0x08),'B':(0x02,0x04),'C':(0x0a,0x0c),'D':(0x05,0x0e)}

def validate(data):
    if len(data)<MINIMUM or data[:4]!=HEADER or data[-1]!=0xf7:
        raise ValueError('Not an MPK249 single-preset SysEx dump (check model/length/header/F7).')
    if b'\xf7' in data[:-1] or any(x>127 for x in data[1:-1]):
        raise ValueError('Unexpected multiple messages or illegal high-bit payload byte.')
    if data[7]>29:raise ValueError('Unexpected destination slot byte (>29).')
    # Offsets from dobemad/MPK249/mpk2_preset.py; fail closed if a type is unknown.
    for pos,size,count,allowed in [(0x2fd,9,24,{0,1,2,3}),(0x3d5,6,24,{0,1}),
                                   (0x3d,11,64,{0,1,2}),(0x465,13,24,{0,1,2,3,4}),
                                   (0x59d,13,5,{0,1,2,3,4})]:
        for idx in range(count):
            if data[pos+size*idx] not in allowed:
                raise ValueError(f'Unknown control type at offset {pos+size*idx:#x}; refusing potentially incompatible dump.')

def apply(data,mapping,slot=None):
    validate(data)
    target=bytearray(data)
    target[8:16]=b'MPKUNIV2'
    if slot is not None:
        if not 1<=slot<=30:raise ValueError('Slot must be 1-30')
        target[7]=slot-1
    for control in mapping['assignments']:
        kind=control['type'];i=control['index']-1;chan=control['channel']; bank=control['bank']; cc=control.get('cc')
        if kind in ('Knob','Fader','Switch'):
            index='ABC'.index(bank)*8+i
            if kind=='Knob':
                off=0x2fd+9*index
                target[off:off+6]=bytes([0,chan,cc,0,127,1])
            elif kind=='Fader':
                off=0x3d5+6*index
                target[off:off+6]=bytes([0,chan,cc,0,127,1])
            else:
                off=0x465+13*index
                for pos,val in [(0,0),(1,chan),(2,cc),(3,1 if control['mode']=='toggle' else 0),(5,0),(7,1)]:
                    target[off+pos]=val
        elif kind=='Pad':
            index='ABCD'.index(bank)*16+i; off=0x3d+11*index
            target[off]=0;target[off+1]=chan;target[off+2]=control['note']
            target[off+3]=1;target[off+4]=0;target[off+5]=0
            target[off+9],target[off+10]=COLORS[bank]
        elif kind=='Navigation':
            off=0x59d+13*i
            for pos,val in [(0,0),(1,chan),(2,cc),(3,0),(5,0),(7,1)]:target[off+pos]=val
        else:raise ValueError(f'Unexpected type: {kind}')
    validate(target)
    return bytes(target)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--slot',type=int,help='Destination slot 1-30; default original slot')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    mapping=json.loads((P/'MPKUNIV2.mapping.json').read_text())
    if not args.input.is_file():parser.error('No such input SysEx')
    raw=args.input.read_bytes()
    try:out=apply(raw,mapping,args.slot)
    except ValueError as e:parser.error(str(e))
    path=args.output or args.input.with_name(args.input.stem+'_MPKUNIV2.syx')
    if path.resolve()==args.input.resolve() or path.exists():parser.error('Output overlaps input or exists. Choose a fresh filename.')
    path.write_bytes(out)
    print(f'Generated {path} | slot {out[7]+1} | changed {sum(a!=b for a,b in zip(raw,out))} bytes')
    print('NO changes were transmitted to the keyboard. Validate visually in editor; BACK UP target slot before uploading.')
if __name__=='__main__':main()