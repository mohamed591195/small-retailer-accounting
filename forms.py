from PyQt5.QtWidgets import (
    QDialog, 
    QVBoxLayout, 
    QHBoxLayout, 
    QPushButton, 
    QLineEdit, 
    QLabel,
    QMessageBox,
    QFileDialog,
    QComboBox,
    QListWidget,
    QAbstractItemView,
    QFrame
)

from PyQt5 import QtCore, QtGui
from models import Classification, Product, ProductSize, ProductColor, ColorSize, SoldProduct, get_or_create
from utils import get_confirmation_message, get_color_sizes_preview
from pathlib import Path
from PIL import Image

current_path = Path.cwd()

class ClassficationForm(QDialog):

    def __init__(self, session):
        super().__init__()

        self.session = session
        
        self.setLayoutDirection(QtCore.Qt.RightToLeft)

        vertical_layout = QVBoxLayout()

        self.setLayout(vertical_layout)
        
        self.classificationNameInput = QLineEdit()
        self.classificationNameInput.setAlignment(QtCore.Qt.AlignCenter)

        vertical_layout.addWidget(QLabel('اسم التصنيف'))
        vertical_layout.addWidget(self.classificationNameInput)
    
        self.add_button = QPushButton('اضافة')

        self.add_button.setStyleSheet('''
            QPushButton::selected, QPushButton::hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #fafafa, stop: 0.4 #f4f4f4,
                                stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
                }
            QPushButton {
                border: 2px solid #8f8f91;
                border-radius: 6px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
                }

        ''')

        self.add_button.clicked.connect(self.add_classification)

        vertical_layout.addWidget(self.add_button)   

        self.setGeometry(700, 350, 400, 150)

    def add_classification(self):
        
        text = self.classificationNameInput.text()

        same_classifications = self.session.query(Classification).filter_by(name=text).all()
        
        if len(same_classifications):
            self.close()
            QMessageBox.warning(
                self, 
                'تحذير',
                'التصنيف موجود بالفعل!'
            )
            return

        classification = Classification(name=text)

        self.session.add(classification)
        self.session.commit()

        QMessageBox.information(
            self,
            'عملية ناجحة',
            'تمت الاضافة بنجاح'
        )
        self.close()
  
    
class SizesMultiChoiceListDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setGeometry(500, 500, 520, 500)

        self.setStyleSheet('''
            QPushButton::selected, QPushButton::hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #fafafa, stop: 0.4 #f4f4f4,
                                stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
                }
            QPushButton {
                border: 2px solid #8f8f91;
                border-radius: 6px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
                }
            
            QListWidget::item {
                text-align:center;
                padding: 5 10px;
            }
        ''')

        vertical_layout = QVBoxLayout()

        self.setLayout(vertical_layout)

        self.colorInput = QLineEdit()
        self.colorInput.setAlignment(QtCore.Qt.AlignCenter)

        # adding reptead color sizes 
        hlayout = QHBoxLayout()

        self.size_repeating_btn = QPushButton('اضافة')
        self.size_repeating_btn.clicked.connect(self.add_size_repeater_unit)

        self.repeated_size_input = QLineEdit()
        self.repeated_size_input.setPlaceholderText('المقاس')
        self.repeated_size_input.setAlignment(QtCore.Qt.AlignHCenter)
        self.repeated_size_input.setValidator(QtGui.QIntValidator())
        
        self.repeated_size_counter = QLineEdit()
        self.repeated_size_counter.setPlaceholderText('العدد')
        self.repeated_size_counter.setAlignment(QtCore.Qt.AlignHCenter)
        self.repeated_size_counter.setValidator(QtGui.QIntValidator())

        hlayout.addWidget(self.size_repeating_btn)
        hlayout.addWidget(self.repeated_size_input)

        hlayout.addWidget(self.repeated_size_counter)
        hlayout.setDirection(QHBoxLayout.RightToLeft)

        self.repeated_sizes_preview = QLineEdit()
        self.repeated_sizes_preview.setEnabled(False)

        self.repeated_sizes = {}
        # end
        

        vertical_layout.addWidget(QLabel('اللون'))
        vertical_layout.addWidget(self.colorInput)

        vertical_layout.addLayout(hlayout)
        vertical_layout.addWidget(self.repeated_sizes_preview)

        self.sizes_list = QListWidget()

        self.sizes_list.setLayoutDirection(QtCore.Qt.RightToLeft)

        for i in range(1, 60):
            self.sizes_list.addItem(str(i))

        self.sizes_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.sizes_list.setWrapping(True)
        self.sizes_list.setFlow(self.sizes_list.LeftToRight)
        self.sizes_list.setResizeMode(self.sizes_list.Adjust)
        self.selected_color_sizes = []

        self.done_button = QPushButton('تم')
        self.done_button.clicked.connect(self.doneBtnClicked)

        vertical_layout.addWidget(self.sizes_list)

        vertical_layout.addWidget(self.done_button)

    def add_size_repeater_unit(self):
        size = self.repeated_size_input.text()
        counter = self.repeated_size_counter.text()

        if size and counter and size not in self.repeated_sizes:

            self.repeated_sizes[size] = int(counter)

            repeated_sizes_preview = self.repeated_sizes_preview.text()
            repeated_sizes_preview += f' -- مقاس {size} تكرار {counter} مرة '

            self.repeated_sizes_preview.setText(repeated_sizes_preview)
        return
        
    def doneBtnClicked(self):
        
        sizes_counts_dic = {i.text(): 1 for i in self.sizes_list.selectedItems()}

        sizes_counts_dic.update(self.repeated_sizes)

        if not self.colorInput.text():
            QMessageBox.warning(
                self, 
                'لم يتم كتابة لون',
                f'يرجى ملىء حثل ادخال اللون اولا!'
            )
            return
        
        if not sizes_counts_dic:
            QMessageBox.warning(
                self, 
                'لم يتم اختيار مقاسات',
                f'يرجى اختيار مقاس واحد عالاقل لللون المكتوب قبل الاضافة'
            )
            return
        self.selected_color_sizes = (
            self.colorInput.text(),
            sizes_counts_dic
        )
        self.close()   
        
    
