import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
from clicker_help import HelpRulesWindow
from MainWindow import *
from BaseImprove import *


class Clicker:
    def __init__(self):
        super().__init__()
        self.con = sqlite3.connect("most_finished_clicker.db")
        self.cur = self.con.cursor()
        self.cookies = 0
        self.improvements = {'clicks': Clicks(), 'fopf': Fopf(), 'fakt': Fakt(), 'frkt': Frkt(),
                             'fefm': Fefm(), 'fivt': Fivt(), 'fupm': Fupm()}

    def get_cookies(self):
        return self.cookies

    def buy_improvement(self, improvement):
        if self.cookies > improvement.price:
            improvement.number += 1
            improvement.cookies -= improvement.price
            improvement.price = improvement.price * 1.15

    def log_in(self):
        pass

    def autoclick(self):
        for i in self.improvements.values():
            pass

    def click(self):
        self.cookies += Clicks.number

    def increase(self):
        pass

    def save(self):
        pass

    def get_improvement(self, improvement_name):
        return self.improvements[improvement_name]
