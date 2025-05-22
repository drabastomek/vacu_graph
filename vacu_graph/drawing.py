import sys
import numpy as np 
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout,
    QWidget, QFileDialog, QLabel, QHBoxLayout, QInputDialog, QDialog,
    QLineEdit, QDialogButtonBox, QFormLayout, QComboBox, QLineEdit
)
from PyQt5.QtGui import QPainter, QPen, QPixmap, QImage
from PyQt5.QtCore import Qt, QPoint

import pandas as pd

from image_viewer import ImageViewerWidget

class DrawingApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Plate curves extractor")
        self.viewer = ImageViewerWidget(self)
        self.output_dir = '.' # current directory
        self.output_dir_allocated = False

        self.init_ui()

    def init_ui(self):
        # controls
        load_btn = QPushButton("Load Image")
        add_axes = QPushButton("Annotate axes")
        add_line = QPushButton("Annotate line")
        save_btn = QPushButton("Save Annotations")

        load_btn.clicked.connect(self.load_image)
        add_axes.clicked.connect(self.annotate_axes)
        add_line.clicked.connect(self.annotate_line)
        save_btn.clicked.connect(self.save_annotations)

        controls = QHBoxLayout()
        controls.addWidget(load_btn)
        controls.addWidget(add_axes)
        controls.addWidget(add_line)
        controls.addWidget(save_btn)

        # configuration
        tube_type_conf_label = QLabel(self)
        tube_type_conf_label.setText('Tube type:')
        self.tube_type_input = QLineEdit(self)

        tube_type_layout = QHBoxLayout()
        tube_type_layout.addWidget(tube_type_conf_label)
        tube_type_layout.addWidget(self.tube_type_input)

        plate_voltage_conf_label = QLabel(self)
        plate_voltage_conf_label.setText('Voltage resolution:')
        self.plate_voltage_resolution = QLineEdit(self)

        plate_voltage_layout = QHBoxLayout()
        plate_voltage_layout.addWidget(plate_voltage_conf_label)
        plate_voltage_layout.addWidget(self.plate_voltage_resolution)

        configuration_layout = QHBoxLayout()
        configuration_layout.addLayout(tube_type_layout)
        configuration_layout.addLayout(plate_voltage_layout)

        # final layout
        layout = QVBoxLayout()
        layout.addLayout(controls)
        layout.addLayout(configuration_layout)
        layout.addWidget(self.viewer)

        # self.setLayout(layout)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_image(self):
        self.viewer.load_image()

    def annotate_axes(self):
        self.viewer.annotate_axes()
        
    def annotate_line(self):
        self.viewer.annotate_line()

    def save_annotations(self):
        curves = self.viewer.get_curves()

        if self.tube_type_input.text() == '' or self.plate_voltage_resolution.text() == '':
            ExceptionDialog(message='Please add the tube type and / or resolution.')
        elif len(curves) == 0:
            ExceptionDialog(message='Annotate the curves first')
        else:
            if not self.output_dir_allocated:
                self.output_dir = QFileDialog.getExistingDirectory(self, "Choose output directory",self.output_dir)
                self.output_dir_allocated = True

            tube_type = self.tube_type_input.text()
            resolution = float(self.plate_voltage_resolution.text())
            precision = self.viewer.get_precision()

            full = pd.DataFrame()

            for line in curves:
                points = pd.DataFrame(curves[line]['points'], columns=['voltage', 'current'])
                pixels = pd.DataFrame(curves[line]['pixels'], columns=['x', 'y'])
                temp_full = pd.concat([points, pixels], axis = 1)
                temp_full['line'] = line
                full = pd.concat([full, temp_full])

            full['group'] = (full['voltage'] / resolution).round(0) * resolution
            grouped = full.groupby(by=['line','group']).aggregate({'voltage': 'mean', 'current': 'mean'}).reset_index()
            grouped['current'] = grouped['current'].round(precision)
            grouped['voltage'] = grouped['group']
            grouped = grouped[['line', 'voltage', 'current']]

            full.to_csv(f'{self.output_dir}/{tube_type}-hi_res.csv', index=False)
            grouped.to_csv(f'{self.output_dir}/{tube_type}-agg.csv', index=False)

