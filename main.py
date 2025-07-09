import sys
import os
import shutil
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QFileDialog, QVBoxLayout
)

class FileManager(QWidget):
    def __init__(self):
        super().__init__()
        self.file_history = {}

        self.setWindowTitle("Smart File Manager")
        self.setGeometry(100, 100, 600, 200)
        self.setStyleSheet("""
        QWidget {
            background-color: #1e1e1e;
            color: #e6e6e6;
            font-family: 'Segoe UI', sans-serif;
        }

        QPushButton {
            background-color: #8e44ad;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 8px;
        }

        QPushButton:hover {
            background-color: #732d91;
        }

        QLineEdit {
            background-color: #2c2c2c;
            border: 1px solid #444;
            color: #e6e6e6;
            padding: 5px;
            border-radius: 4px;
        }

        QLabel {
            font-size: 16px;
            font-weight: bold;
        }
        """)

        layout = QVBoxLayout()

        self.label = QLabel("Choose a folder to organize:")
        layout.addWidget(self.label)

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("No folder selected yet...")
        layout.addWidget(self.path_input)

        self.browse_button = QPushButton("📂 Browse Folder")
        self.browse_button.clicked.connect(self.select_folder)
        layout.addWidget(self.browse_button)

        self.organize_button = QPushButton("🧹 Organize Files")
        self.organize_button.clicked.connect(self.organize_files)
        layout.addWidget(self.organize_button)

        self.undo_button = QPushButton("↩️ Undo Last Organize")
        self.undo_button.clicked.connect(self.undo_last_action)
        layout.addWidget(self.undo_button)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.path_input.setText(folder_path)

    def organize_files(self):
        folder_path = self.path_input.text()

        if not folder_path or not os.path.exists(folder_path):
            self.status_label.setText("❌ Please select a valid folder.")
            return

        self.status_label.setText("🔄 Organizing files... Please wait.")
        QApplication.processEvents()

        file_types = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif'],
            'Videos': ['.mp4', '.mov', '.avi', '.mkv'],
            'Documents': ['.pdf', '.docx', '.txt', '.xlsx'],
            'Music': ['.mp3', '.wav'],
            'Archives': ['.zip', '.rar', '.7z'],
        }

        moved = 0
        self.file_history = {}

        for dirpath, _, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                ext = os.path.splitext(filename)[1].lower()
                found = False

                for folder_name, extensions in file_types.items():
                    if ext in extensions:
                        dest_folder = os.path.join(dirpath, folder_name)
                        os.makedirs(dest_folder, exist_ok=True)
                        new_path = os.path.join(dest_folder, filename)
                        shutil.move(file_path, new_path)
                        self.file_history[file_path] = new_path
                        moved += 1
                        found = True
                        break

                if not found:
                    other_folder = os.path.join(dirpath, "Others")
                    os.makedirs(other_folder, exist_ok=True)
                    new_path = os.path.join(other_folder, filename)
                    shutil.move(file_path, new_path)
                    self.file_history[file_path] = new_path
                    moved += 1

        with open("undo_history.json", "w") as f:
            json.dump(self.file_history, f)

        self.status_label.setText(f"✅ Organized {moved} files successfully!")

    def undo_last_action(self):
        try:
            with open("undo_history.json", "r") as f:
                history = json.load(f)
        except FileNotFoundError:
            self.status_label.setText("⚠️ No undo history found.")
            return

        undone = 0
        errors = 0

        for original_path, moved_path in history.items():
            try:
                os.makedirs(os.path.dirname(original_path), exist_ok=True)
                if os.path.exists(moved_path):
                    shutil.move(moved_path, original_path)
                    undone += 1
                else:
                    print(f"⚠️ File not found for undo: {moved_path}")
                    errors += 1
            except Exception as e:
                print(f"❌ Error moving {moved_path} -> {original_path}: {e}")
                errors += 1

        # Clean up only empty folders created during organization
        folder_path = self.path_input.text()
        folder_types = ['Images', 'Videos', 'Documents', 'Music', 'Archives', 'Others']

        for dirpath, dirnames, _ in os.walk(folder_path):
            for folder in folder_types:
                full_path = os.path.join(dirpath, folder)
                if os.path.isdir(full_path) and not os.listdir(full_path):
                    try:
                        os.rmdir(full_path)
                        print(f"🗑️ Deleted empty folder: {full_path}")
                    except Exception as e:
                        print(f"❌ Couldn't delete {full_path}: {e}")

        if undone > 0:
            self.status_label.setText(f"🔙 Undone: {undone} files restored. ✅")
        elif errors > 0:
            self.status_label.setText(f"⚠️ Undo failed for some files.")
        else:
            self.status_label.setText("⚠️ No files were restored.")

        # Delete history file
        if os.path.exists("undo_history.json"):
            os.remove("undo_history.json")

# Main app start
app = QApplication(sys.argv)
window = FileManager()
window.show()
sys.exit(app.exec_())
