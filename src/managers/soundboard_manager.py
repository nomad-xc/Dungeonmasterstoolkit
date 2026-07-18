from pathlib import Path

from src.models.soundboard_sound import SoundboardSound
from src.models.auto_sounds import AutoSounds


class SoundboardManager:

    SOUNDS_FOLDER = Path("library/soundboard/entries")
    AUDIO_FOLDER = Path("library/soundboard/audio")
    AUTO_SOUNDS_FILE = Path("library/soundboard/auto_sounds.json")

    @classmethod
    def audio_folder(cls):
        cls.AUDIO_FOLDER.mkdir(parents=True, exist_ok=True)
        return cls.AUDIO_FOLDER

    #
    # Sound Board - freeform, many
    #

    @classmethod
    def create_sound(cls, name, path):

        sound = SoundboardSound(name=name, path=path)
        cls.save_sound(sound)

        return sound

    @classmethod
    def save_sound(cls, sound):

        cls.SOUNDS_FOLDER.mkdir(parents=True, exist_ok=True)
        sound.save(cls.SOUNDS_FOLDER)

    @classmethod
    def load_sounds(cls):

        cls.SOUNDS_FOLDER.mkdir(parents=True, exist_ok=True)

        sounds = []

        for file in sorted(cls.SOUNDS_FOLDER.glob("*.json")):
            try:
                sounds.append(SoundboardSound.load(file))
            except Exception as e:
                print(f"Failed to load {file}: {e}")

        return sounds

    @classmethod
    def delete_sound(cls, sound):

        file = cls.SOUNDS_FOLDER / f"{sound.name}.json"

        if file.exists():
            file.unlink()

    #
    # Auto Sounds - single fixed-slot record
    #

    @classmethod
    def load_auto_sounds(cls):
        return AutoSounds.load(cls.AUTO_SOUNDS_FILE)

    @classmethod
    def save_auto_sounds(cls, auto_sounds):
        auto_sounds.save(cls.AUTO_SOUNDS_FILE)
