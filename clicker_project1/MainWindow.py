import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
from clicker_help import HelpRulesWindow
from clicker import *
from BaseImprove import *


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.clicker = Clicker()

        self.con = sqlite3.connect("finish_clicker.db")
        self.cur = self.con.cursor()
        self.nickname, self.ok_pressed = QInputDialog.getText(self, "registration/login",
                                                              "Какое погоняло у тебя на физтехе?")

        uic.loadUi('clicker.ui', self)
        if self.ok_pressed:
            if not self.cur.execute('''  
                SELECT nick FROM nicknames
                    WHERE nick = ? ''', (self.nickname,)
                                    ).fetchall():
                self.cur.execute('''
                    INSERT INTO nicknames(nick) VALUES(?)
                        ''', (self.nickname,))
                self.con.commit()
                self.nick_id = self.cur.execute('''
                    SELECT id FROM nicknames
                        WHERE nick == ?
                    ''', (self.nickname,)).fetchall()[0][0]

                self.save_data = '0;0;0;0;0;0;0;0'
                self.cur.execute('''
                    INSERT INTO nicknames_stats(stats,nick_id) VALUES(?,?)
                ''', (self.save_data, self.nick_id,))
                self.con.commit()

            else:
                self.nick_id = self.cur.execute('''
                                                    SELECT id FROM nicknames
                                                        WHERE nick == ?
                                                    ''', (self.nickname,)).fetchall()[0][0]
                self.save_data = (self.cur.execute('''
                                    SELECT stats FROM nicknames_stats
                                        WHERE nick_id == ?
                                ''', (self.nick_id,)).fetchall())[0][0]
                save_data1 = self.save_data.split(';')
                updateQLC(save_data1)

        self.main_click.clicked.connect(self.clicker.click())
        self.click_push.clicked.connect(self.buy_improvement())
        self.fopf_push.clicked.connect(self.buy_improvement())
        self.fakt_push.clicked.connect(self.buy_improvement())
        self.frkt_push.clicked.connect(self.buy_improvement())
        self.fefm_push.clicked.connect(self.buy_improvement())
        self.fivt_push.clicked.connect(self.buy_improvement())
        self.fupm_push.clicked.connect(self.buy_improvement())
        self.save_push.clicked.connect(self.save)
        self.tabWidget.tabBarClicked.connect(self.load_leaderboard)
        self.help.clicked.connect(self.return_help)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.Wautoclick)
        self.timer.start(1000)

    def window_autoclick(self):
        self.сlicker.autoclick()

    def return_help(self):
        window = HelpRulesWindow()
        window.exec()

    def buy_improvement(self):
        improvement_name = self.sender().text()
        improvement = self.clicker.get_improvement(improvement_name)
        self.clicker.buy_improvement(improvement)

    def load_leaderboard(self):
        result = self.cur.execute(f'''
                            SELECT nick_id,stats FROM nicknames_stats
                            ''').fetchall()
        result1 = []
        for i in result:
            nick = self.cur.execute('''
                        SELECT nick from nicknames
                        WHERE id = ?
                    ''', (i[0],)).fetchall()

            save = i[1]
            result1.append([nick[0][0], save.split(';')[0].split('.')[0]])
        self.table.setRowCount(len(result1))
        self.table.setColumnCount(2)
        for i, elem in enumerate(result1):
            for j, val in enumerate(elem):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))
        self.table.setHorizontalHeaderLabels(['nick', 'save'])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
