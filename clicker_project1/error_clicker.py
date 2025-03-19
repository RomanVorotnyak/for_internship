from PyQt5 import uic
from PyQt5.QtWidgets import *


class ErrorWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('error.ui', self)