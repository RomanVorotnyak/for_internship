import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
from clicker_help import HelpRulesWindow
from error_clicker import ErrorWindow


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.con = sqlite3.connect("most_finished_clicker.db")
        self.cur = self.con.cursor()
        self.nickname, self.ok_pressed = QInputDialog.getText(self, "Вход",
                                                              "Какое погоняло у тебя на физтехе?")

        uic.loadUi('clicker.ui', self)
        if self.ok_pressed:
            try:
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

                    self.click_number.display(1)
                    self.click_price.display(10)
                    self.fopf_price.display(50)
                    self.frkt_price.display(200)
                    self.fakt_price.display(500)
                    self.fefm_price.display(1000)
                    self.fivt_price.display(5000)
                    self.fupm_price.display(20000)
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
                    self.main_display.display(int(float(save_data1[0])))
                    self.click_number.display(int(float(save_data1[1])))
                    self.click_price.display(int(10 * 1.1 ** float(save_data1[1])))
                    self.fopf_number.display(int(float(save_data1[2])))
                    self.fopf_price.display(int(50 * 1.1 ** float(save_data1[2])))
                    self.fakt_number.display(int(float(save_data1[3])))
                    self.fakt_price.display(int(200 * 1.1 ** float(save_data1[3])))
                    self.frkt_number.display(int(float(save_data1[4])))
                    self.frkt_price.display(int(500 * 1.1 ** float(save_data1[4])))
                    self.fefm_number.display(int(float(save_data1[5])))
                    self.fefm_price.display(int(1000 * 1.1 ** float(save_data1[5])))
                    self.fivt_number.display(int(float(save_data1[6])))
                    self.fivt_price.display(int(5000 * 1.1 ** float(save_data1[6])))
                    self.fupm_number.display(int(float(save_data1[7])))
                    self.fupm_price.display(int(20000 * 1.1 ** float(save_data1[3])))
            except Exception:
                self.return_error()

        self.main_click.clicked.connect(self.norm_click)
        self.click_push.clicked.connect(self.increase)
        self.fopf_push.clicked.connect(self.increase)
        self.frkt_push.clicked.connect(self.increase)
        self.fefm_push.clicked.connect(self.increase)
        self.fakt_push.clicked.connect(self.increase)
        self.fivt_push.clicked.connect(self.increase)
        self.fupm_push.clicked.connect(self.increase)
        self.save_push.clicked.connect(self.save)
        self.tabWidget.tabBarClicked.connect(self.load_leaderboard)
        self.help.clicked.connect(self.return_help)

        self.load_leaderboard()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.autoclick)
        self.timer.start(1000)

    def return_help(self):
        help_window = HelpRulesWindow()
        help_window.exec()

    def return_error(self):
        error_window = ErrorWindow()
        error_window.exec()

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

    def save(self):
        self.cur.execute('''
            UPDATE nicknames_stats
            SET stats = ?
            WHERE nick_id = ?
        ''', (self.get_saved_data(), self.nick_id,))
        self.con.commit()

    def autoclick(self):
        self.main_display.display(self.main_display.intValue() + self.fopf_number.intValue() * 5)
        self.main_display.display(self.main_display.intValue() + self.frkt_number.intValue() * 100)
        self.main_display.display(self.main_display.intValue() + self.fakt_number.intValue() * 250)
        self.main_display.display(self.main_display.intValue() + self.fefm_number.intValue() * 500)
        self.main_display.display(self.main_display.intValue() + self.fivt_number.intValue() * 2500)
        self.main_display.display(self.main_display.intValue() + self.fupm_number.intValue() * 10000)

    def norm_click(self):
        self.main_display.display(self.main_display.value() + self.click_number.value())

    def increase(self):
        if self.sender() == self.click_push and self.main_display.value() >= self.click_price.value():
            self.click_number.display(self.click_number.intValue() + 1)
            self.main_display.display(self.main_display.value() - self.click_price.value())
            self.click_price.display(int(self.click_price.intValue() * 1.1))

        elif self.sender() == self.fopf_push and self.main_display.value() >= self.fopf_price.value():
            self.fopf_number.display(self.fopf_number.intValue() + 1)
            self.fopf_price.display(int(self.fopf_price.intValue() * 1.1))
            self.main_display.display(self.main_display.value() - self.fopf_price.value())

        elif self.sender() == self.fakt_push and self.main_display.value() >= self.fakt_price.value():
            self.fakt_number.display(self.fakt_number.intValue() + 1)
            self.main_display.display(self.main_display.value() - self.fakt_price.value())
            self.fakt_price.display(int(self.fakt_price.intValue() * 1.1))

        elif self.sender() == self.frkt_push and self.main_display.value() >= self.frkt_price.value():
            self.frkt_number.display(self.frkt_number.intValue() + 1)
            self.main_display.display(self.main_display.value() - self.frkt_price.value())
            self.frkt_price.display(int(self.frkt_price.intValue() * 1.1))

        elif self.sender() == self.fefm_push and self.main_display.value() >= self.fefm_price.value():
            self.fefm_number.display(self.fefm_number.intValue() + 1)
            self.main_display.display(self.main_display.value() - self.fefm_price.value())
            self.fefm_price.display(int(self.fefm_price.intValue() * 1.1))

        elif self.sender() == self.fivt_push and self.main_display.value() >= self.fivt_price.value():
            self.fivt_number.display(self.fivt_number.intValue() + 1)
            self.main_display.display(self.main_display.value() - self.fivt_price.value())
            self.fivt_price.display(int(self.fivt_price.intValue() * 1.1))

        elif self.sender() == self.fupm_push and self.main_display.value() >= self.fupm_price.value():
            self.fupm_number.display(self.fupm_number.intValue() + 1)
            self.main_display.display(self.main_display.value() - self.fupm_price.value())
            self.fupm_price.display(int(self.fupm_price.intValue() * 1.1))

    def get_saved_data(self):
        return f'{str(self.main_display.value())};{str(self.click_number.value())};\
                {str(self.fopf_number.value())};{str(self.fakt_number.value())};{str(self.frkt_number.value())};\
                {str(self.fefm_number.value())};{str(self.fivt_number.value())};{str(self.fupm_number.value())}'


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
