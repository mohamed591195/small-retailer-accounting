from PyQt5.QtWidgets import (
    QListWidget, 
    QListView, 
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout,
    QListWidgetItem, 
    QDialog,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMainWindow,
    QLabel,
    QMessageBox
)

from PyQt5 import QtWidgets

from PyQt5 import QtCore, QtGui
import os 
from models import (
    Product, 
    SoldProduct, 
    ProductSize, 
    ProductColor, 
    ColorSize,
    Classification
)
from sqlalchemy import desc
import forms
from utils import get_confirmation_message, get_color_sizes_preview


class ImageWidget(QWidget):

    def __init__(self, imagePath, parent):
        super(ImageWidget, self).__init__(parent)
        self.picture = QtGui.QPixmap(imagePath).scaled(
                230, 
                230, 
                QtCore.Qt.KeepAspectRatio
            )

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.picture)

class SoldActionWidget(QWidget):
    def __init__(self, parent, table, row_index, session, sold_unit):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        
        self.session = session
        self.row_index = row_index
        self.sold_unit = sold_unit
        self.table = table
        self.parent = parent

        restore_btn = QPushButton('استرجاع')
        restore_btn.clicked.connect(self.restore_product)

        restore_btn.setStyleSheet('''
            QPushButton:hover {
                background: #F1948A;
                color: white;
            }
            QPushButton {
                background: none;
                border: 2px solid #F1948A;
                border-radius: 6px; 
            }
        ''')

        edit_btn = QPushButton('تعديل')
        edit_btn.clicked.connect(self.edit_sold_unit)

        edit_btn.setStyleSheet('''
        QPushButton:hover {
                background: #AED6F1;
                color: white;
            }
            QPushButton {
                background: none;
                border: 2px solid #AED6F1;
                border-radius: 6px; 
            }
        ''')
        self.layout.addWidget(edit_btn)
        self.layout.addWidget(restore_btn)

        self.setLayout(self.layout)

    def edit_sold_unit(self):
        check_out_dialog = forms.CheckoutForm(self.session, self.sold_unit.product, self.sold_unit)
        check_out_dialog.exec_()

        self.table.removeRow(self.row_index)
        self.parent.add_row(self.row_index, check_out_dialog.sold_product)
        
    def restore_product(self):

        confirmation_message = get_confirmation_message(
            'تأكيد عملية الاسترجاع',
            'يرجي التحقق من المنتج وتأكيد عملية الاسترجاع!' 
        )
        confirmation_message.exec_()

        if confirmation_message.clickedButton().text() == 'الغاء':
            return

        product = self.sold_unit.product

        size = self.session.query(ProductSize).filter_by(size=self.sold_unit.size).one()
        color_obj = self.session.query(ProductColor).filter_by(name=self.sold_unit.color, product=product).one()
        
        color_size_obj = self.session.query(ColorSize).filter_by(size=size, color=color_obj).first()
        
        if color_size_obj:
            color_size_obj.repeating_counter += 1

        else:
            ncolor_size = ColorSize(color=color_obj, size=size, repeating_counter=1)
            self.session.add(ncolor_size)

        product.pairs_number += 1

        self.session.delete(self.sold_unit)
        self.session.commit()
        self.table.removeRow(self.row_index)

class SoldProductsTable(QDialog):
    def __init__(self, session):
        super().__init__()
        
        self.session = session

        self.table = QTableWidget()

        self.table.setColumnCount(8)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.table.setHorizontalHeaderLabels((
            'الصورة',
            'الكود',
            'اللون',
            'المقاس',
            'سعر جملة',
            'سعر البيع',
            'تاريخ البيع',
            'أكشن'
        ))
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(150)
        self.table.setAlternatingRowColors(True)
        self.table.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.table.setStyleSheet(
            '''
            QTableView {
                selection-background-color: #D5F5E3;
                selection-color: black;
                alternate-background-color: #F2F3F4;
            }
            '''
        )

        self.rows_count = 0

        for item in self.session.query(SoldProduct).order_by(desc(SoldProduct.sold_at)):
            self.add_row(self.rows_count, item)
            self.rows_count += 1
            
        self.layout.addWidget(self.table)

        self.showMaximized()

    def add_row(self, row_index, item):
        # image = QTableWidgetItem(item.product.image.split('\\')[-1])
        sku_code = QTableWidgetItem(item.product.sku_code)
        sku_code.setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignCenter)

        color = QTableWidgetItem(item.color)
        color.setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignCenter)

        size = QTableWidgetItem(str(item.size))
        size.setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignCenter)

        original_price = QTableWidgetItem(f" {item.product.original_price}  جــ ")
        original_price.setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignCenter)

        selling_price = QTableWidgetItem(f" {item.sold_by_price}  جــ ")
        selling_price.setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignCenter)

        selling_date = QTableWidgetItem(item.sold_at.strftime("%p %I:%M \n %d/%m/%Y"))
        selling_date.setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignCenter)

        self.table.insertRow(row_index)
        
        self.table.setCellWidget(
            row_index, 
            0, 
            ImageWidget(item.product.image, self)
        )
        # self.table.setItem(self.rows_count, 0, image)
        self.table.setItem(row_index, 1, sku_code)
        self.table.setItem(row_index, 2, color)
        self.table.setItem(row_index, 3, size)
        self.table.setItem(row_index, 4, original_price)
        self.table.setItem(row_index, 5, selling_price)
        self.table.setItem(row_index, 6, selling_date)
        self.table.setCellWidget(
            row_index, 
            7, 
            SoldActionWidget(self, self.table, row_index, self.session, item)
        )

