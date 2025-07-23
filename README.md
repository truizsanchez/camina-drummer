# Camina Drummer

An interactive desktop tool for practicing drums with any MIDI file—complete tempo control, selective channel muting, and a lightweight Kivy-based UI.

> *Named in homage to a rebel spirit from the Belt, this app helps drummers navigate any tempo frontier.*

## Motivation

Practicing drums with commercial audio tracks can be limiting: tempo is fixed, drums are embedded in the mix, and slowing down audio typically reduces quality. However, there are thousands of freely available MIDI files on platforms like [freemidi.org](https://freemidi.org/), which allow instrument separation and tempo manipulation.

**Camina Drummer** is a minimal but practical application to help drum players:

- Load and play `.mid` files.
- Mute the drum track (usually channel 10) or mute everything *except* the drums.
- Adjust playback speed using either **BPM** or **percentage**.
- Practice interactively with customizable playback and a clear tempo reference.

## Features

- 🎵 **Tempo control** — Adjust speed using BPM or percentage.
- 🧠 **Auto BPM detection** — Displays estimated original BPM from the MIDI file.
- 🥁 **Mute channels** — Toggle mute for drum channel or accompaniment.
- 🎹 **SoundFont-based playback** — Uses FluidSynth and accepts `.sf2` and `.sf3` banks.
- 🖥️ **Cross-platform** — Works on Linux, Windows, and macOS with Python.

## Installation

```bash
# Clone the repository
git clone https://github.com/truizsanchez/camina-drummer.git
cd camina-drummer

# Install dependencies
pip install -r requirements.txt
```

### External Requirements

- Install [FluidSynth](https://www.fluidsynth.org/) on your system.
  - On Ubuntu/Debian: `sudo apt install fluidsynth`
  - On macOS (Homebrew): `brew install fluidsynth`
- Obtain a General MIDI SoundFont (e.g. FluidR3_GM.sf2).

## Configuration

Edit `settings.txt` to point to your SoundFont file:

```
# Path to the GM SoundFont file for FluidSynth:
soundfont_path = /path/to/your/FluidR3_GM.sf2
```

Both `.sf2` and `.sf3` formats are supported.

## Usage

```bash
python main.py
```

Once launched:

1. Click **File** to select a `.mid` file.
2. View the estimated BPM in the interface.
3. Enter a target tempo (either as BPM or percentage).
4. Choose whether to mute drums or accompaniment.
5. Press **Play**. Use **Stop** to stop playback.

## Known Limitations

- Assumes that **channel 10** is used for drums, following the General MIDI standard.
- BPM estimation is based on all `set_tempo` events and reflects the average tempo weighted by duration. However, the tempo input field applies a single factor globally and does not reproduce tempo maps.
- Currently only supports `.mid` files.
- GUI is functional but very minimal (reminiscent of old-school "keygens").
- MIDI playback depends on your SoundFont and system synthesizer. The result may sound closer to a classic RPG or dungeon synth 🐉 than a live performance — but it's still rhythmically accurate and great for practice.

## Roadmap

- [ ] Display drumset notation (tab or piano roll)
- [ ] Show MIDI metadata (track names, instruments, length)
- [ ] Improve GUI aesthetics and usability
- [ ] Gamification: connect a MIDI drum kit and measure timing accuracy vs. expected beats


## Attribution

This project is open and free under the MIT License.  
If you find it useful or build something on top of it, a mention or link back would be greatly appreciated — but it’s not required.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.