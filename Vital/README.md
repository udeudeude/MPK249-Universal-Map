# Vital: install persistent global MIDI learn automatically

The public Vital code stores MIDI CC mappings as `midi_learn` in its JSON settings file. The package contains `desired_midi_learn.json` with 47 hand-selected mappings that match `MPKUNIV2`.

1. Start Vital once so it can create its config file. Quit *every* Vital instance (including DAW plugins).
2. Preview: `python3 Vital/install_vital_mappings.py`. If multiple settings files exist, it refuses to guess.
3. Install: `python3 Vital/install_vital_mappings.py --install`, or `--config /exact/path/to/settings --install`.
4. Confirm after restarting Vital: Bank A Knob 1 sends CC74 filter cutoff; Knob2 CC71 resonance; Knobs 5-8 CC20–23 ADSR. Check CCs 110–113 for Macros 1–4.

The installer backs up the original config with a `.MPK249-backup-YYYYMMDD-HHMMSS` suffix. It preserves unrecognized keys and unrelated CC assignments. It merges by destination: mapping a parameter previously controlled by another CC transfers it to the new MPK249 CC.

**Version caveat:** The configuration path and JSON shape are sourced from public Vital code; actual builds might differ. The installer will skip rather than guess if it can't verify a JSON object and `midi_learn` array.

This is a **global** mapping; it does not invent per-preset modulation assignments. Some parameters may have no audible effect on presets that bypass their oscillator, LFO, filter, or effect module.