from typing import TYPE_CHECKING
import math
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QPushButton, QGridLayout
from utils import isNumOrDot, isEmpty, isValidNumber, convertToNumber
from variables import MEDIUM_FONT_SIZE

if TYPE_CHECKING:
    from display import Display
    from main_window import MyWindow
    from info import Info

class Button(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configStyle()

    def configStyle(self):
        font = self.font()
        font.setPixelSize(MEDIUM_FONT_SIZE)
        self.setFont(font)
        self.setMinimumSize(75, 75)


class ButtonsGrid(QGridLayout):
    def __init__(
            self, display: 'Display', info: 'Info', window: 'MyWindow', *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self._gridMask = [
            ['C', '◀', '^', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['N',  '0', '.', '='],
        ]

        self.display = display
        self.info = info
        self.window = window
        self._equation = ''
        self._equationInitialValue = 'Sua conta'
        self._left = None
        self._right = None
        self._op = None

        self.equation = self._equationInitialValue
        self._makeGrid()

    @property
    def equation(self):
        return self._equation
    
    @equation.setter
    def equation(self, value):
        self._equation = value
        self.info.setText(value)

    def _makeGrid(self):
        self.display.eqPressed.connect(self._eq)
        self.display.delPressed.connect(self._backspace)
        self.display.escPressed.connect(self._clear)
        self.display.inputPressed.connect(self._insertToDisplay)
        self.display.operatorPressed.connect(self._configLeftOp)

        for rowNumber, rowData in enumerate(self._gridMask):
            for colNumber, buttonText in enumerate(rowData):
                button = Button(buttonText)

                if not isNumOrDot(buttonText) and not isEmpty(buttonText):
                    button.setProperty('cssClass', 'specialButton')
                    self._configSpecialButton(button)
                self.addWidget(button, rowNumber, colNumber)

                slot = self._makeSlot(self._insertToDisplay, buttonText)
                self._connectButtonClicked(button, slot)

    def _connectButtonClicked(self, button, slot):
        button.clicked.connect(slot) 

    def _configSpecialButton(self, button):
        text = button.text()
        
        if text == 'C':
            self._connectButtonClicked(button, self._clear)

        if text == '◀':
            self._connectButtonClicked(button, self.display.backspace)
        
        if text in '+-/*^':
            self._connectButtonClicked(
                button,
                self._makeSlot(self._configLeftOp, text)
            )
        
        if text == 'N':
            self._connectButtonClicked(button, self._invertNumber)

        if text == '=':
            self._connectButtonClicked(button, self._eq)

    def _makeSlot(self, func, *args, **kwargs):
        @ Slot(bool)
        def realSlot(_):
            func(*args, **kwargs)
        return realSlot

    @Slot()
    def _invertNumber(self):
        displayText = self.display.text()

        if not isValidNumber(displayText):
            return
        
        number = convertToNumber(displayText) * -1
        self.display.setText(str(number))



    @Slot()
    def _insertToDisplay(self, text):
        newDisplayValue = self.display.text() + text

        if not isValidNumber(newDisplayValue):
            return
        
        self.display.insert(text)

    @Slot()    
    def _clear(self):
        print('')
        self._left = None
        self._right = None
        self._op = None
        self.equation = self._equationInitialValue
        self.display.clear()
        self.display.setFocus()

    @Slot()
    def _configLeftOp(self, text):
        displayText = self.display.text()  # Left number.
        self.display.clear()  # Clean the display.
        self.display.setFocus()

        # If no valid number has been set before the operator.
        if not isValidNumber(displayText) and self._left is None:
            self._showError('Você não digitou nada.')
            return
        
        # If there is value in the left number already, we just wait for the right number.
        if self._left is None:
            self._left = convertToNumber(displayText)

        self._op = text
        self.equation = f'{self._left} {self._op} ??'

    @Slot()
    def _eq(self):
        displayText = self.display.text()
        
        if not isValidNumber(displayText) or self._left is None:
            self._showError('Equação incompleta.')
            return
        
        self._right = convertToNumber(displayText)
        self.equation = f'{self._left} {self._op} {self._right}'
        result = 'error'

        try:
            if '^' in self.equation and isinstance(self._left, int | float):
                result = math.pow(self._left, self._right)
                result = convertToNumber(str(result))
            else:
                result = eval(self.equation)
        except ZeroDivisionError:
            self._showError('Um número não pode ser dividido por zero.')
        except OverflowError:
            self._showError('Essa conta não pode ser realizada.')

        self.display.clear()
        self.info.setText(f'{self.equation} = {result}')
        self._right = None
        self._left = result
        self.display.setFocus()

        if result == 'error':
            self._left = None
           
    @Slot()
    def _backspace(self):
        self.display.backspace
        self.display.setFocus()

    def _showError(self, text):
        msgBox = self.window.makeMsgBox()
        msgBox.setText(text)
        msgBox.setIcon(msgBox.Icon.Critical)
        msgBox.exec()
        self.display.setFocus()

    def _showInfo(self, text):
        msgBox = self.window.makeMsgBox()
        msgBox.setText(text)
        msgBox.setIcon(msgBox.Icon.Information)
        msgBox.exec()
        self.display.setFocus()