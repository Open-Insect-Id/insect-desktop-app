"""
Module qui s'occupe des fonctions en lien avec Wikipedia
"""

import webbrowser
import wikipedia
from utils.logger import setup_logger

logger = setup_logger(__name__)


def summarize_wikipedia_page(text, lang) -> str:
    if lang in wikipedia.languages():   
        wikipedia.set_lang(lang)
    else:
        logger.warning(f"Langue '{lang}' non supportée par Wikipedia, utilisation de l'anglais par défaut.")
        wikipedia.set_lang("en")
    try:
        summary = wikipedia.summary(text, sentences = 10)
    except wikipedia.DisambiguationError as error:
        summary = wikipedia.summary(error.options[0], sentences = 10)
    except wikipedia.PageError as error:
        wikipedia.set_lang("en")
        summary = wikipedia.summary(text, sentences = 10)

    return summary

def open_web_browser_wikipedia_search(text, lang):
    if lang in wikipedia.languages():
        wikipedia.set_lang(lang)
    else:
        logger.warning(f"Langue '{lang}' non supportée par Wikipedia, utilisation de l'anglais par défaut.")
        wikipedia.set_lang("en")
    search = wikipedia.search(text, results = 1, suggestion=False)
    if not search:
        lang="en"
        wikipedia.set_lang("en")
        search = wikipedia.search(text, results = 1, suggestion=False)

    webbrowser.open("https://"+lang+".wikipedia.com/wiki/"+search[0])