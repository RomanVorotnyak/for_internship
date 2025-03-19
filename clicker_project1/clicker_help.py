from PyQt5 import uic
from PyQt5.QtWidgets import *


class HelpRulesWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('help.ui', self)