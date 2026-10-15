/* MPK249 PLAY NOW v2 | SuperCollider

Open this file in SuperCollider and evaluate the entire ( ... ) block.
Requires MPKUNIV2 hardware preset, USB MIDI, and working SC sound output.
Keys + Pad A: MIDI Ch1; knobs/faders/switches: MIDI Ch2; Pad B: Ch10;
Pad C,D: Ch2. MIDIdef's channels are zero-indexed (0,1,9).

EVERY bank sends distinct CCs and is recognized by the single CC dispatcher.
Live synth and mappings are built together; no MIDI learn.
Stop sound: Cmd+period. Re-evaluate block to replace MIDIdef registrations.
*/
(
s.waitForBoot({
    var voices = IdentityDictionary.new;
    var values = IdentityDictionary.new;
    var routes = IdentityDictionary.new;
    var midiReady = false;

    MIDIClient.init;
    MIDIIn.connectAll;

    SynthDef(\mpk249_v2_voice, { |out=0, freq=440, gate=1, amp=0.25,
        cutoff=2500, resonance=0.22, shape=0.55, timbre=0.0,
        attack=0.02, decay=0.3, sustain=0.65, release=0.5,
        osc1=0.9, osc2=0.25, noiseLevel=0.04, drive=0.0,
        detune=0.003, lfoRate=0.6, lfoDepth=0.0, lfo2Rate=0.3, lfo2Depth=0.0,
        pan=0.0, filterOn=1, osc1On=1, osc2On=1, noiseOn=1,
        modDepth=0.0, fxMix=0.0, delayTime=0.2, delayFeedback=0.1,
        reverbSize=0.45, reverbMix=0.12, master=0.22|
        var env = EnvGen.kr(Env.adsr(attack,decay,sustain,release),gate,doneAction:2);
        var pitchVib = SinOsc.kr(lfoRate.max(0.01)) * lfoDepth * modDepth;
        var filterLfo = SinOsc.kr(lfo2Rate.max(0.01)) * lfo2Depth * 1.5;
        var f = freq * (pitchVib * 0.04).midiratio;
        var first = VarSaw.ar(f,0,shape.clip(0.02,0.98)) * osc1 * osc1On;
        var second = Pulse.ar(f*(1+detune), (0.5+timbre*0.45).clip(0.02,0.98)) * osc2 * osc2On;
        var source = (first+second+WhiteNoise.ar(noiseLevel*noiseOn))*0.28;
        var filtered = RLPF.ar(source, (cutoff*(filterLfo.exp)).clip(80,14000), resonance.clip(0.08,0.95));
        var sig = SelectX.ar(filterOn.clip(0,1),[source,filtered]);
        sig = (sig*(1+drive*3)).tanh;
        sig = CombC.ar(sig,0.7,delayTime.clip(0.03,0.65),delayFeedback.clip(0,0.85)*2)+sig;
        sig = (sig*(1-fxMix)) + (FreeVerb.ar(sig,fxMix*reverbMix,reverbSize,0.25)*fxMix);
        sig = Pan2.ar(sig*env*amp*master,pan);
        Out.ar(out,Limiter.ar(sig,0.7));
    }).add;

    SynthDef(\mpk249_v2_hit, { |out=0, freq=140, level=0.25|
        var env=EnvGen.kr(Env.perc(0.002,0.22),doneAction:2);
        var sig=(SinOsc.ar(freq*(1+EnvGen.kr(Env.perc(0,0.07,2))))*0.7+WhiteNoise.ar(0.25));
        Out.ar(out,(sig*env*level*0.3).dup);
    }).add;
    s.sync;

    values.putAll((
        amp:0.27, master:0.23, cutoff:2400, resonance:0.25, shape:0.55,
        timbre:0, attack:0.015, decay:0.25, sustain:0.7, release:0.55,
        osc1:0.85, osc2:0.2, noiseLevel:0.05, drive:0,
        detune:0.003, lfoRate:0.6, lfoDepth:0.1, lfo2Rate:0.4,
        lfo2Depth:0.15, pan:0, modDepth:0.15, fxMix:0.5,
        delayTime:0.25, delayFeedback:0.0, reverbSize:0.5, reverbMix:0.2,
        filterOn:1, osc1On:1, osc2On:1, noiseOn:1
    ));

    // CC -> [server argument, min, max, curve]; ranges are intentional.
    // The direct filter frequency mapping is exponential. Other controls are linear.
    [
        [74,\cutoff,85,12000,\exp], [71,\resonance,0.08,0.93,\lin],
        [18,\shape,0.02,0.98,\lin], [19,\timbre,-1,1,\lin],
        [20,\attack,0.002,3.0,\exp], [21,\decay,0.01,3.0,\exp],
        [22,\sustain,0,1,\lin], [23,\release,0.02,6.0,\exp],
        [24,\master,0,0.5,\lin], [25,\osc1,0,1,\lin],
        [26,\osc2,0,1,\lin], [27,\noiseLevel,0,0.6,\lin],
        [28,\drive,0,1,\lin], [29,\modDepth,0,1,\lin],
        [30,\fxMix,0,1,\lin], [31,\pan,-1,1,\lin],
        [78,\lfoRate,0.04,18,\exp], [79,\lfoDepth,0,1,\lin],
        [80,\lfo2Rate,0.04,18,\exp], [81,\lfo2Depth,0,1,\lin],
        [82,\attack,0.002,4,\exp], [83,\decay,0.01,4,\exp],
        [84,\sustain,0,1,\lin], [85,\release,0.01,8,\exp],
        [86,\pan,-1,1,\lin], [87,\detune,0,0.06,\lin],
        [88,\timbre,-1,1,\lin], [89,\cutoff,80,14000,\exp],
        [90,\delayTime,0.04,0.65,\lin], [91,\delayFeedback,0,0.85,\lin],
        [92,\reverbSize,0,1,\lin], [93,\reverbMix,0,1,\lin],
        // Bank C is an immediately live alternative macro surface. Its
        // controls intentionally change the parameters above, not unmapped knobs.
        [110,\cutoff,80,14000,\exp], [111,\resonance,0.08,0.95,\lin],
        [112,\shape,0.02,0.98,\lin], [113,\timbre,-1,1,\lin],
        [114,\drive,0,1,\lin], [115,\lfoDepth,0,1,\lin],
        [116,\reverbMix,0,1,\lin], [117,\delayFeedback,0,0.85,\lin],
        [40,\master,0,0.5,\lin], [41,\osc1,0,1,\lin],
        [42,\osc2,0,1,\lin], [43,\noiseLevel,0,0.6,\lin],
        [44,\attack,0.002,3,\exp], [45,\release,0.02,7,\exp],
        [46,\lfo2Rate,0.04,18,\exp], [47,\pan,-1,1,\lin]
    ].do { |spec| routes[spec[0]] = spec.copyRange(1,4) };

    ~mpkV2Set = { |parameter, value|
        values[parameter] = value;
        voices.values.do { |node| node.set(parameter,value) };
    };

    ~mpkV2Stop = {
        MIDIdef(\mpkV2CC).free;
        MIDIdef(\mpkV2On).free;
        MIDIdef(\mpkV2Off).free;
        MIDIdef(\mpkV2PadOn).free;
        MIDIdef(\mpkV2PadOff).free;
        MIDIdef(\mpkV2Drum).free;
        voices.values.do { |node| node.set(\gate,0) };
        voices.clear;
    };

    MIDIdef.noteOn(\mpkV2On, { |velocity,note,ch,src|
        var node, args;
        if (velocity > 0) {
            if (voices[note].notNil) {voices[note].set(\gate,0)};
            args = [\freq,note.midicps];
            values.keysValuesDo { |k,v| args = args ++ [k,v] };
            node=Synth(\mpk249_v2_voice, args);
            node.set(\amp, velocity.linlin(1,127,0.05,0.5));
            voices[note]=node;
        }{
            if (voices[note].notNil) {voices[note].set(\gate,0);voices.removeAt(note)};
        };
    },chan:0);

    MIDIdef.noteOff(\mpkV2Off, { |velocity,note|
        if (voices[note].notNil) {voices[note].set(\gate,0);voices.removeAt(note)};
    },chan:0);

    // Pad C and D sound a separate pluck voice, while note pads A mirror the keyboard.
    MIDIdef.noteOn(\mpkV2PadOn, { |velocity,note|
        Synth(\mpk249_v2_hit,[\freq,note.midicps,\level,velocity/127]);
    },chan:1);
    MIDIdef.noteOff(\mpkV2PadOff, { },chan:1);
    MIDIdef.noteOn(\mpkV2Drum, { |velocity,note|
        Synth(\mpk249_v2_hit,[\freq,(note.linexp(36,51,70,320)),\level,velocity/127]);
    },chan:9);

    MIDIdef.cc(\mpkV2CC, { |raw,cc,ch,src|
        var route=routes[cc];
        if (route.notNil) {
            var min=route[1];var max=route[2];var mode=route[3];var result;
            result = if(mode == \exp,{raw.linexp(0,127,min,max)},{raw.linlin(0,127,min,max)});
            ~mpkV2Set.value(route[0],result);
        };
        if ([70,72,73,75,76,77,118,119].includes(cc)) {
            if(cc==70){~mpkV2Set.value(\osc1On,(raw>=64).asInteger)};
            if(cc==72){~mpkV2Set.value(\osc2On,(raw>=64).asInteger)};
            if(cc==73){~mpkV2Set.value(\noiseOn,(raw>=64).asInteger)};
            if(cc==75){~mpkV2Set.value(\filterOn,(raw>=64).asInteger)};
            if(cc==77){~mpkV2Set.value(\fxMix,(raw>=64).asInteger)};
            if(cc==118){~mpkV2Set.value(\reverbMix,(raw>=64).asInteger)};
        };
        if ((cc>=102) && (cc<=109)) {
            if(cc==105){~mpkV2Set.value(\delayFeedback,if(raw>=64,0.6,0))};
            if(cc==106){~mpkV2Set.value(\reverbMix,if(raw>=64,0.4,0))};
            if(cc==107){~mpkV2Set.value(\drive,if(raw>=64,0.7,0))};
            if(cc==108){~mpkV2Set.value(\modDepth,if(raw>=64,0.5,0))};
        };
        if ((cc>=48) && (cc<=55)) {
            if(raw>=64) {~mpkV2Set.value(\timbre,(cc-48).linlin(0,7,-1,1))};
        };
        if(cc==56 && (raw>=64)) {"MPK249 controller ready".postln};
        if(cc==57 && (raw>=64)) {~mpkV2Set.value(\cutoff,250)};
        if(cc==58 && (raw>=64)) {~mpkV2Set.value(\cutoff,6000)};
        if(cc==59 && (raw>=64)) {~mpkV2Set.value(\reverbMix,0.65)};
        if(cc==60 && (raw>=64)) {~mpkV2Set.value(\reverbMix,0.05)};
    },chan:1);

    "MPK249 UNIVERSAL v2: PLAY NOW. Note channel 1; CC channel 2; pad hits channels 2 and 10.".postln;
    "Bank A K1=CC74 cutoff, K2=CC71 resonance, K5-8=ADSR F1=master; B=modulation/FX; C=macros.".postln;
});
)