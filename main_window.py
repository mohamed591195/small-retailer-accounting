from PyQt5.QtWidgets import (
    QMainWindow, 
    QApplication, 
    QAction, 
    QVBoxLayout, 
    QHBoxLayout,
    QTabWidget, 
    QWidget, 
    QListWidget,
    QMessageBox,
    QLineEdit,
    QLabel,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)

from models import (
    get_db_session,
    Classification,
    Product,
    SoldProduct
)

from forms import ClassficationForm, AddProductForm, CheckoutForm

from PyQt5 import QtCore
from PyQt5 import QtGui

from tables import SoldProductsTable, StoredProductsTable


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.setLocale(QtCore.QLocale(QtCore.QLocale.Arabic, QtCore.QLocale.Egypt))

        self.session = get_db_session()

        self.setUpGUI()

    def viewProduct(self):
        sku_code = self.code_entry.text()

        product = self.session.query(Product).filter(Product.sku_code==sku_code).first()

        if not product:

            QMessageBox.warning(
                self, 
                'خطأ فى الكود',
                '''لم يتم العثور على منتج مرتبط بهذا الكود
                          ،تأكد من صحة الكود وحاول مرة اخرى
                '''
            )
            return

        check_out_dialog = CheckoutForm(self.session, product)
        check_out_dialog.exec_()

    def displayClassificationForm(self):
        dialog = ClassficationForm(self.session)
        dialog.exec_()

    def dispalyProductForm(self):

        classifications = self.session.query(Classification).all()
        
        if not classifications:
            
            QMessageBox.warning(
                self, 
                'تحذير',
                'يرجي اضافة اصناف اولا ثم يمكنك اضافة منتجات'
            )

        else:
            dialog = AddProductForm(self.session, classifications)
            dialog.exec_()

    def displayExportsTable(self):
        
        sold_products = self.session.query(SoldProduct).all()

        if not sold_products:
            QMessageBox.warning(
                self, 
                'تحذير',
                'لم يتم بيع منتجات حتى الآن'
            )

        else:
            table_dialog = SoldProductsTable(self.session)
            table_dialog.exec_()

    def displayWhatInStore(self):

        products = self.session.query(Product).count()
        if not products:
            QMessageBox.warning(
                self, 
                'تحذير',
                'لا يوجد منتجات لعرضها، عند اضافة منتجات ستراها هنا!'
            )
            return
        table_dialog = StoredProductsTable(self.session)
        table_dialog.exec_()
        
    def setUpGUI(self):

        self.setWindowTitle('Adidas!')
        # ##### menu bar ###########
    
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet(
            '''
            QMenuBar {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                            stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
            }

            QMenuBar::item {
                padding: 0 40px;
            }

            QMenuBar::item::selected, QMenuBar::item::hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #fafafa, stop: 0.4 #f4f4f4,
                                stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
            }
            
            '''
        )

        new_menu = menu_bar.addMenu('جديد')
        show_menu = menu_bar.addMenu('عرض')

        newClassificationAction = QAction('صنف جديد', self)
        newClassificationAction.triggered.connect(self.displayClassificationForm)

        newProductAction = QAction('منتج جديد', self)
        newProductAction.triggered.connect(self.dispalyProductForm)

        new_menu.addAction(newProductAction)
        new_menu.addAction(newClassificationAction)

        showStoredProducts = QAction('عرض المخزن', self)
        showStoredProducts.triggered.connect(self.displayWhatInStore)
        
        showExportsAction = QAction('عرض الصادر', self)
        showExportsAction.triggered.connect(self.displayExportsTable)

        show_menu.addAction(showExportsAction)
        show_menu.addAction(showStoredProducts)

        # ##### end menu bar ###########

        # ##### tab containter ###########
        
        self.layout = QVBoxLayout()

        self.setStyleSheet('''
            QPushButton::selected, QPushButton::hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #fafafa, stop: 0.4 #f4f4f4,
                                stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
                }
            QPushButton {
                margin: 20px 20px;
                border: 2px solid #8f8f91;
                border-radius: 6px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
                }
            QPushButton {
                padding: 0 20
            }
            
            QLineEdit::focus, QLineEdit::hover {
                background: none;
                }
            QLineEdit {
                margin: 20px 20px;
                border: 2px solid #8f8f91;
                border-radius: 6px;
                background: #E5E7E9;
                }

        ''')

        # self.tabs_indexs = {}
        
        # for i, c in enumerate(self.classifications):
        #     self.tab_widget.addTab(TabClass(classification=c), c.name)
        #     self.tabs_indexs[c.name] = i
       

        vertical_layout = QVBoxLayout()
        
        vertical_layout.setAlignment(QtCore.Qt.AlignHCenter)
        vertical_layout.setAlignment(QtCore.Qt.AlignVCenter)
        
        courier_font = QtGui.QFont('Courier New', 20)

        self.label = QLabel('ضع كود المنتج')
        self.label.setStyleSheet('margin-top: 60px;')
        self.label.setFont(courier_font)
        self.label.setAlignment(QtCore.Qt.AlignHCenter)
  

        self.code_entry = QLineEdit()
        self.code_entry.setStyleSheet('margin: 30 500; padding: 5;')
        self.code_entry.setFont(courier_font)
        self.code_entry.setAlignment(QtCore.Qt.AlignCenter)

        self.code_entry.returnPressed.connect(self.viewProduct)      

        self.find_button = QPushButton('أظهر المنتج')
        self.find_button.setStyleSheet('margin: 20 800')

        self.find_button.clicked.connect(self.viewProduct)
        
        vertical_layout.addWidget(self.label)
        vertical_layout.addWidget(self.code_entry)
        vertical_layout.addWidget(self.find_button)

        self.layout.addLayout(vertical_layout)

        verticalSpacer = QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Expanding) 
        self.layout.addItem(verticalSpacer)

        layout_widget = QWidget()
        layout_widget.setLayout(self.layout)

        self.setCentralWidget(layout_widget)


if __name__ == "__main__":

    font = QtGui.QFont('cairo', 12)
    app = QApplication([])
    
    app.setFont(font)

    window = MainWindow()
    
    window.showMaximized()
    
    app.exec_()
