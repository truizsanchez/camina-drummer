from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import mido
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex

from midi_player import MidiPlayer
from utils.tempo import TempoMode, TempoUtil

logger = logging.getLogger(__name__)


class DrumPracticeApp(App):
    """Main application class for the MIDI practice tool."""

    TITLE_BASE = "Drum Practice MIDI Player"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.player = MidiPlayer()
        self.current_file: Path | None = None

        self.current_file_label: Label | None = None
        self.mute_drums_chk: CheckBox | None = None
        self.mute_others_chk: CheckBox | None = None
        self.tempo_input: TextInput | None = None
        self.tempo_mode_spinner: Spinner | None = None
        self.original_bpm_label: Label | None = None

    def build(self):
        self._configure_window()
        Window.clearcolor = get_color_from_hex("#101010")  # Dark gray background
        root = BoxLayout(orientation="vertical", padding=10, spacing=10)
        root.add_widget(self._build_menu_bar())
        root.add_widget(self._build_main_controls())
        return root

    def _configure_window(self) -> None:
        self.title = self.TITLE_BASE
        Window.minimum_width, Window.minimum_height = 320, 240

    def _build_menu_bar(self) -> BoxLayout:
        bar = BoxLayout(orientation="horizontal", size_hint=(1, None), height=30, spacing=10)
        file_btn = Button(text="File", size_hint=(None, 1), width=80, background_color=get_color_from_hex("#88FF88"))
        file_btn.bind(on_release=self._open_file_dialog)
        bar.add_widget(file_btn)

        self.current_file_label = Label(text="No file loaded", halign="left", valign="middle", color=get_color_from_hex("#00FF00"))
        self.current_file_label.bind(size=self.current_file_label.setter("text_size"))
        bar.add_widget(self.current_file_label)
        return bar

    def _build_main_controls(self) -> BoxLayout:
        layout = BoxLayout(orientation="horizontal", spacing=10)
        controls = BoxLayout(orientation="vertical", spacing=5, padding=5)

        # --- Mute drums checkbox ---
        self.mute_drums_chk = CheckBox(color=get_color_from_hex("#00FF00"))
        row_drums = self._row_with_checkboxes((self.mute_drums_chk, "Mute drums"))
        controls.add_widget(row_drums)
        self.mute_drums_chk.bind(active=lambda _, v: setattr(self.player, "mute_drums", v))

        # --- Mute accompaniment checkbox ---
        self.mute_others_chk = CheckBox(color=get_color_from_hex("#00FF00"))
        row_others = self._row_with_checkboxes((self.mute_others_chk, "Mute accompaniment"))
        controls.add_widget(row_others)
        self.mute_others_chk.bind(active=lambda _, v: setattr(self.player, "mute_others", v))

        # --- Tempo input and mode selector ---
        tempo_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=30, spacing=5)

        tempo_label = Label(text="Tempo:", size_hint=(None, None), height=30, width=60,
                            color=get_color_from_hex("#00FF00"))
        self.tempo_input = TextInput(
            multiline=False,
            size_hint=(1, None),
            height=30,
            foreground_color=get_color_from_hex("#00FF00"),
            background_color=get_color_from_hex("#202020")
        )
        self.tempo_mode_spinner = Spinner(
            text=TempoMode.BPM.value,
            values=[mode.value for mode in TempoMode],
            size_hint=(None, None),
            size=(120, 30),
            background_color=get_color_from_hex("#88FF88"),
            color=get_color_from_hex("#00FF00")
        )

        tempo_row.add_widget(tempo_label)
        tempo_row.add_widget(self.tempo_input)
        tempo_row.add_widget(self.tempo_mode_spinner)
        controls.add_widget(tempo_row)

        # --- Spacer (optional) ---
        controls.add_widget(BoxLayout())

        self.original_bpm_label = Label(
            text="Original BPM: N/A",
            size_hint=(1, None),
            height=30,
            color=get_color_from_hex("#00FF00")
        )
        controls.add_widget(self.original_bpm_label)


        # --- Playback buttons ---
        play_btn = Button(
            text="Play",
            size_hint=(0.5, 1),
            background_color=get_color_from_hex("#88FF88"),
            color=get_color_from_hex("#00FF00")
        )
        stop_btn = Button(
            text="Stop",
            size_hint=(0.5, 1),
            background_color=get_color_from_hex("#330000"),
            color=get_color_from_hex("#FF5555")
        )
        play_btn.bind(on_release=self._on_play)
        stop_btn.bind(on_release=self._on_stop)

        controls.add_widget(self._row_with_widgets(play_btn, stop_btn))

        layout.add_widget(controls)
        return layout

    @staticmethod
    def _row_with_checkboxes(*pairs: tuple[CheckBox, str]) -> BoxLayout:
        row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=30, spacing=5, padding=(10, 0))
        for checkbox, label_text in pairs:
            checkbox.size_hint_x = None
            checkbox.width = 30
            row.add_widget(checkbox)

            label = Label(
                text=label_text,
                size_hint=(1, 1),
                halign="left",
                valign="middle",
                color=get_color_from_hex("#00FF00")
            )
            label.bind(size=label.setter("text_size"))
            row.add_widget(label)
        return row

    @staticmethod
    def _row_with_label_and_widget(label_text: str, widget) -> BoxLayout:
        row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=30, spacing=5)
        row.add_widget(Label(text=label_text, size_hint=(None, None), height=30, width=120, color=get_color_from_hex("#00FF00")))
        row.add_widget(widget)
        return row

    @staticmethod
    def _row_with_widgets(*widgets) -> BoxLayout:
        row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=30, spacing=5)
        for w in widgets:
            row.add_widget(w)
        return row

    def _open_file_dialog(self, _btn) -> None:
        chooser = FileChooserListView(filters=["*.mid"], path=str(Path.home()))
        popup = Popup(title="Select MIDI File", content=chooser, size_hint=(0.9, 0.9))
        chooser.bind(on_submit=lambda *_: self._load_selected_file(chooser, popup))
        popup.open()

    def _load_selected_file(self, chooser: FileChooserListView, popup: Popup) -> None:
        if chooser.selection:
            self.current_file = Path(chooser.selection[0])
            filename = self.current_file.name
            if self.current_file_label:
                self.current_file_label.text = filename
            Window.set_title(f"{self.TITLE_BASE} - {filename}")
            logger.info(f"Loaded MIDI file: {filename}")
            popup.dismiss()
            bpm = TempoUtil.detect_original_bpm(self.current_file)
            self.original_bpm_label.text = f"Original BPM: {bpm:.2f}"

    def _on_play(self, _btn) -> None:
        if not self.current_file:
            logger.warning("No MIDI file selected.")
            return
        mode_text = self.tempo_mode_spinner.text if self.tempo_mode_spinner else TempoMode.BPM.value
        mode = TempoMode(mode_text)
        tempo_factor = TempoUtil.calculate_tempo_factor(self.current_file, self.tempo_input.text, mode)
        logger.info(f"Playing '{self.current_file.name}' with tempo factor {tempo_factor:.2f}")
        self.player.play(str(self.current_file), tempo_factor)

    def _on_stop(self, _btn) -> None:
        logger.info("Stopping playback.")
        self.player.stop()


if __name__ == "__main__":
    DrumPracticeApp().run()
