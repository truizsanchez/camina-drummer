# midi_player.py
from functools import cached_property, lru_cache
import logging
import mido
import fluidsynth
import threading
import time
import os

logger = logging.getLogger(__name__)

class MidiPlayer:
    """Handles MIDI file playback using FluidSynth."""
    def __init__(self):
        self.soundfont_path = self._load_soundfont_path()
        self.mute_drums = False    # mute drum channel (10, index 9)
        self.mute_others = False   # mute all other channels
        self._play_thread = None
        self._stop_flag = False

    def _load_soundfont_path(self):
        """Reads the soundfont path from settings.txt."""
        config_file = "settings.txt"
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"{config_file} not found with SoundFont path.")
        path = None
        with open(config_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue  # ignore comments/empty lines
                if "=" in line:
                    key, value = line.split("=", 1)
                    if key.strip().lower() in ("soundfont", "soundfont_path", "soundfont path"):
                        path = value.strip()
                else:
                    path = line.strip()
        if not path:
            raise ValueError("No soundfont path found in settings.txt")
        if not os.path.exists(path):
            raise FileNotFoundError(f"The specified soundfont does not exist: {path}")
        return path

    def play(self, midi_file_path, tempo_factor=1.0):
        """
        Starts playback of a MIDI file in a separate thread.
        - midi_file_path: path to the .mid file
        - tempo_factor: time multiplier (1.0 = original tempo, 2.0 = half speed, 0.5 = double speed)
        """
        if self._play_thread and self._play_thread.is_alive():
            logger.warning("A MIDI is already playing. Stop current playback before starting a new one.")
            return

        try:
            midi = mido.MidiFile(midi_file_path)
        except Exception as e:
            logger.error(f"Error loading MIDI file: {e}")
            return

        if tempo_factor <= 0:
            tempo_factor = 1.0
        logger.info(f"Playing '{os.path.basename(midi_file_path)}' (tempo factor = {tempo_factor:.2f})...")

        self._stop_flag = False

        def _play_thread_func():
            fs = fluidsynth.Synth()
            if os.name == "posix":
                try:
                    fs.start(driver="alsa")
                except Exception:
                    fs.start(driver="pulseaudio")
            else:
                fs.start(driver="dsound")
            sfid = fs.sfload(self.soundfont_path)
            fs.program_select(0, sfid, 0, 0)
            fs.program_select(9, sfid, 128, 0)

            start_time = time.time()
            for msg in midi:
                if self._stop_flag:
                    break
                wait = msg.time * tempo_factor
                if wait > 0.0:
                    time.sleep(wait)
                if msg.type == 'note_on' and not self._stop_flag:
                    if (self.mute_drums and msg.channel == 9) or (self.mute_others and msg.channel != 9):
                        pass
                    else:
                        fs.noteon(msg.channel, msg.note, msg.velocity)
                elif msg.type == 'note_off' and not self._stop_flag:
                    if (self.mute_drums and msg.channel == 9) or (self.mute_others and msg.channel != 9):
                        pass
                    else:
                        fs.noteoff(msg.channel, msg.note)
                elif msg.type == 'program_change':
                    fs.program_change(msg.channel, msg.program)
                elif msg.type == 'set_tempo':
                    pass

            fs.delete()
            elapsed = time.time() - start_time
            logger.info(f"Playback finished (actual duration: {elapsed:.1f} s).")

        self._play_thread = threading.Thread(target=_play_thread_func, daemon=True)
        self._play_thread.start()

    def stop(self):
        """Stops current playback, if any."""
        if self._play_thread and self._play_thread.is_alive():
            logger.info("Stopping playback...")
            self._stop_flag = True
            self._play_thread.join(timeout=1.0)
            self._play_thread = None
            logger.info("Playback stopped.")
        else:
            logger.info("No active playback to stop.")

@lru_cache
def estimate_midi_bpm(midi_file_path):
    """
    Estimate the average BPM of a MIDI file by analyzing all set_tempo messages.
    It calculates a time-weighted average based on how long each tempo was in effect.
    Returns:
        float: estimated BPM, or 120.0 as a fallback.
    """
    try:
        midi = mido.MidiFile(midi_file_path)
        ticks_per_beat = midi.ticks_per_beat
        current_tempo = 500000

        total_seconds = 0.0
        weighted_bpm_sum = 0.0
        absolute_tick = 0
        tempo_changes = []

        for msg in midi:
            if not msg.is_meta:
                continue
            absolute_tick += msg.time
            if msg.type == 'set_tempo':
                tempo_changes.append((absolute_tick, msg.tempo))

        if not tempo_changes:
            bpm = mido.tempo2bpm(current_tempo)
            logger.info(f"Estimated BPM (default): {bpm:.2f}")
            return bpm

        total_ticks = sum(msg.time for msg in midi)
        tempo_changes.append((total_ticks, None))

        for i in range(len(tempo_changes) - 1):
            tick_i, tempo_i = tempo_changes[i]
            tick_next, _ = tempo_changes[i + 1]
            delta_ticks = tick_next - tick_i
            delta_seconds = mido.tick2second(delta_ticks, ticks_per_beat, tempo_i)
            bpm = mido.tempo2bpm(tempo_i)
            weighted_bpm_sum += bpm * delta_seconds
            total_seconds += delta_seconds

        if total_seconds == 0:
            bpm = mido.tempo2bpm(current_tempo)
            logger.info(f"Estimated BPM (default): {bpm:.2f}")
            return bpm

        estimated_bpm = weighted_bpm_sum / total_seconds
        logger.info(f"Estimated BPM: {estimated_bpm:.2f}")
        return estimated_bpm

    except Exception as e:
        logger.warning(f"Error estimating MIDI BPM: {e}")
        logger.info("Estimated BPM: 120.0 (fallback)")
        return 120.0
