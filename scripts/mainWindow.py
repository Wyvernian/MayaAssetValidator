from maya import cmds
from maya import OpenMayaUI as omui

from shiboken2 import wrapInstance
from PySide2 import QtWidgets, QtCore
import MayaAssetValidator.scripts.validator

# ENV/NAMED VARIABLES
WINDOW_TITLE = "Maya Asset Validator"
WORKSPACE_CONTROL_NAME = "MayaAssetValidatorWorkspaceControl"
UI_OBJECT_NAME = "MayaAssetValidatorWidget"


def get_maya_main_window():
    ptr = omui.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapInstance(int(ptr), QtWidgets.QWidget)
    return None


def delete_existing_workspace_control():
    if cmds.workspaceControl(WORKSPACE_CONTROL_NAME, exists=True):
        cmds.deleteUI(WORKSPACE_CONTROL_NAME)


def delete_existing_widget():
    existing = QtWidgets.QApplication.instance().findChild(QtWidgets.QWidget, UI_OBJECT_NAME)
    if existing is not None:
        existing.setParent(None)
        existing.deleteLater()

# Collapsable Widget
class CollapsibleSection(QtWidgets.QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)

        self.toggle_button = QtWidgets.QToolButton(text=title, checkable=True, checked=True)
        self.toggle_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(QtCore.Qt.DownArrow)

        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 5, 10, 5)

        self.toggle_button.toggled.connect(self.on_toggled)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.toggle_button)
        main_layout.addWidget(self.content_widget)

    def on_toggled(self, checked):
        self.content_widget.setVisible(checked)
        self.toggle_button.setArrowType(QtCore.Qt.DownArrow if checked else QtCore.Qt.RightArrow)

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

# Main Window Widget
class MyDockWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName(UI_OBJECT_NAME)

        self.setWindowTitle(WINDOW_TITLE)

        root_layout = QtWidgets.QVBoxLayout(self)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(8)

        tabs = QtWidgets.QTabWidget()

        # --- Tab 1: Main ---
        tab_main = QtWidgets.QWidget()
        tab_main_layout = QtWidgets.QVBoxLayout(tab_main)

        info_label = QtWidgets.QLabel("This is a dockable PySide2 window for Maya 2024.")
        info_label.setWordWrap(True)
        tab_main_layout.addWidget(info_label)

        name_row = QtWidgets.QHBoxLayout()
        name_row.addWidget(QtWidgets.QLabel("Name:"))
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("Enter a name")
        name_row.addWidget(self.name_edit)
        tab_main_layout.addLayout(name_row)

        self.run_button = QtWidgets.QPushButton("Run Action")
        self.run_button.clicked.connect(self.on_run_clicked)
        tab_main_layout.addWidget(self.run_button)

        tab_main_layout.addStretch()
        tabs.addTab(tab_main, "Main")

        # --- Tab 2: Options ---
        tab_options = QtWidgets.QWidget()
        tab_options_layout = QtWidgets.QVBoxLayout(tab_options)

        self.option_a = QtWidgets.QCheckBox("Enable option A")
        self.option_b = QtWidgets.QCheckBox("Enable option B")
        tab_options_layout.addWidget(self.option_a)
        tab_options_layout.addWidget(self.option_b)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        tab_options_layout.addWidget(QtWidgets.QLabel("Strength:"))
        tab_options_layout.addWidget(self.slider)

        tab_options_layout.addStretch()
        tabs.addTab(tab_options, "Options")

        # --- Tab 3: Advanced / collapsible ---
        tab_advanced = QtWidgets.QWidget()
        tab_advanced_layout = QtWidgets.QVBoxLayout(tab_advanced)

        section = CollapsibleSection("Advanced Settings")
        section.add_widget(QtWidgets.QLabel("Example advanced field 1"))
        section.add_widget(QtWidgets.QLineEdit())
        section.add_widget(QtWidgets.QLabel("Example advanced field 2"))
        section.add_widget(QtWidgets.QSpinBox())

        tab_advanced_layout.addWidget(section)
        tab_advanced_layout.addStretch()
        tabs.addTab(tab_advanced, "Advanced")

        root_layout.addWidget(tabs)

        bottom_row = QtWidgets.QHBoxLayout()
        self.status_label = QtWidgets.QLabel("Ready.")
        bottom_row.addWidget(self.status_label)
        bottom_row.addStretch()

        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.close)
        bottom_row.addWidget(close_btn)

        root_layout.addLayout(bottom_row)

    def on_run_clicked(self):
        name = self.name_edit.text().strip() or "Unnamed"
        enabled = []
        if self.option_a.isChecked():
            enabled.append("A")
        if self.option_b.isChecked():
            enabled.append("B")

        strength = self.slider.value()
        cmds.warning("Run clicked: name={}, options={}, strength={}".format(name, enabled, strength))
        self.status_label.setText("Last run: {}".format(name))


def create_dockable_window():
    delete_existing_workspace_control()
    delete_existing_widget()

    cmds.workspaceControl(
        WORKSPACE_CONTROL_NAME,
        label=WINDOW_TITLE,
        dockToMainWindow=("right", 1),
        retain=True,
        floating=False,
        initialWidth=380,
        initialHeight=300
    )

    control_ptr = omui.MQtUtil.findControl(WORKSPACE_CONTROL_NAME)
    if not control_ptr:
        return

    control_widget = wrapInstance(int(control_ptr), QtWidgets.QWidget)

    layout = control_widget.layout()
    if layout is None:
        layout = QtWidgets.QVBoxLayout(control_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    widget = MyDockWidget(parent=control_widget)
    layout.addWidget(widget)


def restore_dockable_window():
    """
    Use this for Maya workspaceControl restore callbacks if needed.
    """
    create_dockable_window()


def show_window():
    create_dockable_window()
