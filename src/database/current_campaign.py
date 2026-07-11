from pathlib import Path


class CurrentCampaign:

    _name = None
    _path = None

    @classmethod
    def load(cls, name):

        cls._name = name
        cls._path = Path("campaigns") / name

    @classmethod
    def unload(cls):

        cls._name = None
        cls._path = None

    @classmethod
    def loaded(cls):

        return cls._name is not None

    @classmethod
    def name(cls):

        return cls._name

    @classmethod
    def path(cls):

        return cls._path