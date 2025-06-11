from PyQt6.QtWidgets import (
    QVBoxLayout,
    QLabel, QDialog,
    QLineEdit, QDialogButtonBox, QFormLayout, QComboBox, QLineEdit
)

class AxesAnnotationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.axes_name = QComboBox(self)
        self.axes_name.addItems(['Plate current', 'Plate voltage'])
        self.min_point = QLineEdit(self)
        self.max_point = QLineEdit(self)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)

        layout = QFormLayout(self)
        layout.addRow("Select the axis to annotate", self.axes_name)
        layout.addRow("Minimum value", self.min_point)
        layout.addRow("Maximum value", self.max_point)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getAllInputs(self):
        return {'axis': self.axes_name.currentText(), 'min': self.min_point.text(), 'max': self.max_point.text()}

class ExceptionDialog(QDialog):
    def __init__(self, parent=None, message=None):
        super().__init__(parent)

        if message is not None:
            self.message = message
        else:
            self.message = 'An exception occured. Fix the forms before proceeding.'

        self.setWindowTitle('Exception occured')
       
        # Create a label with a message
        label = QLabel(self.message)
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttonBox.accepted.connect(self.accept)

        # Create a layout for the dialog
        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(label)
        dialog_layout.addWidget(buttonBox)

        # Set the layout for the dialog
        self.setLayout(dialog_layout)

        # Show the dialog as a modal dialog (blocks the main window)
        self.exec()
    