class AddProductForm(QDialog):

    def __init__(self, session, classifications, product=None):
        super().__init__()

        self.session = session

        self.product = product

        self.setStyleSheet('''
            QPushButton::selected, QPushButton::hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #fafafa, stop: 0.4 #f4f4f4,
                                stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
                }
            QPushButton {
                border: 2px solid #8f8f91;
                border-radius: 6px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
                }

        ''')

        upper_hlayout = QHBoxLayout()

        first_vertical_layout = QVBoxLayout()
        second_vertical_layout = QVBoxLayout()

        # second_vertical_layout.setDirection(QHBoxLayout.RightToLeft)
        
        first_frame = QFrame()
        first_frame.setStyleSheet('QFrame { margin: 10px; padding: 5px }')
        first_frame.setFrameStyle(2)
        first_frame.setLayout(first_vertical_layout)
        
        second_frame = QFrame()
        second_frame.setStyleSheet('QFrame { margin: 0px; background: #D5DBDB }')
        second_frame.setFrameStyle(2)
        second_frame.setLayout(second_vertical_layout)

        upper_hlayout.addWidget(first_frame, 50)
        upper_hlayout.addWidget(second_frame, 50)

        self.setLayoutDirection(QtCore.Qt.RightToLeft)

        self.setLayout(upper_hlayout)
        
        self.productSkucodeInput = QLineEdit()
        regex = QtCore.QRegExp('[a-zA-Z0-9_.+-]+')
        regex_validator = QtGui.QRegExpValidator(regex, self.productSkucodeInput)
        self.productSkucodeInput.setValidator(regex_validator)
        self.productSkucodeInput.setAlignment(QtCore.Qt.AlignCenter)

        self.originalPriceInput = QLineEdit()
        self.originalPriceInput.setValidator(QtGui.QIntValidator())
        self.originalPriceInput.setAlignment(QtCore.Qt.AlignCenter)

        self.suggestedPrice = QLineEdit()
        self.suggestedPrice.setValidator(QtGui.QIntValidator())
        self.suggestedPrice.setAlignment(QtCore.Qt.AlignCenter)

        self.classificationsCombo = QComboBox()
        # to be used for getting items index below 
        classifications_list = [c.name for c in classifications] 
        self.classificationsCombo.addItems(classifications_list)

        second_vertical_layout.addWidget(QLabel('النوع او الصنف'))
        second_vertical_layout.addWidget(self.classificationsCombo)
        
        h_layout = QHBoxLayout()

        self.imgBtn = QPushButton('اضف صورة') 
        self.imgBtn.setStyleSheet('padding: 0 5px;')
        self.imgBtn.clicked.connect(self.openFileDialog)
        h_layout.addWidget(self.imgBtn)

        self.imagePathPreview =  QLabel('')
        self.imagePath = ''
        
        h_layout.addWidget(self.imagePathPreview)
        
        first_vertical_layout.addLayout(h_layout)

        second_vertical_layout.addWidget(QLabel('الكود'))
        second_vertical_layout.addWidget(self.productSkucodeInput)

        second_vertical_layout.addWidget(QLabel('سعر الجملة'))
        second_vertical_layout.addWidget(self.originalPriceInput)

        second_vertical_layout.addWidget(QLabel('اقل سعر'))
        second_vertical_layout.addWidget(self.suggestedPrice)
        
        self.sizes_list_dialog_btn = QPushButton('اضف الالوان بالمقاسات المتاحة') 
        self.sizes_list_dialog_btn.setStyleSheet('padding: 0 5px; width: 50px; margin: 20px 50;')
        self.selected_colors_sizes = []

        self.sizes_list_dialog_btn.clicked.connect(self.openSizesListDialog)
        first_vertical_layout.addWidget(self.sizes_list_dialog_btn)

        self.sizesListPreview = QLabel('')
        self.sizesListPreview.setEnabled(False)
        self.sizesListPreview.setStyleSheet('''background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #fafafa, stop: 0.4 #f4f4f4,
                                stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);;
                                ''')

        first_vertical_layout.addWidget(self.sizesListPreview)

        if self.product:
            self.add_button = QPushButton('حفظ التعديل')
            self.productSkucodeInput.setText(self.product.sku_code)
            self.originalPriceInput.setText(str(self.product.original_price))
            self.suggestedPrice.setText(str(self.product.suggested_price))
            self.classificationsCombo.setCurrentIndex(classifications_list.index(self.product.classification.name))
            self.imagePathPreview.setPixmap(QtGui.QPixmap(self.product.image).scaled(300, 300, QtCore.Qt.KeepAspectRatio))
            self.imagePath = self.product.image
            self.sizesListPreview.setText('المتاح بالمخزن \n' + get_color_sizes_preview(product))
        else:
            self.add_button = QPushButton('اضافة')

        self.add_button.setStyleSheet('margin: 20px 0;')
        self.add_button.clicked.connect(self.add_product)
        second_vertical_layout.addWidget(self.add_button)   

        self.setGeometry(500, 250, 900, 200)


    def openSizesListDialog(self):
        color_sizes_dialog = SizesMultiChoiceListDialog()
        color_sizes_dialog.exec_()

        if color_sizes_dialog.selected_color_sizes:
            
            self.selected_colors_sizes.append(color_sizes_dialog.selected_color_sizes) 
            
            sizes_preview = self.sizesListPreview.text()

            if sizes_preview.startswith('المتاح'):
                sizes_preview = ''

            if sizes_preview:
                sizes_preview += '\n'

            color, sizes_dic = color_sizes_dialog.selected_color_sizes

            t = ''
            for item in sizes_dic.items():
                t += f' - {item[0]}' if item[1] == 1 else f' - ({item[0]} * {item[1]})'
                
            sizes_preview += f'{color}: {t}' 

            self.sizesListPreview.setText(sizes_preview)


    def openFileDialog(self):
        filename = QFileDialog.getOpenFileName(self, 'اختر الصورة', filter='Images (*.png *.jpg)')
        self.imagePath = filename[0]
        self.imagePathPreview.setPixmap(
            QtGui.QPixmap(self.imagePath).scaled(
                300, 
                300, 
                QtCore.Qt.KeepAspectRatio
            )
        )
 
    def add_product(self):
        
         # to skip validation if there is no change in sizes and colors
        if self.product and not self.selected_colors_sizes:
            self.selected_colors_sizes = 'no change'

        product_data = {
            'skucode': self.productSkucodeInput.text(),
            'originalPrice': self.originalPriceInput.text(),
            'suggestedPrice': self.suggestedPrice.text(),
            'image': self.imagePath,
            'sizes': self.selected_colors_sizes
        }

        fields_translation = {
            'skucode': 'الكود',
            'originalPrice': 'سعر الجملة',
            'suggestedPrice': 'أقل سعر',
            'image': 'صورة المنتج',
            'sizes': 'المقاسات'
        }

        for field_name, value in product_data.items():

            if not value:
                field_translated = fields_translation[field_name]
                QMessageBox.warning(
                    self, 
                    field_translated,
                    f'يرجى ملىء حقل ({field_translated}) اولا!'
                )
                return 

        product_with_same_code = self.session.query(Product).filter_by(sku_code=product_data['skucode']).first()
        
        if product_with_same_code:
            if not self.product == product_with_same_code:

                QMessageBox.warning(
                        self, 
                        'خطأ بالكود',
                        f'هذا الكود تم استخدامه من قبل ، يرجى اختيار كود جديد'
                )
                return 

        img_name = product_data['image'].split('/')[-1]
        image_destination = str(Path.joinpath(current_path, 'images', img_name))

        self.same_destination = False

        if self.product:
            
            if self.product.image != image_destination:
                self.same_destination = True 

            # we check if the colors-sizes list changed 
            if not self.sizesListPreview.text().startswith('المتاح'):
                # if changed we start changing colors depending on new values 
                # but with respect to sold units of previous colors and its sizes
                self.sold_colors = set(unit.color for unit in self.product.sold_units)
                self.sold_colors.update(c_s[0] for c_s in self.selected_colors_sizes)

                for color_obj in self.product.colors:
                    # if there's sold units or will be created in the new editing 
                    # with this color, we just delete all availabel sizes 
                    # for clean addition later in the next lines if we want
                    if color_obj.name in self.sold_colors:

                        self.session.query(ColorSize).filter_by(
                            color=color_obj, 
                        ).delete()
                    # else we delete the color 
                    else:
                        self.session.delete(color_obj)

        if not self.same_destination:
            img = Image.open(product_data['image'])
            img.save(image_destination)

        if not self.product:
            self.product = get_or_create(
                self.session, 
                Product, 
                sku_code=product_data['skucode'],
                original_price=product_data['originalPrice'] ,
                suggested_price=product_data['suggestedPrice'] ,
                image=image_destination,
            )

        else:
            self.product.sku_code = product_data['skucode']
            self.product.original_price = int(product_data['originalPrice'])
            self.product.suggested_price = int(product_data['suggestedPrice'])
            self.product.image = image_destination

        classification = self.session.query(Classification).filter(
            Classification.name==self.classificationsCombo.currentText()
        ).one()

        self.product.classification = classification

        if type(self.selected_colors_sizes) == list:

            self.pairs_count = 0

            for color, sizes_dic in self.selected_colors_sizes:

                color = get_or_create(self.session, ProductColor, name=color, product=self.product)
                
                for size, counts in sizes_dic.items():

                    size_obj = get_or_create(self.session, ProductSize, size=int(size))

                    color_size_obj = get_or_create(
                        self.session, 
                        ColorSize, 
                        color=color, 
                        size=size_obj,
                        repeating_counter=counts
                    )
                    self.pairs_count += int(counts)
                
                self.product.pairs_number = self.pairs_count

        self.session.commit()

        QMessageBox.information(
            self,
            'عملية ناجحة',
            'تمت الاضافة بنجاح'
        )

        self.close()

      