# class ImageViewerWidget(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.img = QLabel(self)
#         self.img.setAlignment(Qt.AlignCenter)

#         self.img_underlay = QImage()

#         self.canvas = CanvasWidget(self)

#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.addWidget(self.img)

#     def resizeEvent(self, event):
#         self.canvas.resize(self.img.size())
#         super().resizeEvent(event)

#     def load_image(self, image_path=None):
#         image_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
#         if not image_path or image_path is None:
#             return
        
#         pixmap = QPixmap(image_path)
#         self.img.setPixmap(pixmap)
#         self.img.resize(pixmap.size())
#         self.canvas.resize(pixmap.size())

#         self.img_underlay = self.img.pixmap().toImage().convertToFormat(QImage.Format_Mono)
#         self.canvas.underlayImg = self.img_underlay

#     def get_points(self):
#         return self.canvas.points
    
#     def annotate_line(self):
#         self.canvas.annotate_line()

#     def annotate_axes(self):
#         self.canvas.annotate_axes()

#     def get_curves(self):
#         return self.canvas.curves
    
#     def get_precision(self):
#         return self.canvas.precision

# class AxesAnnotationDialog(QDialog):
#     def __init__(self, parent=None):
#         super().__init__(parent)

#         self.axes_name = QComboBox(self)
#         self.axes_name.addItems(['Plate current', 'Plate voltage'])
#         self.min_point = QLineEdit(self)
#         self.max_point = QLineEdit(self)

#         buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

#         layout = QFormLayout(self)
#         layout.addRow("Select the axis to annotate", self.axes_name)
#         layout.addRow("Minimum value", self.min_point)
#         layout.addRow("Maximum value", self.max_point)
#         layout.addWidget(buttonBox)

#         buttonBox.accepted.connect(self.accept)
#         buttonBox.rejected.connect(self.reject)

#     def getAllInputs(self):
#         return {'axis': self.axes_name.currentText(), 'min': self.min_point.text(), 'max': self.max_point.text()}

# class ExceptionDialog(QDialog):
#     def __init__(self, parent=None, message=None):
#         super().__init__(parent)

#         if message is not None:
#             self.message = message
#         else:
#             self.message = 'An exception occured. Fix the forms before proceeding.'

#         self.setWindowTitle('Exception occured')
#         # Create a label with a message
#         label = QLabel(self.message)
#         buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
#         buttonBox.accepted.connect(self.accept)

#         # Create a layout for the dialog
#         dialog_layout = QVBoxLayout()
#         dialog_layout.addWidget(label)
#         dialog_layout.addWidget(buttonBox)

#         # Set the layout for the dialog
#         self.setLayout(dialog_layout)

#         # Show the dialog as a modal dialog (blocks the main window)
#         self.exec_()
    
# class CanvasWidget(QWidget):
#     def __init__(self, parent=None, underlay=None, geometry=None):
#         super().__init__(parent)
#         self.parent = parent
#         self.underlayImg = underlay

#         self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
#         self.setAttribute(Qt.WA_TranslucentBackground)
#         self.setMouseTracking(True)

#         if geometry is None:
#             self.setGeometry(0, 0, 800, 600)
#         else:
#             self.setGeometry(geometry)

#         self.drawing = False
#         self.last_point = QPoint()
#         self.current_point = QPoint()
#         self.shapes = []
#         self.temp_line = []
#         self.curves = {}

#         self.annotating_axes = False
#         self.axes = {}             # axes min / max coordinates and mapping to actual values ((min, max), (map_min, map_max))
#         self.axes_transform = {}   # store transform function for each axis in a form of (slope, offset)
#         self.text_annotations = [] # to make sure we got the scaling right
#         self.divider = {           # how many points to draw
#             'Plate current': 5,
#             'Plate voltage': 5
#         }
#         self.precision = 3         # precision for rounding final results

