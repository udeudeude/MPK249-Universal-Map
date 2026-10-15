# Bespoke Synth: zero per-control learning via scripting

Two independent assets:

- `MPK249_Universal_v2.controller.json` is a physical graphical map. Copy it into `~/Documents/BespokeSynth/controllers/` with the supplied installer; select it in `midicontroller` once. This alone does **not** assign musical destinations.
- `One_Click_Bindings.py` uses the built-in Bespoke **script module** Python interpreter and documented `midicontroller.set_connection()` API to **batch-create 32 actual MIDI mappings**.

## Create and save your first fully mapped Bespoke layout

1. In Bespoke create `midicontroller`, `oscillator`, and an output. Keep exact module names `midicontroller` and `oscillator`, or change `CONTROLLER` and `SYNTH` inside the script to match.
2. Select the MPK249 MIDI input and patch the controller's *note output* to the oscillator and the oscillator's audio to output.
3. Add a `script` module. Open `One_Click_Bindings.py` in a text editor, copy it to the script module, and run it once inside Bespoke. **Do not run it in external Python; it uses Bespoke-specific API modules.**
4. Move Bank A knobs, observe oscillator's `fmax` and `q` controls, and verify the other sliders. Save the entire Bespoke session/layout as your startup instrument.

If a target UI control doesn't exist in your copy of Bespoke, the Bespoke scripting API silently ignores that target rather than creating a new one. The `.py` file uses official oscillator control names; different versions can have different names. Full correctness requires an on-device test.

To use the mapping with different synth modules, change only the list of CC->module field names at the beginning of the script. No manual MIDI learning for each new mapping.

Sources: [Bespoke scripting reference](https://github-wiki-see.page/m/BespokeSynth/BespokeSynth/wiki/Scripting-Reference) and [Bespoke oscillator controls](https://www.bespokesynth.com/docs/).