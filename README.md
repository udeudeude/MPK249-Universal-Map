# MPK249 Universal Map
**MPK-Ready-to-play**: reusable, no-repetitive-mapping setup for the Akai MPK249 across SuperCollider, Vital, VCV Rack, Bespoke Synth, and AudioKit Synth One (iOS).

> **Status: hardware-ready beta.** The offline test suite passes, but this project has **not** been verified on an actual MPK249 or on the target Mac/iPhone. It does not yet deliver zero setup for every application, particularly Bespoke and iOS Synth One.

## Start here
1. [Download the repository ZIP](https://github.com/udeudeude/MPK249-Universal-Map/archive/refs/heads/main.zip), extract it on the Mac, and open **[START_HERE.md](START_HERE.md)**.
2. Start each desktop synth once, then close it. Run `python3 Tools/install_mac.py` to **preview** what would change. When satisfied, run `python3 Tools/install_mac.py --install` or the Mac `Install_on_Mac.command` launcher. The installer backs up existing settings where it writes.
3. Connect your MPK249. Using [dobemad's community MPK249 editor](https://github.com/dobemad/MPK249), **export and save a single-program SysEx backup** before changing anything. Then generate a candidate using `python3 Hardware/apply_to_mpk249_dump.py YOUR_BACKUP.syx --slot 30`. Back up slot 30 too; it may contain a preset. Inspect the generated `.syx` in the editor before transmitting it.
4. Open the included SuperCollider and VCV Rack starting instruments, or use the Vital global mapping installer. For Bespoke and Synth One, follow their dedicated setup notes.

## Included
| Area | What you get | Limits |
|---|---|---|
| **MPK249 hardware** | 141 MIDI assignments across knobs, faders, switches, pads, and navigation | Needs a real original single-program SysEx dump, then editor upload |
| **Vital** | 47 global MIDI assignments with backups and merge behavior | Application configuration paths vary |
| **VCV Rack 2** | Prewired subtractive synthesizer with 16 CC mappings | Select MIDI/audio ports once, then optionally make the template default |
| **SuperCollider** | Playable synth/percussion starter and MIDIdef mappings | Evaluate patch and set an appropriate audio/MIDI environment |
| **Bespoke Synth** | Controller graphic layout plus script for batch-assignment | Needs a starter Bespoke layout with modules and a one-time script run |
| **Synth One iOS** | Defaults-compatible CC74 cutoff, CC71 resonance | Other synth controls require app-specific configuration; no verified bulk import |

**A complete universal mapping for arbitrary third-party patches is not possible without defining each patch's destinations.** This project eliminates repetitive setup where persistent mappings or reusable templates are supported.

## Offline tests
```sh
python3 -m unittest discover -s Tests -v
```
The test suite checks map completeness, simulated MPK249 SysEx transformation, safe Vital config merging, patch structure, and installer preview behavior. **Passing these tests does not substitute for device testing.**

## References and credits
This project builds on documented behavior of [dobemad/MPK249](https://github.com/dobemad/MPK249), [Vital](https://github.com/mtytel/vital), [VCV Rack](https://github.com/VCVRack/Rack), [VCV Fundamental](https://github.com/VCVRack/Fundamental), [Bespoke Synth](https://github.com/BespokeSynth/BespokeSynth), and [AudioKit Synth One](https://github.com/AudioKit/AudioKitSynthOne). See [START_HERE.md](START_HERE.md) for details and references.

**No license has been chosen for this repository yet.** Please review licensing and upstream dependencies before redistributing modifications beyond personal use.
