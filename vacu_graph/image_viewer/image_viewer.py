from PyQt5.QtWidgets import QVBoxLayout, QWidget, QFileDialog, QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

from vacu_graph.canvas.canvas import CanvasWidget

class ImageViewerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.img = QLabel(self)
        self.img.setAlignment(Qt.AlignCenter)

        self.img_underlay = QImage()

        self.canvas = CanvasWidget(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.img)

    def resizeEvent(self, event):
        self.canvas.resize(self.img.size())
        super().resizeEvent(event)

    def load_image(self, image_path=None):
        image_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
        if not image_path or image_path is None:
            return
        
        pixmap = QPixmap(image_path)
        self.img.setPixmap(pixmap)
        print(pixmap.size())
        self.img.resize(pixmap.size())
        self.canvas.resize(pixmap.size())

        self.canvas.setGeometry(self.img.geometry())

        # get an QImage object so we get access to each pixel
        self.img_underlay = self.img.pixmap().toImage().convertToFormat(QImage.Format_Mono)
        self.canvas.underlayImg = self.img_underlay

        print('Canvas geometry: ', self.canvas.geometry())
        print('Image geometry: ', self.img.geometry())

        return pixmap.size()
    
    def annotate_line(self):
        self.canvas.annotate_line()

    def annotate_axes(self):
        self.canvas.annotate_axes()

    def get_curves(self):
        return self.canvas.curves
    
    def get_precision(self):
        return self.canvas.precision
    
    def get_axes(self):
        return self.canvas.axes