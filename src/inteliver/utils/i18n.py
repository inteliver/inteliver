import gettext
from pathlib import Path

from fastapi import Request


class TranslationWrapper:
    """
    Singleton class for managing translations using gettext.

    This class initializes the translation object and provides a method for retrieving translated strings.

    Attributes:
        _instance (TranslationWrapper): The singleton instance of the TranslationWrapper class.
        translations (gettext.GNUTranslations): The translation object for managing translations.
    """

    _instance = None

    def __new__(cls):
        """
        Create a new instance of the class if it doesn't exist, otherwise return the existing instance.

        Returns:
            TranslationWrapper: The instance of the class.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_translation()
        return cls._instance

    def init_translation(self):
        """
        Initialize the translation object.

        This method sets up the translation object using the default language and the specified translation directory.
        """
        lang = "en"  # Default language
        # src/inteliver/translation
        locales_dir = Path(__file__).parent.parent / "translations"
        self.translations = gettext.translation(
            "messages", localedir=locales_dir, languages=[lang], fallback=True
        )
        self.translations.install()

    def gettext(self, message: str) -> str:
        """
        Get the translated string for the specified message.

        Args:
            message (str): The message to be translated.

        Returns:
            str: The translated string.
        """
        return self.translations.gettext(message)


async def set_locale(request: Request):
    """
    Set the locale based on the request headers.

    This method retrieves the accept-language header from the request and sets the locale accordingly.

    Args:
        request (Request): The incoming request object.
    """
    translation_wrapper = TranslationWrapper()

    lang = request.headers.get("Accept-Language", "en")
    locales_dir = Path(__file__).parent.parent / "translations"

    translation_wrapper.translations = gettext.translation(
        "messages", localedir=locales_dir, languages=[lang], fallback=True
    )

    translation_wrapper.translations.install()


def _(message: str) -> str:
    """
    Get the translated string for the specified message.

    This method is a shorthand for calling gettext() and is used to retrieve translated strings.

    Args:
        message (str): The message to be translated.

    Returns:
        str: The translated string.
    """
    translation_wrapper = TranslationWrapper()
    return translation_wrapper.gettext(message)
