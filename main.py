import sqlite3
import sys

from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QTableWidget
from PyQt5 import uic


class My_App(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.con = sqlite3.connect('coffee.sqlite')
        self.cur = self.con.cursor()

        self.update_table()

    def update_table(self):
        self.tableWidget.setRowCount(0)
        info = self.cur.execute("""SELECT * FROM coffee""")
        for i1, row in enumerate(info):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for i2, elem in enumerate(row):
                self.tableWidget.setItem(i1, i2, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeColumnsToContents()

    def closeEvent(self, event):
        self.con.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = My_App()
    ex.show()
    sys.exit(app.exec_())
