import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QRadioButton, QLineEdit,
                             QLabel, QMessageBox, QFileDialog, QCheckBox)
from PyQt5.QtCore import Qt

class FileRenamer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setWindowTitle("批量文件重命名工具")
        self.setGeometry(300, 300, 600, 400)

    def init_ui(self):
        layout = QVBoxLayout()

        # 文件选择按钮
        hbox_btns = QHBoxLayout()
        self.btn_folder = QPushButton("选择文件夹", self)
        self.btn_files = QPushButton("选择文件", self)
        hbox_btns.addWidget(self.btn_folder)
        hbox_btns.addWidget(self.btn_files)
        layout.addLayout(hbox_btns)

        # 文件列表
        self.file_list = QListWidget(self)
        layout.addWidget(self.file_list)

        # 命名选项
        self.radio_keep = QRadioButton("保留原文件名", self)
        self.radio_increment = QRadioButton("递增命名", self)
        self.radio_keep.setChecked(True)
        
        # 起始数字输入框
        self.start_num_layout = QHBoxLayout()
        self.lbl_start_num = QLabel("起始数字:", self)
        self.edit_start_num = QLineEdit("1", self)
        self.start_num_layout.addWidget(self.lbl_start_num)
        self.start_num_layout.addWidget(self.edit_start_num)
        self.lbl_start_num.hide()
        self.edit_start_num.hide()

        # 后缀选项
        self.chk_suffix = QCheckBox("启用后缀修改", self)
        self.chk_suffix.setChecked(False)
        self.chk_suffix.toggled.connect(self.toggle_suffix_input)
        hbox_suffix = QHBoxLayout()
        self.lbl_suffix = QLabel("新后缀名:", self)
        self.edit_suffix = QLineEdit(self)
        self.edit_suffix.setEnabled(False)  # 默认禁用后缀输入框
        hbox_suffix.addWidget(self.lbl_suffix)
        hbox_suffix.addWidget(self.edit_suffix)

        # 执行按钮
        self.btn_execute = QPushButton("执行重命名", self)

        # 布局组织
        layout.addWidget(self.radio_keep)
        layout.addWidget(self.radio_increment)
        layout.addLayout(self.start_num_layout)
        layout.addWidget(self.chk_suffix) 
        layout.addLayout(hbox_suffix)
        layout.addWidget(self.btn_execute)

        # 信号连接
        self.btn_folder.clicked.connect(self.select_folder)
        self.btn_files.clicked.connect(self.select_files)
        self.radio_increment.toggled.connect(self.toggle_number_input)
        self.btn_execute.clicked.connect(self.process_files)

        self.setLayout(layout)

    def toggle_suffix_input(self, checked):
        self.edit_suffix.setEnabled(checked)

    def toggle_number_input(self, checked):
        self.lbl_start_num.setVisible(checked)
        self.edit_start_num.setVisible(checked)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.file_list.clear()
            for f in os.listdir(folder):
                path = os.path.join(folder, f)
                if os.path.isfile(path):
                    self.file_list.addItem(path)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择文件")
        if files:
            self.file_list.clear()
            for f in files:
                self.file_list.addItem(f)

    def process_files(self):
        # 获取文件列表
        file_paths = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        if not file_paths:
            QMessageBox.warning(self, "警告", "请先选择文件或文件夹！")
            return

        # 处理后缀
        new_ext = ""
        if self.chk_suffix.isChecked():
            new_ext = self.edit_suffix.text().strip()
            new_ext = f".{new_ext}" if new_ext and not new_ext.startswith(".") else new_ext
        else:
            new_ext = None

        try:
            if new_ext == "" or new_ext == ".":
                reply = QMessageBox.question(self, "警告", "文件后缀为空，是否继续？", 
                                 QMessageBox.Cancel | QMessageBox.Ok, QMessageBox.Cancel)
                if reply == QMessageBox.Ok:
                    new_ext = ""
                else :
                    return
                
            if self.radio_keep.isChecked():
                self.rename_keep(file_paths, new_ext)
            else:
                start_num = int(self.edit_start_num.text())
                self.rename_increment(file_paths, new_ext, start_num)
            QMessageBox.information(self, "完成", "文件重命名成功！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"操作失败：{str(e)}")

    def rename_keep(self, files, new_ext):
        for file_path in files:
            dir_name = os.path.dirname(file_path)
            base_name = os.path.basename(file_path)
            
            # 分割文件名为主干和原扩展名
            if '.' in base_name:
                name_part, original_ext_part = base_name.split('.', 1)
                original_ext = '.' + original_ext_part
            else:
                name_part = base_name
                original_ext = ''

            # 处理新后缀
            if new_ext is not None:
                # 用户启用了后缀修改
                if new_ext:
                    final_ext = '.' + new_ext.lstrip('.')
                else:
                    final_ext = ''
            else:
                # 未启用后缀修改，保留原扩展名
                final_ext = original_ext

            new_name = f"{name_part}{final_ext}"
            new_path = os.path.join(dir_name, new_name)
            
            # 直接覆盖已存在的文件，使用os.replace
            if os.path.abspath(file_path) != os.path.abspath(new_path):
                os.replace(file_path, new_path)
            
            self.update_list_item(file_path, new_path)

    def rename_increment(self, files, new_ext, start_num):
        for idx, file_path in enumerate(files):
            dir_name = os.path.dirname(file_path)
            base_name = os.path.basename(file_path)
            
            # 获取文件的原始扩展名
            name_parts = base_name.split('.', 1)
            if len(name_parts) > 1:
                _, old_ext = name_parts
            else:
                old_ext = ""  # 如果没有扩展名，默认为空字符串
            
            # 如果没有启用后缀修改，则使用原扩展名
            if new_ext:
                new_name = f"{start_num + idx}{new_ext}"
            else:
                new_name = f"{start_num + idx}.{old_ext}"

            new_path = os.path.join(dir_name, new_name)
            
            # 处理文件名冲突
            counter = 1
            while os.path.exists(new_path):
                if new_ext:
                    new_name = f"{start_num + idx}_{counter}{new_ext}"
                else:
                    new_name = f"{start_num + idx}_{counter}.{old_ext}"
                new_path = os.path.join(dir_name, new_name)
                counter += 1
            
            os.rename(file_path, new_path)
            self.update_list_item(file_path, new_path)

    def update_list_item(self, old_path, new_path):
        items = self.file_list.findItems(old_path, Qt.MatchExactly)
        if items:
            items[0].setText(new_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileRenamer()
    window.show()
    sys.exit(app.exec_())