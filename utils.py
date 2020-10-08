from PyQt5.QtWidgets import QMessageBox, QPushButton
from PyQt5.QtGui import QFont
from PyQt5 import QtCore

def get_confirmation_message(title, message):

    confirmation_message = QMessageBox()
    confirmation_message.setLayoutDirection(QtCore.Qt.RightToLeft)
    confirmation_message.setStyleSheet('messagebox-text-interaction-flags: 5')
    confirmation_message.setFont(QFont('courier new', 16))
    confirmation_message.setIcon(QMessageBox.Warning)
    confirmation_message.setWindowTitle(title)
    confirmation_message.setText(message)

    confirmation_message.addButton(QPushButton('تأكيد'), QMessageBox.ActionRole)
    confirmation_message.addButton(QPushButton('الغاء'), QMessageBox.RejectRole)

    return confirmation_message


def get_color_sizes_preview(product):
    t = ''
    for i, color in enumerate(product.colors):

        t2 = ''
        for c_z in color.color_sizes:
            t2 += f'{c_z.size}/' if c_z.repeating_counter == 1 else f'({c_z.size} * {c_z.repeating_counter})/'
        
        if i:
            t += '\n'

        t += f'{color}: {t2}'
    return t
        