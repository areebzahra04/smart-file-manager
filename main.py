import sys
import os
import shutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QFileDialog, QVBoxLayout
)

class FileManager(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Smart File Manager")
        self.setGeometry(100, 100, 600, 200)

        # Layout
        layout = QVBoxLayout()

        # Label
        self.label = QLabel("Choose a folder to organize:")
        layout.addWidget(self.label)

        # Text box to show selected folder
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("No folder selected yet...")
        layout.addWidget(self.path_input)

        # Browse Button
        self.browse_button = QPushButton("📂 Browse Folder")
        self.browse_button.clicked.connect(self.select_folder)
        layout.addWidget(self.browse_button)

        # Organize Button
        self.organize_button = QPushButton("🧹 Organize Files")
        self.organize_button.clicked.connect(self.organize_files)
        layout.addWidget(self.organize_button)

        self.setLayout(layout)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            print("Selected folder:", folder_path)
            self.path_input.setText(folder_path)

    def organize_files(self):
        folder_path = self.path_input.text()

        if not folder_path or not os.path.exists(folder_path):
            self.label.setText("❌ Please select a valid folder.")
            return

        # File type categories
        file_types = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif'],
            'Videos': ['.mp4', '.mov', '.avi', '.mkv'],
            'Documents': ['.pdf', '.docx', '.txt', '.xlsx'],
            'Music': ['.mp3', '.wav'],
            'Archives': ['.zip', '.rar', '.7z'],
        }

        moved = 0

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            if os.path.isfile(file_path):
                ext = os.path.splitext(filename)[1].lower()
                found = False
                print(f"Checking file: {filename} — Extension: {ext}")

                for folder_name, extensions in file_types.items():
                    if ext in extensions:
                        dest_folder = os.path.join(folder_path, folder_name)
                        os.makedirs(dest_folder, exist_ok=True)
                        shutil.move(file_path, os.path.join(dest_folder, filename))
                        moved += 1
                        found = True
                        break

                if not found:
                    other_folder = os.path.join(folder_path, "Others")
                    os.makedirs(other_folder, exist_ok=True)
                    shutil.move(file_path, os.path.join(other_folder, filename))
                    moved += 1

        print("✅ Done organizing.")
        self.label.setText(f"✅ Organized {moved} files successfully!")

# Main app start
app = QApplication(sys.argv)
window = FileManager()
window.show()
sys.exit(app.exec_())
