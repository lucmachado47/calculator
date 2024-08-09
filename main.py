import sys
from variables import WINDOW_ICON_PATH
from buttons import ButtonsGrid, Button
from info import Info
from main_window import MyWindow
from display import Display
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
import styles

if __name__ == '__main__':
    # Create the application
    app = QApplication(sys.argv)
    styles.setupTheme(app)
    window = MyWindow()

    # Icon.
    icon = QIcon(str(WINDOW_ICON_PATH))
    window.setWindowIcon(icon)
    app.setWindowIcon(icon)

    # Info
    info = Info('Sua conta')
    window.addWidgetToVLayout(info)

    # Display
    display = Display()
    window.addWidgetToVLayout(display)

    # Grid
    buttonsGrid = ButtonsGrid(display, info, window)
    window.vLayout.addLayout(buttonsGrid)

    
    # Run the program.
    window.adjustFixedSize()
    window.show()
    app.exec()