#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             self.drawing = True
#             self.last_point = event.pos()
#             self.current_point = event.pos()

#     def mouseReleaseEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             self.drawing = False
#             shape = (self.last_point, self.current_point)
#             self.shapes.append(shape)
#             self.update()

#             if not self.annotating_axes:
#                 coords = self.__extract_points(self.last_point, self.current_point)
#                 line = self.__find_the_points(coords, self.last_point, self.current_point)

#                 self.temp_line.append(line)

#             if self.annotating_axes:
#                 dlg = AxesAnnotationDialog()
#                 exception = False

#                 if dlg.exec():
#                     _ax = dlg.getAllInputs()

#                     axis = _ax['axis']

#                     diff_x = abs(self.shapes[0][0].x() - self.shapes[0][1].x())
#                     diff_y = abs(self.shapes[0][0].y() - self.shapes[0][1].y())
                    
#                     if axis == 'Plate voltage':
#                         if diff_y > diff_x:
#                             ExceptionDialog(message='Looks like you are trying to annotate current, not voltage.')
#                             exception = True
#                         else:
#                             self.axes[axis] = (
#                                 (int(_ax['min']), int(_ax['max'])),
#                                 (self.shapes[0][0].x(), self.shapes[0][1].x()),
#                                 self.shapes[0]
#                             )

#                     if axis == 'Plate current':
#                         if diff_x > diff_y:
#                             ExceptionDialog(message='Looks like you are trying to annotate voltage, not current.')
#                             exception = True
#                         else:
#                             self.axes[axis] = (
#                                 (int(_ax['min']), int(_ax['max'])),
#                                 (self.shapes[0][0].y(), self.shapes[0][1].y()),
#                                 self.shapes[0]
#                             )
#                 if not exception:
#                     self.__prepare_transforms(_ax['axis'])
#                     self.annotating_axes = False
#                     self.shapes = []

#     def paintEvent(self, event):
#         painter = QPainter(self)
        
#         # define pens
#         Rpen = QPen()
#         Rpen.setWidth(2)
#         Rpen.setColor(Qt.red)

#         Bpen = QPen()
#         Bpen.setWidth(2)
#         Bpen.setColor(Qt.blue)

#         Gpen = QPen()
#         Gpen.setWidth(2)
#         Gpen.setColor(Qt.green)
        
#         # draw guide lines
#         painter.setPen(Rpen)

#         for shape in self.shapes:
#             painter.drawLine(shape[0], shape[1])

#         if self.drawing:
#             painter.drawLine(self.last_point, self.current_point)

#         # draw curve points
#         painter.setPen(Bpen)

#         for curve in self.curves:
#             for x, y in self.curves[curve]['pixels']:
#                 painter.drawPoint(int(x),int(y))

#         # draw axes
#         painter.setPen(Gpen)

#         for _ax in self.axes:
#             pt1, pt2 = self.axes[_ax][2]
#             painter.drawLine(pt1, pt2)

#         # draw text
#         painter.setPen(Rpen)
#         for t in self.text_annotations:
#             painter.drawText(t[0], t[1], t[2])

#     def mouseMoveEvent(self, event):
#         if self.drawing:
#             self.current_point = event.pos()
#             self.update()

#     def annotate_line(self):
#         if len(self.axes_transform) != 2:
#             ExceptionDialog(message='Before annotating lines you need to annotate axes.')
#         elif len(self.temp_line) == 0:
#             ExceptionDialog(message='Draw the line to extract points.')
#         else:
#             x,y = self.__prepare_full_line(self.temp_line)
#             x_slope, x_offset = self.axes_transform['Plate voltage'][0], self.axes_transform['Plate voltage'][1]
#             y_slope, y_offset = self.axes_transform['Plate current'][0], self.axes_transform['Plate current'][1]

#             x_transform = [self.__transform_point(p, x_slope, x_offset) for p in x]
#             y_transform = [self.__transform_point(p, y_slope, y_offset) for p in y]