class StoredActionWidget(QWidget):
    def __init__(self, parent, table, row_index, session, product):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        
        self.session = session
        self.row_index = row_index
        self.product = product
        self.table = table
        self.parent = parent

        delete_btn = QPushButton('خذف')
        delete_btn.clicked.connect(self.delete_stored_unit)

        delete_btn.setStyleSheet('''
            QPushButton:hover {
                background: #F1948A;
                color: white;
            }
            QPushButton {
                background: none;
                border: 2px solid #F1948A;
                border-radius: 6px; 
            }
        ''')

        edit_btn = QPushButton('تعديل')
        edit_btn.clicked.connect(self.edit_stored_unit)

        edit_btn.setStyleSheet('''
        QPushButton:hover {
                background: #AED6F1;
                color: white;
            }
            QPushButton {
                background: none;
                border: 2px solid #AED6F1;
                border-radius: 6px; 
            }
        ''')

        self.layout.addWidget(edit_btn)
        self.layout.addWidget(delete_btn)

        self.setLayout(self.layout)

    def edit_stored_unit(self):
        classifications = self.session.query(Classification).all()
        add_product_form = forms.AddProductForm(self.session, classifications, self.product)
        add_product_form.exec_()

        self.table.removeRow(self.row_index)
        self.parent.add_row(self.row_index, add_product_form.product)

    def delete_stored_unit(self):

        if self.product.sold_units:
            message = 'هذا المنتج تمت عليه عمليات بيع لذلك سيتم تصفير الالوان بالمقاسات المتاحة ولن يتم حذفه نهائيا'

        else:
            message = 'يرجى العلم ان هذا المنتج  لم يتم عليه اى عملية بيع، \n لذلك سيتم حذفه نهائيا ولا يمكن الرجوع عن ذلك'

        confirmation_message = get_confirmation_message(
            'تأكيد عملية الحذف ',
            message
        )
        confirmation_message.exec_()

        if confirmation_message.clickedButton().text() == 'الغاء':
            return

        if not self.product.sold_units:
            self.session.delete(self.product)
            self.session.commit()
            self.table.removeRow(self.row_index)
            return

        
        for color in self.product.colors:
            self.session.delete(color)

        self.product.pairs_number = 0

        self.session.commit()
        self.table.removeRow(self.row_index)
        self.parent.add_row(self.row_index, self.product)


class StoredProductsTable(QDialog):
    def __init__(self, session):
        super().__init__()

        self.session = session

        self.table = QTableWidget()

        self.table.setColumnCount(9)
        self.table.setFont(QtGui.QFont('courier new', 15))
        self.table.horizontalHeader().setFont(QtGui.QFont('courier new', 15))
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.table.setHorizontalHeaderLabels((
            'الصورة',
            'الكود',
            'عدد الازواج',
            'الالوان بالمقاسات',
            'سعر جملة',
            'اقل سعر بيع',
            'المبيعات',
            'تاريخ الاضافة',
            'أكشن'
        ))
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)

        self.table.verticalHeader().setDefaultSectionSize(150)
        self.table.setAlternatingRowColors(True)
        self.table.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.table.setStyleSheet(
            '''
            QTableView {
                selection-background-color: #D5F5E3;
                selection-color: black;
                alternate-background-color: #F2F3F4;
            }
            '''
        )

        self.rows_count = 0

        for item in self.session.query(Product).order_by(desc(Product.created_at)):
            self.add_row(self.rows_count, item)
            self.rows_count += 1
            
        self.layout.addWidget(self.table)

        self.showMaximized()

    def add_row(self, row_index, item):
        # image = QTableWidgetItem(item.product.image.split('\\')[-1])
        sku_code = QTableWidgetItem(item.sku_code)
        sku_code.setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignCenter)

        pairs_number = QTableWidgetItem(f'{item.pairs_number} أزواج')
        pairs_number.setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignCenter)

        color_sizes_preview = get_color_sizes_preview(item)
        stored_colors_sizes = QTableWidgetItem(color_sizes_preview)
        stored_colors_sizes.setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignCenter)

        original_price = QTableWidgetItem(f" {item.original_price}  جــ ")
        original_price.setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignCenter)

        suggested_price = QTableWidgetItem(f" {item.suggested_price}  جــ ")
        suggested_price.setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignCenter)

        sold_colors_sizes = {}

        t = ''

        for unit in item.sold_units:
            if not unit.color in sold_colors_sizes:
                sold_colors_sizes[unit.color] = [unit.size]
            else:
                sold_colors_sizes[unit.color] += [unit.size]

        for i, (color, sizes) in enumerate(sold_colors_sizes.items()):
            if i:
                t += '\n'
            t += f'{color}: {sizes}'
        
        sold_colors_sizes = QTableWidgetItem(t)
        sold_colors_sizes.setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignCenter)

        creation_date = QTableWidgetItem(item.created_at.strftime("%p %I:%M \n %d/%m/%Y"))
        creation_date.setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignCenter)

        self.table.insertRow(row_index)
        
        self.table.setCellWidget(
            row_index, 
            0, 
            ImageWidget(item.image, self)
        )
        # self.table.setItem(self.rows_count, 0, image)
        self.table.setItem(row_index, 1, sku_code)
        self.table.setItem(row_index, 2, pairs_number)
        self.table.setItem(row_index, 3, stored_colors_sizes)
        self.table.setItem(row_index, 4, original_price)
        self.table.setItem(row_index, 5, suggested_price)
        self.table.setItem(row_index, 6, sold_colors_sizes)
        self.table.setItem(row_index, 7, creation_date)
        self.table.setCellWidget(
            row_index, 
            8, 
            StoredActionWidget(self, self.table, row_index, self.session, item)
        )

        
        