import random
import logging


def status_message(self, key):
    msg = self.i18n.t(key) if hasattr(self, "i18n") else str(key)
    if msg is None:
        return str(key)
    return msg


def update_status(self, text):
    self.sidebar.update_status(text)


def update_map_btn(self):
    if self.has_search_result():
        self.sidebar.set_map_state("normal")
    else:
        self.sidebar.set_map_state("disabled")


def update_clear_btn(self):
    if self.image_path:
        self.sidebar.set_clear_state("normal")
    else:
        self.sidebar.set_clear_state("disabled")


def has_search_result(self):
    return self.insect_species and (self.computed_insect_name is not None)