#             text, ok = QInputDialog.getText(self, "Annotate", "Enter label for this line:")

#             if ok:
#                 self.curves[text] = {
#                     'pixels': list(zip(x, y)),
#                     'points': list(zip(x_transform, y_transform))
#                 }
#                 self.shapes = []
#                 self.temp_line = []

#     def annotate_axes(self):
#         self.annotating_axes = True

#     def __prepare_transforms(self, axis):
#         _axis = self.axes[axis]
#         _map_dims, _img_dims = _axis[0], _axis[1]

#         slope = float(_map_dims[1] - _map_dims[0]) / float(_img_dims[1] - _img_dims[0])
#         offset = float(_img_dims[0])

#         self.axes_transform[axis] = (slope, offset)
        
#         # add some 5 text annotations to confirm
#         # if max(_map_dims) <=10:
#         max_map_dim = max(_map_dims)
#         self.divider[axis] = int(max_map_dim / np.power(10, int(np.log10(max_map_dim))))

#         step_map = round((_map_dims[1] - _map_dims[0]) / self.divider[axis])
#         step_img = round((_img_dims[1] - _img_dims[0]) / self.divider[axis])

#         if axis == 'Plate current':
#             ## determine precision for the current
#             self.precision = abs(int(np.log10(max(_map_dims)))-3)

#             missing_coord = _axis[-1][0].x()
#             for y, text in zip(
#                 range(_img_dims[0]+step_img, _img_dims[1]+step_img, step_img),
#                 range(_map_dims[0]+step_map, _map_dims[1]+step_map, step_map)
#             ):
#                 self.text_annotations.append((missing_coord, y, str(text)))
#         else:
#             missing_coord = _axis[-1][0].y()
#             for x, text in zip(
#                 range(_img_dims[0]+step_img, _img_dims[1]+step_img, step_img),
#                 range(_map_dims[0]+step_map, _map_dims[1]+step_map, step_map)
#             ):
#                 self.text_annotations.append((x, missing_coord, str(text)))

#     def __transform_point(self, point, slope, offset):
#         return slope * (point - offset)

#     def __swap_variables(self, x, y):
#         x = x ^ y  
#         y = x ^ y  
#         x = x ^ y 

#         return x, y

#     def __extract_points(self, start_point, end_point):
#         s_x, s_y = start_point.x(), start_point.y()
#         e_x, e_y = end_point.x(), end_point.y()

#         coords = np.ones([self.underlayImg.width(), self.underlayImg.height()]) * 16777216

#         # flip if end point coords are smaller than the start ones
#         if s_x > e_x: 
#             s_x, e_x = self.__swap_variables(s_x, e_x)

#         if s_y > e_y:
#             s_y, e_y = self.__swap_variables(s_y, e_y)

#         for x in range(s_x, e_x):
#             for y in range(s_y, e_y):
#                 pix = self.underlayImg.pixel(x,y) & 0x00FFFFFF
#                 if pix == 0:
#                     coords[x][y] = 0

#         # coords_np = np.array(coords)
#         # np.save('test.npy', coords_np)
#         # print(start_point, end_point)
#         return coords


#     def __find_black_point(self, coords, start_point, band_width): 
#         # TODO: add a penalty for veering too far away from the direction of the drawn line
#         start_point_black_vec = coords[start_point.x(), start_point.y()-band_width:start_point.y()+band_width]
#         try:
#             for i in range(band_width):
#                 if start_point_black_vec[band_width + i] == 0:
#                     return start_point.y()+i
#                 if start_point_black_vec[band_width - i] == 0:
#                     return start_point.y()-i
#         except IndexError as e:
#             raise e
        
#     def __reject_outliers(self, counts, values, m = 5.):
#         d = np.abs(counts - np.median(counts))
#         mdev = np.median(d)
#         s = d/mdev if mdev else np.zeros(len(d))
#         return values[np.where(s<m)[0]]
        
