import sys
import numpy as np 
from PyQt6.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout,
    QWidget, QFileDialog, QLabel, QHBoxLayout,
    QLineEdit, QLineEdit#, QApplication, QAction
)
# from PyQt5.QtGui import QAction

import matplotlib.pyplot as plt

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

        tube_max_diss_label = QLabel(self)
        tube_max_diss_label.setText('Plate max (W):')
        self.tube_max_diss = QLineEdit(self)

        tube_max_diss_layout = QHBoxLayout()
        tube_max_diss_layout.addWidget(tube_max_diss_label)
        tube_max_diss_layout.addWidget(self.tube_max_diss)

        plate_voltage_conf_label = QLabel(self)
        plate_voltage_conf_label.setText('Voltage resolution:')
        self.plate_voltage_resolution = QLineEdit(self)

        plate_voltage_layout = QHBoxLayout()
        plate_voltage_layout.addWidget(plate_voltage_conf_label)
        plate_voltage_layout.addWidget(self.plate_voltage_resolution)

        configuration_layout = QHBoxLayout()
        configuration_layout.addLayout(tube_type_layout)
        configuration_layout.addLayout(tube_max_diss_layout)
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

        # self.__createMenu()

    def load_image(self):
        self.img_size = self.viewer.load_image()
        self.resize(self.img_size)

    def annotate_axes(self):
        self.viewer.annotate_axes()
        
    def annotate_line(self):
        self.viewer.annotate_line()

    def save_annotations(self):
        curves = self.viewer.get_curves()

        if (
            self.tube_type_input.text() == '' or 
            self.plate_voltage_resolution.text() == '' or
            self.tube_max_diss == ''
        ):
            ExceptionDialog(message='Tube type, max plate dissipatio, and resolution fileds need to be defined.')
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

            # save data
            full.to_csv(f'{self.output_dir}/{tube_type}-hi_res.csv', index=False)
            grouped.to_csv(f'{self.output_dir}/{tube_type}-agg.csv', index=False)

            # plot the chart and save
            self.__plot_curves(grouped)

    def __plot_curves(self, df_input):
        def find_nearest_point(df, target_value):
            df.reset_index(inplace=True, drop=True)
            abs_difference = abs(df['voltage'] - target_value)
            closest_index = abs_difference.idxmin()
            closest_row = df.iloc[closest_index]

            return closest_row['current']
        
        # prepare max dissipation curve
        max_plate_dissipation = float(self.tube_max_diss.text())

        df_max_dissipation = df_input[['voltage']].drop_duplicates().reset_index(drop=True)
        df_max_dissipation['max_dissipation'] = max_plate_dissipation / df_max_dissipation['voltage'] * 1000
        df_max_dissipation = df_max_dissipation.loc[df_max_dissipation['voltage'] > 0]
        df_max_dissipation = df_max_dissipation.sort_values(by='voltage')

        # get the axes limits
        axes = self.viewer.get_axes()
        x_lim, y_lim = axes['Plate voltage'][0], axes['Plate current'][0]

        # generate the plot
        _, ax = plt.subplots(figsize=(12,9), squeeze=True) 
        for label, df in df_input.groupby('line'):
            df.plot(
                x='voltage', 
                y='current', 
                ax=ax, 
                label=label, 
                xlim=x_lim, 
                ylim=y_lim, 
                title=self.tube_type_input.text(), 
                ylabel='current (mA)', 
                c='black'
            )
            label_x_position = df.max()['voltage']
            label_y_position = find_nearest_point(df, label_x_position)
            ax.annotate(xy=(0, 0), xytext=(label_x_position, label_y_position), text=label)

        df_max_dissipation.plot(x='voltage', y='max_dissipation', ax=ax, c='r')

        # add grid lines
        plt.grid(True, which='major', linestyle='-', color='black', alpha=0.5)
        plt.grid(True, which='minor', linestyle=':', color='gray', alpha=0.3)
        plt.minorticks_on()
        plt.tight_layout()

        # save the plot
        plt.savefig(f'{self.output_dir}/{self.tube_type_input.text()}.png', dpi=300)

    # def __createMenu(self):
    #     exitAct = QAction('&Exit', self)
    #     exitAct.setShortcut('Ctrl+Q')
    #     exitAct.setStatusTip('Exit application')
    #     exitAct.triggered.connect(QApplication.instance().quit)

    #     menuBar = self.menuBar()
    #     fileMenu = menuBar.addMenu("&Files")
    #     fileMenu.addAction(exitAct)
    #     menuBar.setNativeMenuBar(True)

    #     print('dupa')