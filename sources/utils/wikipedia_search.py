"""
Module qui s'occupe des fonctions en lien avec Wikipedia
"""

import webbrowser
import wikipedia
from utils.logger import setup_logger

logger = setup_logger(__name__)


def summarize_wikipedia_page(text, lang) -> str:
    logger.info(f"Récupération du résumé Wikipedia pour: {text} (lang={lang})")
    if lang in wikipedia.languages():
        wikipedia.set_lang(lang)
        logger.debug(f"Langue Wikipedia définie: {lang}")
    else:
        logger.warning(
            f"Langue '{lang}' non supportée par Wikipedia, utilisation de l'anglais par défaut."
        )
        wikipedia.set_lang("en")
    try:
        summary = wikipedia.summary(text, sentences=10)
        logger.info(f"Résumé Wikipedia obtenu ({len(summary)} caractères)")
        return summary
    except wikipedia.DisambiguationError as error:
        logger.info(
            f"Page d'ambigüité, utilisation de la première option: {error.options[0]}"
        )
        summary = wikipedia.summary(error.options[0], sentences=10)
        return summary
    except wikipedia.PageError as error:
        logger.warning(f"Page non trouvée, tentative en anglais: {error}")
        wikipedia.set_lang("en")
        summary = wikipedia.summary(text, sentences=10)
        logger.info(f"Résumé Wikipedia obtenu en anglais ({len(summary)} caractères)")
        return summary


def open_web_browser_wikipedia_search(text, lang):
    if lang in wikipedia.languages():
        wikipedia.set_lang(lang)
    else:
        logger.warning(
            f"Langue '{lang}' non supportée par Wikipedia, utilisation de l'anglais par défaut."
        )
        wikipedia.set_lang("en")
    search = wikipedia.search(text, results=1, suggestion=False)
    if not search:
        lang = "en"
        wikipedia.set_lang("en")
        search = wikipedia.search(text, results=1, suggestion=False)

    webbrowser.open("https://" + lang + ".wikipedia.com/wiki/" + search[0])
