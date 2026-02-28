"""
Module qui s'occupe des fonctions en lien avec Wikipedia
"""

import wikipedia
import webbrowser


def summary(text):
    wikipedia.set_lang("fr")
    try:
        summary = wikipedia.summary(text, sentences = 10)
    except wikipedia.DisambiguationError as error:
        summary = wikipedia.summary(error.options[0], sentences = 10)
    except wikipedia.PageError as error:
        wikipedia.set_lang("en")
        summary = wikipedia.summary(text, sentences = 10)

    # TODO Change this to a visual outout in the app because RN it's just a debug print
    print(summary)

def search(text):
    lang = "fr"
    wikipedia.set_lang("fr")
    search = wikipedia.search(text, results = 1, suggestion=False)
    if search == []:
        lang="en"
        wikipedia.set_lang("en")
        search = wikipedia.search(text, results = 1, suggestion=False)

    webbrowser.open("https://"+lang+".wikipedia.com/wiki/"+search[0])