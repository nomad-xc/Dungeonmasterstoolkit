from pathlib import Path

from src.models.token import Token


class TokenManager:

    TOKENS_FOLDER = Path("library/tokens")
    IMAGES_FOLDER = Path("library/tokens/images")

    @classmethod
    def images_folder(cls):
        cls.IMAGES_FOLDER.mkdir(parents=True, exist_ok=True)
        return cls.IMAGES_FOLDER

    @classmethod
    def create_token(cls, name, path):

        token = Token(name=name, path=path)
        cls.save_token(token)

        return token

    @classmethod
    def save_token(cls, token):

        cls.TOKENS_FOLDER.mkdir(parents=True, exist_ok=True)
        token.save(cls.TOKENS_FOLDER)

    @classmethod
    def load_tokens(cls):

        cls.TOKENS_FOLDER.mkdir(parents=True, exist_ok=True)

        tokens = []

        for file in sorted(cls.TOKENS_FOLDER.glob("*.json")):
            try:
                tokens.append(Token.load(file))
            except Exception as e:
                print(f"Failed to load {file}: {e}")

        return tokens

    @classmethod
    def delete_token(cls, token):

        file = cls.TOKENS_FOLDER / f"{token.name}.json"

        if file.exists():
            file.unlink()
