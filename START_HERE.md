# MPK249 Universal v2: zero *repetitive* mapping

**Target:** a 2018 MacBook Pro running macOS Sequoia 15.7.9, with SuperCollider, Vital, VCV Rack 2, Bespoke Synth, and original AudioKit Synth One on iPhone/iPad.

This package is substantially more useful than a MIDI number chart. It contains a 141-assignment hardware preset *builder* and ready-made software-side mappings and playable starting instruments. **It is not yet a tested one-click install.** It has been constructed from open-source file-format documentation and passed offline checks, but the hardware and target applications have not been available to run.

## Stage 1: On the Mac, *once*

1. Unzip the folder. Start each app you want to configure at least once, then **quit** Vital, Bespoke and VCV Rack.
2. Open Terminal and run `python3 Tools/install_mac.py` while inside this folder (or double-click `Install_on_Mac.command`). It shows what would be installed. Confirm when ready, or run `python3 Tools/install_mac.py --install` directly. Existing files are backed up before replacement, and the Vital installer preserves unrelated MIDI assignments. It will skip Vital if its configuration is missing or ambiguous instead of guessing.
3. Connect the MPK249. In the independent [dobemad MPK249 editor](https://github.com/dobemad/MPK249), **back up your existing hardware program** as a *single-preset* `.syx` dump. For further assurance also back up all hardware programs. The editor is independent third-party software; compatibility with your specific system has **not** been verified in this environment.
4. Run `python3 Hardware/apply_to_mpk249_dump.py /path/to/your_original.syx --slot 30` (slot 30 is a suggestion, not known to be empty). The output is a new file with `_MPKUNIV2.syx` appended. Back up the original contents of the **target slot** before proceeding. Verify mappings visually in the editor, send the output, and load the new program on the keyboard. **No program in this package communicates with or flashes your MPK249.**
5. Set keybed MIDI channel to 1 if its previous settings used another channel; the Sysex patcher intentionally preserves keyboard/global/pedals/transport parameters it doesn't understand.

## Stage 2: Sit down and play

### Vital: global mapping, once per installation

`Tools/install_mac.py --install` finds the existing Vital JSON settings and installs **47 global MIDI assignments** automatically. The script makes a timestamped backup. Bank A: knob 1 cutoff, knob 2 resonance, knobs 5–8 ADSR; faders control levels, effects and timbre. Bank B controls modulation/effects. Vital's MIDI mappings persist between patches, though no patch is obligated to use or expose every parameter. If Vital is skipped, run `python3 Vital/install_vital_mappings.py --config /exact/path/to/Vial.config --install` after identifying its file. See `Vital/README.md`.

### VCV Rack: ready-patched synth

Open `~/Documents/MPK249/MPK249_Play_Now_legacy.vcv`. It is a *prewired*, playable VCV Rack 2 subtractive synth, with 16 CC destinations inside a MIDI-MAP module, needing **only core and Fundamental modules**. Choose the MPK249 as input in both the `MIDI-CV` and `MIDI-MAP` modules and choose your Mac audio output in `AUDIO-2` (one-time routing). Optionally save this as VCV Rack's startup template from its File menu (or run the Mac installer with `--set-vcv-default` if Rack2 already created its documents folder, after ensuring the existing template is backed up). More details in `VCV_Rack/README.md`.

### SuperCollider: play on launch

Open `SuperCollider/MPK249_Play_Now.scd` and evaluate its complete parenthesized block. It initializes MIDI, creates 2 SynthDefs and maps Banks A/B/C, some switches and all pad banks to sounds. Keyboard channel 1 plays synth notes, pad bank B channel 10 plays drums, pads C/D channel 2 sound plucks. Reuse it as your startup patch. `Cmd+.` stops sound. No MIDI learn.

### Bespoke Synth: programmatic batch-mapping

The installer adds a graphical controller template, but a controller picture is **not** an instrument mapping. To make actual functional assignments, build a simple layout with a `midicontroller` module patched to an `oscillator` module and an audio output. Add a Bespoke `script` module, paste `Bespoke/One_Click_Bindings.py` into its Python editor and run it **once**. That script installs 32 CC-to-oscillator bindings without manually learning them one-by-one, using the documented `midicontroller.set_connection()` API. Save that Bespoke layout as your default/startup layout. For arbitrary modules, the script is a reusable starting point but needs specific target UI control names in future patches. See `Bespoke/README.md`.

### Synth One on iOS: partial immediate controls

The public-source original Synth One defaults **CC74 = cutoff** and **CC71 = resonance**; our Knob A1 and A2 send exactly those values. Keyboard and pad bank A are on channel 1 and should play melodic notes with a USB MIDI iOS connection. **Other Synth One controls are mostly UNASSIGNED by default**, and unlike desktop Vital, iOS Synth One does not expose a verified whole-map import mechanism; it is **not fully zero-setup** for all knobs. This package does not modify an iOS app, and no direct import has been demonstrated. See `Synth_One_iOS/README.md`.

## Designed MIDI map (hardware channel in parentheses)

| Bank | Knobs 1-8 | Faders 1-8 | Switches 1-8 |
|---|---|---|---|
| A | `74,71,18–23` (2) | `24–31` (2) | `70,72,73,75,76,77,118,119` (2) |
| B | `78–85` (2) | `86–93` (2) | `102–109` (2) |
| C | `110–117` (2) | `40–47` (2) | `48–55` (2) |

Pads A = channel 1 notes 60–75; Pads B = channel 10 notes 36–51; Pads C = channel 2 notes 36–51; Pads D = channel 2 notes 60–75. Navigation five controls = channel 2 CC 56–60. Keyboard = channel 1 (check once). **Transport, pitch/mod wheels, pedal settings, arpeggiator and keyboard channel are not changed by the automated SysEx patcher.**

## Non-goals and open verification tasks

- One preset cannot magically assign arbitrary parameters on *every* third-party instrument. Global mappings like Vital's work where those parameters exist, and VCV/Bespoke requires a patch or template containing the targets.
- None of the patches/scripts has been run against your specific MPK249 firmware, the five installed app versions, or a Mac/iOS sound device. Think of this as a comprehensive **hardware-ready beta** rather than proof that every application is instantly usable.
- The SysEx editor is reverse-engineered. Backups and visual inspection before upload are essential.
- System-dependent audio/MIDI device selection remains a one-time step; it does **not** mean programming every knob.
- Bespoke and iOS Synth One don't currently reach the same effortless level as Vital/SuperCollider/VCV. Avoid declaring the project complete until real tests are performed.

## Sources consulted

- [MPK249 community editor and reverse-engineered preset codec](https://github.com/dobemad/MPK249/blob/main/mpk2_preset.py)
- [Vital source for MIDI mappings and global config](https://github.com/mtytel/vital/blob/main/src/common/load_save.cpp) and [parameter names](https://github.com/mtytel/vital/blob/main/src/common/synth_parameters.cpp)
- [VCV Rack 2 MIDI-MAP serialization](https://github.com/VCVRack/Rack/blob/v2/src/core/MIDIMap.cpp) and [Core MIDI-CV module](https://github.com/VCVRack/Rack/blob/v2/src/core/MIDI_CV.cpp)
- [VCV Fundamental free modules](https://github.com/VCVRack/Fundamental)
- [Bespoke controller JSON reference](https://github.com/BespokeSynth/BespokeSynth/tree/main/resource/userdata_original/controllers) and [Python scripting reference](https://github-wiki-see.page/m/BespokeSynth/BespokeSynth/wiki/Scripting-Reference)
- [AudioKit Synth One source AppSettings.swift](https://github.com/AudioKit/AudioKitSynthOne/blob/master/AudioKitSynthOne/Settings/AppSettings.swift)