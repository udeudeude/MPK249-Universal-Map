# Original AudioKit Synth One (iOS)

The [source-code defaults](https://github.com/AudioKit/AudioKitSynthOne/blob/master/AudioKitSynthOne/Settings/AppSettings.swift) declare:

- `cutoffCC = 74`
- `resonanceCC = 71`
- `masterVolumeCC = 255`, ADSR knobs = `255`, most others = `255` (the app's unassigned sentinel).

The MPK249 Universal v2 preset sends CC74 on Bank A Knob 1 and CC71 on Bank A Knob 2. They should operate Synth One's filter **without any MIDI Learn**, subject to correct input routing, any existing custom overrides, and the iOS app version retaining these defaults.

Set original Synth One to accept channel 1 notes (or Omni). MPK249 keys and Pad A use channel 1. Its knobs use channel 2: enable Omni if you want Synth One to see the knobs (the MIDI callback in the public app source filters by configured channel unless Omni).

## Why the entire iOS surface is not automatically mapped yet

Unlike macOS Vital, the original Synth One keeps `AppSettings` inside its app's storage. I could not verify a supported import path for bulk MIDI-learn assignments into the iOS app from the Mac. Thus this is **two ready-to-use knobs**, not a full preset. Other controls can be assigned and saved once through MIDI Learn inside Synth One, or a new app build could add bulk import support. No unverified installer is provided that claims to edit the sandbox.