class CheckoutForm(QDialog):

    def __init__(self, session, product, sold_product=None):

        super().__init__()

        self.session = session
        
        self.product = product

        # in case of editing sold unit
        self.sold_product = sold_product
        # end

        self.setWindowTitle('انشاء او تعديل عملية بيع')
        
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

        ''')

        upper_hlayout = QHBoxLayout()

        first_vertical_layout = QVBoxLayout()
        second_vertical_layout = QVBoxLayout()

        # second_vertical_layout.setDirection(QHBoxLayout.RightToLeft)
        
        edit_frame = QFrame()
        edit_frame.setStyleSheet('QFrame { margin: 10px; padding: 5px }')
        edit_frame.setFrameStyle(2)
        edit_frame.setLayout(first_vertical_layout)
        
        data_frame = QFrame()
        data_frame.setStyleSheet('QFrame { margin: 0px; background: #D5DBDB }')
        data_frame.setFrameStyle(2)
        data_frame.setLayout(second_vertical_layout)

        upper_hlayout.addWidget(edit_frame, 50)
        upper_hlayout.addWidget(data_frame, 50)

        self.setLayoutDirection(QtCore.Qt.RightToLeft)

        self.setLayout(upper_hlayout)
        
        self.productSKUCode = QLineEdit(self.product.sku_code)
        self.productSKUCode.setAlignment(QtCore.Qt.AlignCenter)
        self.productSKUCode.setEnabled(False)

        self.pairsNumber = QLineEdit(str(self.product.pairs_number))
        self.pairsNumber.setAlignment(QtCore.Qt.AlignCenter)
        self.pairsNumber.setEnabled(False)

        self.suggestedPrice = QLineEdit(str(self.product.suggested_price))
        self.suggestedPrice.setAlignment(QtCore.Qt.AlignCenter)
        self.suggestedPrice.setEnabled(False)
        self.suggestedPrice.setStyleSheet('margin-bottom: 20px;')

        # in case of editing sold unit
        if self.sold_product:
            self.add_button = QPushButton('تطبيق التعديل')
            self.priceSoldBy = QLineEdit(str(sold_product.sold_by_price))
        else:
            self.add_button = QPushButton('اضافة للصادر')
            self.priceSoldBy = QLineEdit()
        # end
        self.add_button.clicked.connect(self.add_product)

        self.colorsListCombo = QComboBox()

        self.colorsListCombo.addItems([color.name for color in self.product.colors])

        self.colorsListCombo.currentTextChanged.connect(self.color_selected)

        self.sizesListCombo = QComboBox()
        self.color_selected()

        self.imagePathPreview =  QLabel()
        self.imagePathPreview.setPixmap(
            QtGui.QPixmap(self.product.image).scaledToHeight(250)
        )
        
        second_vertical_layout.addWidget(self.imagePathPreview)
    
        second_vertical_layout.addWidget(QLabel('الكود'))
        second_vertical_layout.addWidget(self.productSKUCode)

        second_vertical_layout.addWidget(QLabel('عدد الازواج المتاحة'))
        second_vertical_layout.addWidget(self.pairsNumber)

        second_vertical_layout.addWidget(QLabel('السعر المقترح'))
        second_vertical_layout.addWidget(self.suggestedPrice)
        
        # in case of editing sold unit
        if self.sold_product:
            current_color_label = QLabel(f'اللون الحالى: {sold_product.color} ')
            current_color_label.setStyleSheet('color: #F1948A')
            first_vertical_layout.addWidget(current_color_label)
        # end

        first_vertical_layout.addWidget(QLabel('اختر اللون'))
        first_vertical_layout.addWidget(self.colorsListCombo)

        # in case of editing sold unit
        if self.sold_product:
            current_size_label = QLabel(f'المقاس الحالى: {sold_product.size} ')
            current_size_label.setStyleSheet('color: #F1948A')
            first_vertical_layout.addWidget(current_size_label)
        # end

        first_vertical_layout.addWidget(QLabel('اختر المقاس'))
        first_vertical_layout.addWidget(self.sizesListCombo)

        first_vertical_layout.addWidget(QLabel('سعر البيع'))
        first_vertical_layout.addWidget(self.priceSoldBy)
        
        first_vertical_layout.addWidget(self.add_button)   

        self.setGeometry(500, 250, 900, 200)     
    
    def color_selected(self):

        color_name = self.colorsListCombo.currentText()

        self.selected_color_obj = self.session.query(ProductColor).filter_by(name=color_name, product=self.product).one()

        self.sizesListCombo.clear()

        # in case of editing sold unit
        if self.sold_product and self.sold_product.color == color_name:

            size_obj = self.session.query(ProductSize).filter_by(size=self.sold_product.size).one()

            color_size = self.session.query(ColorSize).filter_by(
                color=self.selected_color_obj,
                size=size_obj
            ).first()

            if not color_size:
                self.sizesListCombo.addItem(str(self.sold_product.size))
        # end

        if self.selected_color_obj.color_sizes:
            self.sizesListCombo.setEnabled(True)
            self.add_button.setEnabled(True)
            self.sizesListCombo.addItems(
                [str(color_size.size) for color_size in self.selected_color_obj.color_sizes if color_size.repeating_counter > 0]
            )

        else:
            self.sizesListCombo.setEnabled(False)
            self.add_button.setEnabled(False)
 
    def add_product(self):
        
        selling_price = self.priceSoldBy.text()
        selected_size = self.sizesListCombo.currentText()

        if not selling_price:

            QMessageBox.warning(
                        self, 
                        'سعر البيع',
                        'يرجى ملىء حقل (سعر البيع) اولا!'
                    )
            return
        
        confirmation_message_text = f'''
                                        السعر : {selling_price} 
                                        اللون: {self.selected_color_obj.name}
                                        المقاس: {selected_size}
                                    '''

        confirmation_message = get_confirmation_message('تأكيد عملية البيع', confirmation_message_text)
        confirmation_message.exec_()

        if confirmation_message.clickedButton().text() == 'الغاء':
            return

        size = self.session.query(ProductSize).filter_by(size=selected_size).one()

        # in case of editing sold unit
        if self.sold_product:

            sold_size_obj = self.session.query(ProductSize).filter_by(size=self.sold_product.size).one()
            sold_color_obj = self.session.query(ProductColor).filter_by(name=self.sold_product.color, product=self.product).one()

            # adding the old size 
            # first we check if the target color_size pair is repeated so if it still exists
            # we increase it's repeating counts by one
            color_size = self.session.query(ColorSize).filter_by(
                color=sold_color_obj,
                size=sold_size_obj
            ).first()

            if color_size:

                color_size.repeating_counter += 1

            # else we create new one 
            else:
                ncolor_size = ColorSize(color=sold_color_obj, size=sold_size_obj, repeating_counter=1)
                self.session.add(ncolor_size)
            
            # here we remove the new chosen color_size pair or decrease by one if it's repeated
            color_size_obj = self.session.query(ColorSize).filter_by(
                color=self.selected_color_obj, 
                size=size
            ).one()

            if color_size_obj.repeating_counter > 1:

                color_size_obj.repeating_counter -= 1

            else:

                self.session.delete(color_size_obj)

            self.sold_product.size = size.size
            self.sold_product.color = self.selected_color_obj.name
            self.sold_product.sold_by_price = selling_price

            self.session.add(self.sold_product)
            self.session.commit()

            QMessageBox.information(
                self,
                'عملية ناجحة',
                'تم التعديل بنجاح'
            )
            self.close()
            return
        # end  

        # removing color_size pair or decrease it by one if it's repeated
        color_size_obj = self.session.query(ColorSize).filter_by(
            color=self.selected_color_obj, 
            size=size
        ).one()

        if color_size_obj.repeating_counter > 1:

            color_size_obj.repeating_counter -= 1

        else:

            self.session.delete(color_size_obj)
        
        self.product.pairs_number -= 1

        sold_product = SoldProduct(
            product=self.product, 
            color=self.selected_color_obj.name,
            size=selected_size,
            sold_by_price=selling_price,
        )
        
        self.session.add(sold_product)
        self.session.commit()

        QMessageBox.information(
            self,
            'عملية ناجحة',
            'تمت الاضافة بنجاح'
        )
        self.close()

        
        
        

        

        
