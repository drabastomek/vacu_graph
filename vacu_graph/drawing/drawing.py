import sys
import numpy as np 
from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout,
    QWidget, QFileDialog, QLabel, QHBoxLayout,
    QLineEdit, QLineEdit
)
# from PyQt5.QtGui import QPainter, QPen, QPixmap, QImage
# from PyQt5.QtCore import Qt, QPoint

import pandas as pd

from vacu_graph.image_viewer.image_viewer import ImageViewerWidget
from vacu_graph.dialogs.dialogs import ExceptionDialog

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