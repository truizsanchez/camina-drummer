from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path

import mido

logger = logging.getLogger(__name__)


class TempoMode(Enum):
    BPM = "BPM"
    PERCENTAGE = "Percentage"


class TempoUtil:

    @classmethod
    def calculate_tempo_factor(cls, midi_path: Path, user_input: str | None, mode: TempoMode = TempoMode.BPM) -> float:
        if not user_input:
            return 1.0
        text = user_input.strip()
        try:
            if mode == TempoMode.PERCENTAGE:
                percent = float(text)
                return 100.0 / percent if percent > 0 else 1.0
            desired_bpm = float(text)
            if desired_bpm <= 0:
                return 1.0
            original_bpm = cls.detect_original_bpm(midi_path)
            return original_bpm / desired_bpm
        except ValueError:
            logger.warning(f"Invalid tempo input: {text}")
            return 1.0


    @classmethod
    def detect_original_bpm(cls, midi_path: Path) -> float:
        try:
            for msg in mido.MidiFile(str(midi_path)):
                if msg.type == "set_tempo":
                    return mido.tempo2bpm(msg.tempo)
        except Exception as exc:
            logger.warning(f"Could not read tempo from MIDI: {exc}")
        return 120.0


