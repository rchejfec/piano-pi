# Piano Pi Brain — v2 Roadmap

Living doc. Items are loosely ordered by dependency, not priority.

## Phase A: Sound Curation 🎹
*No new hardware. Just software + ears.*

- [ ] Research and download 2–3 dedicated piano SoundFonts (Salamander Grand, etc.)
- [ ] A/B test on the Pi through the speaker — pick the best "home" sound
- [ ] Curate instrument list: 2–3 core sounds + 4–5 fun/crazy ones
- [ ] Add "reset to home" gesture — e.g. hold Next button for 1s to jump back to core piano
- [ ] Explore: does the Keystation sound different with a better SF2? (velocity curves, dynamics)

## Phase B: MiniLab 3 + Controller Mapping 🎛️
*Plug in the MiniLab, see what it sends, map everything useful.*

- [ ] Connect MiniLab 3, run `aseqdump` — document all pads, knobs, sliders, buttons
- [ ] Find its MIDI channel (probably different from Keystation's ch4)
- [ ] Multi-controller support — make channel configurable or auto-detect
- [ ] **Drums via pads**: Route MiniLab pads to GM channel 9 (drum kit)
- [ ] **Drums via keys**: Add drum kits as selectable instruments in next/prev list
- [ ] **Knobs → synth params**: Map to reverb depth, chorus, filter cutoff, etc.
- [ ] **Sliders → volume**: Could replace physical speaker volume knob
- [ ] Decide: do we need different "profiles" per controller?

## Phase C: Practice Features 🥁
*Depends on B (controller mapping informs what controls are available).*

- [ ] **Metronome** — FluidSynth can trigger a click on a timer. BPM control via knob?
- [ ] **Simple looper** — Record a MIDI phrase, loop it, play over it
- [ ] **Arpeggiator** — Hold keys, auto-arpeggiate at BPM
- [ ] **Backing tracks** — FluidSynth plays .mid files natively. Load a few practice loops
- [ ] Evaluate: which of these need new buttons vs. can use controller controls?

## Phase D: Interface Alternatives 📱
*Independent of B/C. Can explore anytime.*

- [ ] **Web portal** — Flask/FastAPI on the Pi, served over local WiFi
  - Phone opens `http://piano-pi-local:8080`
  - Instrument picker, metronome BPM, volume slider
  - Way more flexible than buttons, no new hardware
  - Gets around the "no screen" problem elegantly
- [ ] **IR remote** — Arduino kit has IR receiver + remote
  - Quick instrument switching from across the room
  - Simpler than web portal but less flexible
- [ ] **LCD display** — Kit has LCD with pin header
  - Show current instrument, BPM, status
  - Nice but not essential if we do web portal

> [!TIP]
> The web portal is the most bang-for-buck here. One implementation gives you unlimited UI on a device you already carry (phone). IR remote is a fun tinkering project though.

## Phase E: Hardware & Form Factor 🔧
*Longer-term conversation.*

- [ ] Speaker: powered mini speaker vs. Bluetooth vs. small amp board?
- [ ] Audio quality: USB DAC dongle (~$5) vs. Pi DAC HAT (~$15)
- [ ] Power: USB battery pack? Always-on with wall plug?
- [ ] Case: 3D print? Project box? Exposed breadboard aesthetic?
- [ ] Could the Pi Zero 2W handle this? (smaller, cheaper, WiFi built-in)

## Open Questions

1. **Profiles per controller** — Do we want the Keystation and MiniLab to have different instrument lists / behaviors when plugged in?
2. **Rust on the metronome** — if we want rock-solid timing, the metronome might need to run as a separate FluidSynth channel rather than from Python. Worth testing Python timing first.
3. **Scope creep guard** — at what point does this want a screen and become "fancy software" again? The web portal walks that line nicely.
