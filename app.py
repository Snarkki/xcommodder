import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QVBoxLayout, QWidget, QPushButton, QTextEdit, QTreeView, QMessageBox, QHBoxLayout, QSplitter
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from parser import XCOM2Parser

class ConfigGenerator:
    def generate_config(self, data):
        # Implement config file generation logic here
        pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XCOM2 Config Editor")
        self.setGeometry(100, 100, 1200, 800)

        main_layout = QHBoxLayout()

        # Left side: Folder structure and file list
        left_layout = QVBoxLayout()
        self.load_button = QPushButton("Select Folder")
        self.load_button.clicked.connect(self.select_folder)
        left_layout.addWidget(self.load_button)

        self.tree_view = QTreeView()
        left_layout.addWidget(self.tree_view)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        # Right side: Content display
        self.content_edit = QTextEdit()
        self.content_edit.setReadOnly(True)

        # Add splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(self.content_edit)
        splitter.setSizes([300, 900])  # Adjust initial sizes as needed

        main_layout.addWidget(splitter)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.parser = XCOM2Parser()
        self.config_generator = ConfigGenerator()
        self.parsed_data = None
        self.current_folder = None

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.current_folder = folder
            self.parse_folder(folder)

    def parse_folder(self, folder):
        self.parsed_data = self.parser.parse_folder(folder)
        self.update_tree_view()

    def update_tree_view(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Files'])
        
        ini_root = QStandardItem('INI Files')
        int_root = QStandardItem('INT Files')
        
        if self.parsed_data and "ini_files" in self.parsed_data:
            for file, data in self.parsed_data['ini_files'].items():
                ini_root.appendRow(QStandardItem(file))

        if self.parsed_data and "int_files" in self.parsed_data:  
            for file, data in self.parsed_data['int_files'].items():
                if file == None or data == None:
                    continue
                int_item = QStandardItem(file)
                for ability in data:
                    ability_item = QStandardItem(ability['Name'])
                    int_item.appendRow(ability_item)
                int_root.appendRow(int_item)
            
        model.appendRow(ini_root)
        model.appendRow(int_root)
        
        self.tree_view.setModel(model)
        self.tree_view.expandAll()
        self.tree_view.clicked.connect(self.on_tree_item_clicked)

    def on_tree_item_clicked(self, index):
        item = self.tree_view.model().itemFromIndex(index)
        if item.parent() is not None:  # This is a file or ability, not a category
            if item.parent().text() == 'INT Files':
                file_name = item.text()
                self.display_int_content(file_name)
            elif item.parent().parent() is not None and item.parent().parent().text() == 'INT Files':
                file_name = item.parent().text()
                ability_name = item.text()
                self.display_ability_content(file_name, ability_name)

    def display_int_content(self, file_name):
        content = self.parsed_data['int_files'][file_name]
        self.content_edit.clear()
        for ability in content:
            self.content_edit.append(f"[{ability['Name']} {ability['Type']}]")
            self.content_edit.append(f"LocFriendlyName={ability['LocFriendlyName']}")
            self.content_edit.append(f"LocLongDescription={ability['LocLongDescription']}")
            self.content_edit.append("\n")

    def display_ability_content(self, file_name, ability_name):
        content = self.parsed_data['int_files'][file_name]
        for ability in content:
            if ability['Name'] == ability_name:
                self.content_edit.clear()
                self.content_edit.append(f"[{ability['Name']} {ability['Type']}]")
                self.content_edit.append(f"LocFriendlyName={ability['LocFriendlyName']}")
                self.content_edit.append(f"LocLongDescription={ability['LocLongDescription']}")
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())