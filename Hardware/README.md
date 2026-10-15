# Hardware preset: safe bulk editing, no manual controller programming

You must first obtain one genuine MPK249 **single-program** SysEx dump. Use the [independent editor](https://github.com/dobemad/MPK249). Preserve original files.

`python3 Hardware/apply_to_mpk249_dump.py input.syx --slot 30` makes a separate `input_MPKUNIV2.syx` with 141 configured controls. The input's original program number is preserved unless `--slot` is specified. Choose a destination slot only after backing up its previous content.

Load the output into the editor, visually inspect the CC/channel fields and pad bank data, upload it to the MPK249, then select the program on the keyboard. The Python script **does not transmit** MIDI, rewrite firmware, or set inaccessible controls such as keyboard MIDI channel / mod wheel / transport. The hardware remains unmodified until you explicitly upload with the editor.

Built from public MPK249 reverse engineering. Not tested on this physical keyboard: stop if editor display disagrees with this map.