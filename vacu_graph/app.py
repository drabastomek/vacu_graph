import os
import sys

# Get the absolute path of the current script
# This is needed for pyinstaller to resolve he imports
_current_script_path = os.path.abspath(__file__)
_vac_dir = os.path.dirname(_current_script_path)
_project_root = os.path.dirname(_vac_dir)

if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from PySide6.QtWidgets import (
    QApplication
)

from vacu_graph.drawing.drawing import DrawingApp

def main():
    app = QApplication(sys.argv)
    window = DrawingApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()