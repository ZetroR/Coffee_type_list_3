import sqlite3
import sys
import traceback

from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QMessageBox
from PyQt5.QtWidgets import QTableWidget, QDoubleSpinBox, QComboBox, QPlainTextEdit
from PyQt5 import uic


class My_App(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.con = sqlite3.connect('coffee.sqlite')
        self.cur = self.con.cursor()

        self.cook = {}
        for i in self.cur.execute("""SELECT * FROM cooked"""):
            self.cook[i[0]] = i[1]

        self.mace = {}
        for i in self.cur.execute("""SELECT * FROM maced"""):
            self.mace[i[0]] = i[1]

        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)

        self.update_table()
        self.tableWidget.cellDoubleClicked.connect(self.change_coffee)
        self.pushButton.clicked.connect(self.add_coffee)
        self.pushButton_2.clicked.connect(self.delete_coffee)

    def update_table(self):
        self.tableWidget.setRowCount(0)
        info = self.cur.execute("""SELECT * FROM coffee""")
        for i1, row in enumerate(info):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for i2, elem in enumerate(row):
                if i2 == 2:
                    self.tableWidget.setItem(i1, i2, QTableWidgetItem(str(self.cook[elem])))
                elif i2 == 3:
                    self.tableWidget.setItem(i1, i2, QTableWidgetItem(str(self.mace[elem])))
                else:
                    self.tableWidget.setItem(i1, i2, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeColumnsToContents()

    def add_coffee(self):
        dial = Change_Dialog(self)
        dial.exec()
        self.con.commit()
        self.update_table()

    def change_coffee(self, y):
        dial = Change_Dialog(self)
        dial.load_info(int(self.tableWidget.item(y, 0).text()))
        dial.exec()
        self.con.commit()
        self.update_table()

    def delete_coffee(self):
        a = list(set([i.row() for i in self.tableWidget.selectedIndexes()]))
        if a != []:
            value = QMessageBox.question(self, '', "Вы действительно хотите удалить выбранные данные?",
                                         QMessageBox.Yes, QMessageBox.No)
            if value == QMessageBox.Yes:
                for i in a:
                    self.cur.execute("DELETE FROM coffee WHERE id = ?", (int(self.tableWidget.item(i, 0).text()),))
        self.con.commit()
        self.update_table()


    def closeEvent(self, event):
        self.con.close()


class Change_Dialog(QDialog):
    def __init__(self, par):
        super().__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.cur = par.cur
        self.id = None

        self.comboBox.addItems([i[1] for i in self.cur.execute("""SELECT * FROM maced""")])
        self.comboBox_2.addItems([i[1] for i in self.cur.execute("""SELECT * FROM cooked""")])

        self.pushButton.clicked.connect(self.act)
        self.pushButton_2.clicked.connect(self.close)

    def load_info(self, id):
        self.id = id
        info = next(self.cur.execute("""SELECT * FROM coffee    WHERE id == ?""", (id,)))

        self.lineEdit.setText(info[1])
        self.spinBox.setValue(info[6])
        self.doubleSpinBox.setValue(info[5])
        self.plainTextEdit.setPlainText(info[4])
        self.comboBox_2.setCurrentIndex(info[2] - 1)
        self.comboBox.setCurrentIndex(info[3] - 1)

    def act(self):
        cooked = next(self.cur.execute("""SELECT ID FROM cooked WHERE name == ?""", (self.comboBox_2.currentText(),)))[0]
        maced = next(self.cur.execute("""SELECT ID FROM maced WHERE name == ?""", (self.comboBox.currentText(),)))[0]

        if self.id is None:
            self.create_task(cooked, maced)
        else:
            self.change_task(cooked, maced)

    def change_task(self, cook, mace):
        if self.check_correct():
            self.cur.execute("""UPDATE coffee
                SET coffee_name = ?, cooked_type = ?, maced_type = ?, description = ?, price = ?, volume = ?
                WHERE ID = ?""", (self.lineEdit.text(), cook, mace, self.plainTextEdit.toPlainText(),
                                  self.doubleSpinBox.value(), self.spinBox.value(), self.id))
            self.close()

    def create_task(self, cook, mace):
        if self.check_correct():
            self.cur.execute("""INSERT INTO coffee(coffee_name, cooked_type, maced_type, description, price, volume)
            VALUES(?, ?, ?, ?, ?, ?)""", (self.lineEdit.text(), cook, mace, self.plainTextEdit.toPlainText(),
                                          self.doubleSpinBox.value(), self.spinBox.value()))
            self.close()

    def check_correct(self):
        if self.lineEdit.text() == '':
            self.label_7.setText("Название не может быть пустым")
        elif self.doubleSpinBox.value() == 0:
            self.label_7.setText("Цена должна быть больше 0")
        elif self.spinBox.value() == 0:
            self.label_7.setText("Объем не может быть нулевым")
        else:
            return True
        return False


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("Oбнаружена ошибка !:", tb)


sys.excepthook = excepthook


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = My_App()
    ex.show()
    sys.exit(app.exec_())
