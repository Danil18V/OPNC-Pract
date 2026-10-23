import json
import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QTextEdit,
    QPushButton, QListWidget, QListWidgetItem, QMessageBox,
    QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QComboBox, QDialog, QDialogButtonBox,
)

# файл, куда сохраняем задачи
TASKS_FILE = "tasks.json"


class AboutWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О программе")
        self.setFixedSize(340, 200)

        lay = QVBoxLayout(self)

        name = QLabel("Task Manager 2.0")
        name.setObjectName("aboutTitle")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info = QLabel(
            "Менеджер задач на PyQt6.\n\n"
            "- приоритеты задач\n"
            "- удаление задачи\n"
            "- сохранение в json\n\n"

        )
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setWordWrap(True)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btns.accepted.connect(self.accept)

        lay.addWidget(name)
        lay.addWidget(info)
        lay.addWidget(btns)


class TaskManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Task Manager 2.0")
        self.resize(720, 620)

        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(12)

        self._make_input_area()
        self._make_buttons()
        self._make_list_area()
        self._make_status()

        # подключаем сигналы
        self.add_button.clicked.connect(self.add_task)
        self.clear_button.clicked.connect(self.clear_tasks)
        self.delete_button.clicked.connect(self.delete_task)
        self.about_button.clicked.connect(self.open_about)
        self.title_input.textChanged.connect(self.on_title_changed)

        self.setStyleSheet(self._get_styles())
        self.load_from_file()
        self.refresh_status()
        self.on_title_changed("")

    # ---------- интерфейс ----------

    def _make_input_area(self):
        box = QGroupBox("Новая задача")
        form = QFormLayout(box)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Название задачи...")
        self.title_input.setMaxLength(120)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Описание (необязательно)...")
        self.desc_input.setFixedHeight(70)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Низкий", "Средний", "Высокий"])
        self.priority_combo.setCurrentIndex(1)

        self.symbols_label = QLabel("Название: 0 символов")
        self.symbols_label.setObjectName("symbolsLabel")

        form.addRow("Название:", self.title_input)
        form.addRow("Описание:", self.desc_input)
        form.addRow("Приоритет:", self.priority_combo)
        form.addRow("", self.symbols_label)

        self.main_layout.addWidget(box)

    def _make_buttons(self):
        top = QHBoxLayout()
        self.add_button = QPushButton("Добавить задачу")
        self.add_button.setObjectName("addButton")
        self.clear_button = QPushButton("Очистить список")
        self.clear_button.setObjectName("clearButton")
        top.addWidget(self.add_button)
        top.addWidget(self.clear_button)

        bottom = QHBoxLayout()
        self.delete_button = QPushButton("Удалить выбранную")
        self.delete_button.setObjectName("deleteButton")
        self.about_button = QPushButton("О программе")
        self.about_button.setObjectName("aboutButton")
        bottom.addWidget(self.delete_button)
        bottom.addWidget(self.about_button)

        self.main_layout.addLayout(top)
        self.main_layout.addLayout(bottom)

    def _make_list_area(self):
        box = QGroupBox("Список задач")
        lay = QVBoxLayout(box)
        self.task_list = QListWidget()
        self.task_list.setObjectName("taskList")
        lay.addWidget(self.task_list)
        self.main_layout.addWidget(box, stretch=1)

    def _make_status(self):
        self.status_label = QLabel("Задач: 0")
        self.status_label.setObjectName("statusLabel")
        self.main_layout.addWidget(self.status_label)
        self.statusBar().showMessage("Готово")

    def _get_styles(self):
        # все стили в одном месте
        return """
        QMainWindow { background-color: #f4f6f8; }

        QGroupBox {
            font-weight: bold;
            border: 1px solid #c8d0d8;
            border-radius: 8px;
            margin-top: 12px;
            padding: 12px 8px 8px 8px;
            background-color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin; left: 12px;
            padding: 0 6px; color: #2c3e50;
        }

        QLineEdit, QTextEdit, QComboBox {
            border: 1px solid #b0bcc7; border-radius: 6px;
            padding: 6px 8px; background-color: #ffffff;
            color: #1a2733;
        }
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border: 2px solid #4a90e2;
        }
        QLineEdit::placeholder, QTextEdit::placeholder {
            color: #9aa5b1;
        }
        QComboBox::drop-down { border: none; width: 20px; }
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #1a2733;
            selection-background-color: #d6e8fb;
            selection-color: #1a2733;
        }

        QPushButton {
            border-radius: 6px; padding: 8px 16px;
            font-weight: bold; color: #ffffff;
            background-color: #7f8c8d;
        }
        QPushButton:hover   { background-color: #95a5a6; }
        QPushButton:pressed { background-color: #5d6d6e; }

        QPushButton#addButton     { background-color: #2ecc71; }
        QPushButton#addButton:hover    { background-color: #27ae60; }
        QPushButton#clearButton   { background-color: #e74c3c; }
        QPushButton#clearButton:hover    { background-color: #c0392b; }
        QPushButton#deleteButton  { background-color: #e67e22; }
        QPushButton#deleteButton:hover    { background-color: #ca6f1e; }
        QPushButton#aboutButton   { background-color: #8e44ad; }
        QPushButton#aboutButton:hover   { background-color: #7d3c98; }

        QListWidget#taskList {
            border: 1px solid #b0bcc7; border-radius: 6px;
            background-color: #ffffff; padding: 4px;
            color: #1a2733;
        }
        QListWidget#taskList::item {
            padding: 6px 8px; border-bottom: 1px solid #eef1f4;
        }
        QListWidget#taskList::item:selected {
            background-color: #d6e8fb; color: #1a2733;
        }

        QLabel#symbolsLabel { color: #7f8c8d; font-size: 11px; }
        QLabel#statusLabel  { color: #2c3e50; font-size: 13px;
                              font-weight: bold; padding: 4px; }
        QLabel#aboutTitle   { font-size: 18px; font-weight: bold; color: #2c3e50; }
        """

    # ---------- сохранение / загрузка ----------

    def load_from_file(self):
        if not os.path.exists(TASKS_FILE):
            return
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                tasks = json.load(f)
            for t in tasks:
                self._append_item(
                    t.get("title", ""),
                    t.get("description", ""),
                    t.get("priority", "Средний"),
                )
        except Exception:
            # если файл побился - просто начинаем с пустого списка
            QMessageBox.warning(self, "Ошибка",
                                "Не удалось прочитать файл задач.")

    def save_to_file(self):
        tasks = []
        for i in range(self.task_list.count()):
            it = self.task_list.item(i)
            d = it.data(Qt.ItemDataRole.UserRole)
            tasks.append({
                "title": d["title"],
                "description": d["description"],
                "priority": d["priority"],
            })
        try:
            with open(TASKS_FILE, "w", encoding="utf-8") as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    # ---------- работа со списком ----------

    def _append_item(self, title, description, priority):
        text = "[" + priority + "] " + title
        if description:
            text += " — " + description

        item = QListWidgetItem(text)
        item.setToolTip(description or "Без описания")
        item.setData(Qt.ItemDataRole.UserRole, {
            "title": title,
            "description": description,
            "priority": priority,
        })
        self.task_list.addItem(item)

    def add_task(self):
        title = self.title_input.text().strip()
        description = self.desc_input.toPlainText().strip()
        priority = self.priority_combo.currentText()

        if not title:
            QMessageBox.warning(self, "Внимание",
                                "Введите название задачи!")
            self.title_input.setFocus()
            return

        self._append_item(title, description, priority)

        # очищаем поля после добавления
        self.title_input.clear()
        self.desc_input.clear()
        self.priority_combo.setCurrentIndex(1)
        self.title_input.setFocus()

        self.save_to_file()
        self.refresh_status()
        self.statusBar().showMessage("Добавлено: " + title, 3000)

    def delete_task(self):
        item = self.task_list.currentItem()
        if item is None:
            QMessageBox.information(self, "Внимание",
                                    "Выберите задачу в списке.")
            return

        title = item.data(Qt.ItemDataRole.UserRole)["title"]
        answer = QMessageBox.question(
            self, "Удаление",
            "Удалить задачу «" + title + "»?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            self.statusBar().showMessage("Отменено", 3000)
            return

        self.task_list.takeItem(self.task_list.row(item))
        self.save_to_file()
        self.refresh_status()
        self.statusBar().showMessage("Удалено: " + title, 3000)

    def clear_tasks(self):
        if self.task_list.count() == 0:
            QMessageBox.information(self, "Список пуст",
                                    "Очищать нечего.")
            return

        answer = QMessageBox.question(
            self, "Очистка",
            "Удалить все задачи (" + str(self.task_list.count()) + ")?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.task_list.clear()
            self.save_to_file()
            self.refresh_status()
            self.statusBar().showMessage("Список очищен", 3000)
        else:
            self.statusBar().showMessage("Отменено", 3000)

    def open_about(self):
        AboutWindow(self).exec()

    # ---------- прочее ----------

    def on_title_changed(self, text):
        self.symbols_label.setText(
            "Название: " + str(len(text)) + " символов"
        )

    def refresh_status(self):
        self.status_label.setText("Задач: " + str(self.task_list.count()))


def main():
    app = QApplication(sys.argv)
    w = TaskManagerWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()