#     def __find_the_points(self, coords_input, start_point, end_point, band_width=50):
#         coords = np.where(coords_input == 0)
#         u_x, c_x = np.unique(coords[0], return_counts=True)
#         u_y, c_y = np.unique(coords[1], return_counts=True)

#         no_outliers_x = self.__reject_outliers(c_x, u_x)
#         no_outliers_y = self.__reject_outliers(c_y, u_y)

#         x_keep, y_keep = np.array([]), np.array([])

#         for x, y in zip(*coords):
#             if x in no_outliers_x and y in no_outliers_y:
#                 x_keep = np.concat([x_keep, [x]])
#                 y_keep = np.concat([y_keep, [y]])
        
#         coords = [x_keep, y_keep]

#         slope = (end_point.y() - start_point.y()) / (end_point.x() - start_point.x())
#         intercept = end_point.y() - slope * end_point.x()
        
#         idxs = np.array([np.power(slope * e + intercept - coords[1][i],2) for i,e in enumerate(coords[0])]) < 20.

#         voltage_all = np.arange(np.min(coords[0]), np.max(coords[0]))
#         missing = np.array(list(set(voltage_all).difference(coords[0])))
#         current_inter = np.interp(missing, coords[0][idxs], coords[1][idxs])

#         data = pd.DataFrame({'voltage': np.concat([coords[0][idxs], missing]), 'current': np.concat([coords[1][idxs], current_inter])}).groupby('voltage').mean().reset_index().values.T#.plot.scatter(x='voltage', y='current')
#         return [data[0], data[1]]

#     # def __find_the_points(self, coords, start_point, end_point, band_width=50):
#     #     # TODO: this needs a better algorithm
#     #     try:
#     #         # if the start point is white -- find the nearest (up or down) point that is black
#     #         start_point = QPoint(start_point.x(), self.__find_black_point(coords, start_point, band_width))
#     #     except:
#     #         start_point = start_point

#     #     # find the line equation so we can follow the points
#     #     slope = (end_point.y() - start_point.y()) / (end_point.x() - start_point.x())
#     #     intercept = end_point.y() - slope * end_point.x()

#     #     line = (np.arange(start_point.x(), end_point.x()) * slope + intercept).astype('int')
        
#     #     # find the 'black' points i.e. follow the line
#     #     x_start = start_point.x()
#     #     x_end = end_point.x()
        
#     #     line_coords = [np.array([]), np.array([])]
        
#     #     for i in range(x_start+1, x_end):
#     #         if coords[i, line[i-x_start]] == 0.0:
#     #             # if it's a black point -- just take it
#     #             line_coords[0] = np.append(line_coords[0], i)
#     #             line_coords[1] = np.append(line_coords[1], line[i-x_start])
#     #         else:
#     #             try:
#     #                 # otherwise, find the nearest black point
#     #                 bp = self.__find_black_point(coords, QPoint(i, int(line[i-x_start])), band_width)

#     #                 if bp is not None:
#     #                     line_coords[0] = np.append(line_coords[0], i)
#     #                     line_coords[1] = np.append(line_coords[1], bp)        
#     #             except:
#     #                 pass
#     #     return line_coords
    
#     def __prepare_full_line(self, points):
#         x = np.concat([e[0] for e in points])
#         y = np.concat([e[1] for e in points])
#         _min, _max = np.min(x), np.max(x)
        
#         missing = sorted(set(range(int(_min), int(_max) + 1)).difference(x))
        
#         x_app, y_app = np.array([]), np.array([])
        
#         for num in missing:
#             inferred = np.round((np.interp(num, x, -y)))
#             x_app = np.append(x_app, num)
#             y_app = np.append(y_app, -inferred)

#         x = np.concat([x, x_app])
#         y = np.concat([y, y_app])

#         return x, y

# def main():
#     app = QApplication(sys.argv)
#     window = DrawingApp()
#     window.show()
#     sys.exit(app.exec_())

# if __name__ == "__main__":
#     main()
