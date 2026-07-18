from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


_players = []


def play_sound(path):

    if not path or not Path(path).exists():
        return

    _players[:] = [p for p in _players if p[0].playbackState() != QMediaPlayer.StoppedState]

    player = QMediaPlayer()
    audio_output = QAudioOutput()
    player.setAudioOutput(audio_output)
    player.setSource(QUrl.fromLocalFile(str(path)))

    player.play()

    _players.append((player, audio_output))
