import sys
import numpy as np 
from PySide6.QtWidgets import (
        QWidget, QInputDialog
)
from PySide6.QtGui import QPainter, QPen, QImage, QColorConstants
from PySide6.QtCore import Qt, QPoint

from vacu_graph.dialogs.dialogs import AxesAnnotationDialog, ExceptionDialog
import pandas as pd

class CanvasWidget(QWidget):
    def __init__(self, parent=None, underlay=None, geometry=None):
        super().__init__(parent)
        self.parent = parent
        self.underlayImg: QImage = underlay

        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        if geometry is None:
            self.setGeometry(0, 0, 800, 600)
        else:
            self.setGeometry(geometry)

        self.drawing = False
        self.last_point = QPoint()
        self.current_point = QPoint()
        self.shapes = []
        self.temp_line = []
        self.curves = {}

        self.annotating_axes = False
        self.axes = {}             # axes min / max coordinates and mapping to actual values ((min, max), (map_min, map_max))
        self.axes_transform = {}   # store transform function for each axis in a form of (slope, offset)
        self.text_annotations = [] # to make sure we got the scaling right
        self.divider = {           # how many points to draw
            'Plate current': 5,
            'Plate voltage': 5
        }
        self.precision = 3         # precision for rounding final results

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()
            self.current_point = event.pos()
            print(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
            shape = (self.last_point, self.current_point)
            self.shapes.append(shape)
            self.update()

            if not self.annotating_axes:
                coords = self.__extract_points(self.last_point, self.current_point)
                line = self.__find_the_points(coords, self.last_point, self.current_point)

                self.temp_line.append(line)

            if self.annotating_axes:
                dlg = AxesAnnotationDialog()
                exception = False

                if dlg.exec():
                    _ax = dlg.getAllInputs()

                    axis = _ax['axis']

                    diff_x = abs(self.shapes[0][0].x() - self.shapes[0][1].x())
                    diff_y = abs(self.shapes[0][0].y() - self.shapes[0][1].y())
                    
                    if axis == 'Plate voltage':
                        if diff_y > diff_x:
                            ExceptionDialog(message='Looks like you are trying to annotate current, not voltage.')
                            exception = True
                        else:
                            self.axes[axis] = (
                                (int(_ax['min']), int(_ax['max'])),
                                (self.shapes[0][0].x(), self.shapes[0][1].x()),
                                self.shapes[0]
                            )

                    if axis == 'Plate current':
                        if diff_x > diff_y:
                            ExceptionDialog(message='Looks like you are trying to annotate voltage, not current.')
                            exception = True
                        else:
                            self.axes[axis] = (
                                (int(_ax['min']), int(_ax['max'])),
                                (self.shapes[0][0].y(), self.shapes[0][1].y()),
                                self.shapes[0]
                            )
                if not exception:
                    self.__prepare_transforms(_ax['axis'])
                    self.annotating_axes = False
                    self.shapes = []

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # define pens
        Rpen = QPen()
        Rpen.setWidth(2)
        Rpen.setColor(Qt.red)

        Bpen = QPen()
        Bpen.setWidth(2)
        Bpen.setColor(Qt.blue)

        Gpen = QPen()
        Gpen.setWidth(2)
        Gpen.setColor(Qt.green)
        
        # draw guide lines
        painter.setPen(Rpen)

        for shape in self.shapes:
            painter.drawLine(shape[0], shape[1])

        if self.drawing:
            painter.drawLine(self.last_point, self.current_point)

        # draw curve points
        painter.setPen(Bpen)

        for curve in self.curves:
            for x, y in self.curves[curve]['pixels']:
                painter.drawPoint(int(x),int(y))

        # draw axes
        painter.setPen(Gpen)

        for _ax in self.axes:
            pt1, pt2 = self.axes[_ax][2]
            painter.drawLine(pt1, pt2)

        # draw text
        painter.setPen(Rpen)
        for t in self.text_annotations:
            painter.drawText(t[0], t[1], t[2])

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.current_point = event.pos()
            self.update()

    def annotate_line(self):
        if len(self.axes_transform) != 2:
            ExceptionDialog(message='Before annotating lines you need to annotate axes.')
        elif len(self.temp_line) == 0:
            ExceptionDialog(message='Draw the line to extract points.')
        else:
            x,y = self.__prepare_full_line(self.temp_line)
            x_slope, x_offset = self.axes_transform['Plate voltage'][0], self.axes_transform['Plate voltage'][1]
            y_slope, y_offset = self.axes_transform['Plate current'][0], self.axes_transform['Plate current'][1]

            x_transform = [self.__transform_point(p, x_slope, x_offset) for p in x]
            y_transform = [self.__transform_point(p, y_slope, y_offset) for p in y]

            text, ok = QInputDialog.getText(self, "Annotate", "Enter label for this line:")

            if ok:
                self.curves[text] = {
                    'pixels': list(zip(x, y)),
                    'points': list(zip(x_transform, y_transform))
                }
                self.shapes = []
                self.temp_line = []

    def annotate_axes(self):
        self.annotating_axes = True

    def __prepare_transforms(self, axis):
        _axis = self.axes[axis]
        _map_dims, _img_dims = _axis[0], _axis[1]

        slope = float(_map_dims[1] - _map_dims[0]) / float(_img_dims[1] - _img_dims[0])
        offset = float(_img_dims[0])

        self.axes_transform[axis] = (slope, offset)
        
        # add some 5 text annotations to confirm
        max_map_dim = max(_map_dims)
        self.divider[axis] = int(max_map_dim / np.power(10, int(np.log10(max_map_dim))))

        step_map = round((_map_dims[1] - _map_dims[0]) / self.divider[axis])
        step_img = round((_img_dims[1] - _img_dims[0]) / self.divider[axis])

        if axis == 'Plate current':
            ## determine precision for the current
            self.precision = abs(int(np.log10(max(_map_dims)))-3)

            missing_coord = _axis[-1][0].x()
            for y, text in zip(
                range(_img_dims[0]+step_img, _img_dims[1]+step_img, step_img),
                range(_map_dims[0]+step_map, _map_dims[1]+step_map, step_map)
            ):
                self.text_annotations.append((missing_coord, y, str(text)))
        else:
            missing_coord = _axis[-1][0].y()
            for x, text in zip(
                range(_img_dims[0]+step_img, _img_dims[1]+step_img, step_img),
                range(_map_dims[0]+step_map, _map_dims[1]+step_map, step_map)
            ):
                self.text_annotations.append((x, missing_coord, str(text)))

    def __transform_point(self, point, slope, offset):
        return slope * (point - offset)

    def __swap_variables(self, x, y):
        x = x ^ y  
        y = x ^ y  
        x = x ^ y 

        return x, y

    def __extract_points(self, start_point, end_point):
        s_x, s_y = start_point.x(), start_point.y()
        e_x, e_y = end_point.x(), end_point.y()

        print('points: ', s_x, s_y, e_x, e_y)
        print(self.geometry())

        coords = np.ones([self.underlayImg.width(), self.underlayImg.height()]) * 16777216

        # flip if end point coords are smaller than the start ones
        if s_x > e_x: 
            s_x, e_x = self.__swap_variables(s_x, e_x)

        if s_y > e_y:
            s_y, e_y = self.__swap_variables(s_y, e_y)

        for x in range(s_x, e_x):
            for y in range(s_y, e_y):
                pix = self.underlayImg.pixel(x,y) & 0x00FFFFFF
                if pix == 0:
                    coords[x][y] = 0

        return coords
        
    def __reject_outliers(self, counts, values, m = 5.):
        d = np.abs(counts - np.median(counts))
        mdev = np.median(d)
        s = d/mdev if mdev else np.zeros(len(d))
        return values[np.where(s<m)[0]]
        
    def __find_the_points(self, coords_input, start_point, end_point):
        # The core method for 'snapping' the drawn line portions
        # to the underlying curve
        coords = np.where(coords_input == 0) # get only the 'black' points from the image

        # remove the grid by simply finding outliers in x and y direction
        u_x, c_x = np.unique(coords[0], return_counts=True)
        u_y, c_y = np.unique(coords[1], return_counts=True)

        no_outliers_x = self.__reject_outliers(c_x, u_x)
        no_outliers_y = self.__reject_outliers(c_y, u_y)

        x_keep, y_keep = np.array([]), np.array([])

        for x, y in zip(*coords):
            if x in no_outliers_x and y in no_outliers_y:
                x_keep = np.concat([x_keep, [x]])
                y_keep = np.concat([y_keep, [y]])
        
        coords = [x_keep, y_keep]

        try:
            # impute missing points that will be there from removing the outliers
            slope = (end_point.y() - start_point.y()) / (end_point.x() - start_point.x())
            intercept = end_point.y() - slope * end_point.x()

            squared_distance = np.array([np.power(slope * e + intercept - coords[1][i],2) for i,e in enumerate(coords[0])])
            idxs = squared_distance < 20.
            voltage_all = np.arange(np.min(coords[0]), np.max(coords[0]))
            missing = np.array(list(set(voltage_all).difference(coords[0])))
            current_inter = np.interp(missing, coords[0][idxs], coords[1][idxs])

            # take the average of the points that were the closest to the drawn line segment
            data = pd.DataFrame({'voltage': np.concat([coords[0][idxs], missing]), 'current': np.concat([coords[1][idxs], current_inter])}).groupby('voltage').mean().reset_index().values.T#.plot.scatter(x='voltage', y='current')
            return [data[0], data[1]]
        except:
            print('\n-------\n')
            # print(start_point, end_point)
            # print(slope, intercept)
            # print(missing, coords[0][idxs], coords[1][idxs], coords, idxs, squared_distance)
            print('\n-------\n')

            return coords

    
    def __prepare_full_line(self, points):
        x = np.concat([e[0] for e in points])
        y = np.concat([e[1] for e in points])
        _min, _max = np.min(x), np.max(x)
        
        missing = sorted(set(range(int(_min), int(_max) + 1)).difference(x))
        
        x_app, y_app = np.array([]), np.array([])
        
        for num in missing:
            inferred = np.round((np.interp(num, x, -y)))
            x_app = np.append(x_app, num)
            y_app = np.append(y_app, -inferred)

        x = np.concat([x, x_app])
        y = np.concat([y, y_app])

        return x, y