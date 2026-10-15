"""Run INSIDE a Bespoke Synth `script` module, not in macOS Terminal.

This creates many permanent MIDI-CC -> UI-control bindings in one operation,
using Bespoke's documented midicontroller scripting API. After it runs,
SAVE YOUR BESPOKE LAYOUT; don't keep re-running it.

Needs Bespoke modules with names `midicontroller` and `oscillator`.
Connect midicontroller's note output to oscillator once.
If you have renamed those modules, edit CONTROLLER / SYNTH below only.

This is a STARTER patch mapping, not a global 'map any arbitrary synth' mechanism.
"""
import midicontroller

CONTROLLER = 'midicontroller'
SYNTH = 'oscillator'

# All known UI field names documented in Bespoke's official `oscillator`
# reference. Unknown optional modules will simply not acquire connections.
# The last column is the musical name of this action.
ASSIGNMENTS = [
    (74,  'fmax',  'Filter cutoff (envelope maximum)'),
    (71,  'q',     'Filter resonance'),
    (18,  'pw',    'Pulsewidth / shape'),
    (19,  'shuffle','Oscillator shuffle'),
    (20,  'envA',  'Amp attack'),
    (21,  'envD',  'Amp decay'),
    (22,  'envS',  'Amp sustain'),
    (23,  'envR',  'Amp release'),
    (24,  'vol',   'Output volume'),
    (25,  'mult',  'Frequency ratio'),
    (26,  'detune','Oscillator detune'),
    (27,  'fmin',  'Filter cutoff (envelope minimum)'),
    (28,  'phase', 'Oscillator phase'),
    (29,  'q',     'Secondary resonance fader'),
    (30,  'syncf', 'Sync frequency'),
    (31,  'soften','Harmonic softening'),
    (78,  'envfilterA','Filter attack'),
    (79,  'envfilterD','Filter decay'),
    (80,  'envfilterS','Filter sustain'),
    (81,  'envfilterR','Filter release'),
    (82,  'pw',    'Alternate shape'),
    (83,  'detune','Alternate detune'),
    (84,  'mult',  'Alternate frequency ratio'),
    (85,  'soften','Alternate soften'),
    (110, 'fmax',  'Macro cutoff'),
    (111, 'q',     'Macro resonance'),
    (112, 'pw',    'Macro pulsewidth'),
    (113, 'shuffle','Macro timbre'),
    (114, 'phase', 'Macro phase'),
    (115, 'detune','Macro detune'),
    (116, 'fmin',  'Macro filter minimum'),
    (117, 'soften','Macro softness'),
]

# Controller API's set_connection() does nothing if target UI control
# does not exist. It does not play notes or supply an audio connection.
controller = midicontroller.get(CONTROLLER)
if controller is None:
    raise RuntimeError('Add a Bespoke midicontroller module named '+CONTROLLER)
for cc, field, description in ASSIGNMENTS:
    controller.set_connection(controller.Control, cc, SYNTH + '~' + field,
                              channel=-1)
print('MPK249 v2: attempted %d batch bindings. Save the layout now.' % len(ASSIGNMENTS))