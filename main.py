import sys
from PyQt6.QtWidgets import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мои задачи")
        self.resize(600, 700)

        self.my_tasks = []

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # ввод названия
        root.addWidget(QLabel("Что надо сделать:"))
        self.title_edit = QLineEdit()
        root.addWidget(self.title_edit)

        # описание
        root.addWidget(QLabel("Подробнее:"))
        self.desc_edit = QTextEdit()
        root.addWidget(self.desc_edit)

        # приоритет
        root.addWidget(QLabel("Насколько срочно:"))
        pr = QHBoxLayout()
        self.p_low = QRadioButton("Низкий")
        self.p_mid = QRadioButton("Средний")
        self.p_high = QRadioButton("Высокий")
        self.p_mid.setChecked(True)
        grp = QButtonGroup(self)
        grp.addButton(self.p_low, 1)
        grp.addButton(self.p_mid, 2)
        grp.addButton(self.p_high, 3)
        pr.addWidget(self.p_low)
        pr.addWidget(self.p_mid)
        pr.addWidget(self.p_high)
        root.addLayout(pr)

        # галочки
        root.addWidget(QLabel("Дополнительно:"))
        grid = QGridLayout()
        self.c_imp = QCheckBox("Важное")
        self.c_notif = QCheckBox("Уведомить")
        self.c_fav = QCheckBox("В избранное")
        grid.addWidget(self.c_imp, 0, 0)
        grid.addWidget(self.c_notif, 0, 1)
        grid.addWidget(self.c_fav, 1, 0)
        root.addLayout(grid)

        # кнопки
        btns = QHBoxLayout()
        self.b_add = QPushButton("Добавить")
        self.b_clear = QPushButton("Очистить")
        self.b_del = QPushButton("Удалить последнюю")
        self.b_add.clicked.connect(self.add_task)
        self.b_clear.clicked.connect(self.reset_fields)
        self.b_del.clicked.connect(self.remove_last)
        btns.addWidget(self.b_add)
        btns.addWidget(self.b_clear)
        btns.addWidget(self.b_del)
        root.addLayout(btns)

        # список задач
        root.addWidget(QLabel("Список задач:"))
        self.tasks_view = QListWidget()
        root.addWidget(self.tasks_view)

        # статус
        st = QHBoxLayout()
        self.status = QLabel("Статус: готово")
        self.counter = QLabel("Задач: 0")
        st.addWidget(self.status)
        st.addStretch()
        st.addWidget(self.counter)
        root.addLayout(st)

    def add_task(self):
        t = self.title_edit.text().strip()
        if not t:
            QMessageBox.warning(self, "Ошибка", "Введите название!")
            return
        if self.p_low.isChecked():
            pr = "Низкий"
        elif self.p_high.isChecked():
            pr = "Высокий"
        else:
            pr = "Средний"
        extra = []
        if self.c_imp.isChecked():
            extra.append("важное")
        if self.c_notif.isChecked():
            extra.append("уведомить")
        if self.c_fav.isChecked():
            extra.append("избранное")
        self.my_tasks.append({
            "title": t,
            "desc": self.desc_edit.toPlainText().strip(),
            "priority": pr,
            "extra": extra
        })
        self.redraw()
        self.status.setText("Статус: задача создана")
        self.counter.setText(f"Задач: {len(self.my_tasks)}")

    def redraw(self):
        self.tasks_view.clear()
        for i, task in enumerate(self.my_tasks, 1):
            self.tasks_view.addItem(f"{i}. [{task['priority']}] {task['title']}")

    def reset_fields(self):
        self.title_edit.clear()
        self.desc_edit.clear()
        self.p_mid.setChecked(True)
        for cb in (self.c_imp, self.c_notif, self.c_fav):
            cb.setChecked(False)
        self.status.setText("Статус: готово")

    def remove_last(self):
        if not self.my_tasks:
            return
        self.my_tasks.pop()
        self.redraw()
        self.counter.setText(f"Задач: {len(self.my_tasks)}")


app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())