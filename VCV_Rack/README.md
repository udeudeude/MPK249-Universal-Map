# VCV Rack 2: playable MIDI-ready synth patch

`MPK249_Play_Now_legacy.vcv` is an **uncompressed legacy JSON** `.vcv` patch. VCV Rack 2 source contains a legacy-file read path; this saves dependencies and is compatible in principle but untested on the user's Rack installation.

The patch has the complete signal chain: `MIDI-CV` -> two `Fundamental VCO`s -> `Fundamental Mixer` -> `Fundamental VCF` -> `Fundamental VCA-1` with `Fundamental ADSR` -> `Core AUDIO-2`. A `Fundamental LFO` drives pulse-width and filter cutoff modulation. A Core `MIDI-MAP` module maps 16 Bank A CCs to live parameters, not an empty mapping list.

**One-time routing:** After opening, set both MIDI modules to the MPK249/CoreMIDI input; MIDI-CV uses channel 1 (VCV's 0-based channel field), MIDI-MAP channel 2 (field 1). Select the desired audio device in AUDIO-2. Save the patch so settings persist. Save it as a startup template in Rack's File menu if desired. This is device selection, not 16 individual MIDI learn operations.

`assign_midi_device.py --device 'MPK249 <name>'` can preinsert a known MIDI device string into a *separate copy* of the patch, but Rack drivers use platform-dependent integer IDs. The default audio output isn't predetermined.

**Caution:** Because all mappings live inside this patch, arbitrary other Rack patches are *not* automatically mapped. Reuse it as a template, clone the patch, or copy its MIDI-MAP and mapped modules.