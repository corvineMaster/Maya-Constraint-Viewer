import sys

from PySide2 import QtGui
from PySide2 import QtWidgets

from shiboken2 import wrapInstance

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya import cmds, mel, OpenMayaUI as omui


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

    
class constraintViewer(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    dialog_instance = None
    constraints = {
        'Parent': 'parentConstraint', 
        'Point': 'pointConstraint',  
        'Orient': 'orientConstraint', 
        'Scale': 'scaleConstraint',
        'Aim': 'aimConstraint', 
        'Pole Vector': 'poleVectorConstraint', 
        'Point On Poly': 'pointOnPolyConstraint', 
        'Geometry': 'geometryConstraint', 
        'Normal': 'normalConstraint', 
        'Tangent': 'tangentConstraint'
        }
        
    @classmethod
    def show_dialog(cls):
        if not cls.dialog_instance:
            cls.dialog_instance = constraintViewer()
        
        if cls.dialog_instance.isHidden():
            cls.dialog_instance.show()
        else:
            cls.dialog_instance.raise_()
            cls.dialog_instance.activateWindow()
        
    def __init__(self, parent=maya_main_window()):
        super(constraintViewer, self).__init__(parent)

        self.setWindowTitle("Show Constraints")
        self.setMinimumWidth(260)

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        
        if cmds.ls(selection=True):
            self.search_bar_field.setText(cmds.ls(selection=True)[0])
        self.refresh_filtered_item_tree()

    def create_widgets(self):
        self.search_filters_dropdown = QtWidgets.QToolBox()
        self.search_bar_field = QtWidgets.QLineEdit()
        self.search_bar_field.setMaximumHeight(25)
        self.search_bar_field.setPlaceholderText('Search')
        self.get_selection_button = QtWidgets.QPushButton()
        self.get_selection_button.setIcon(QtGui.QIcon(':searchEngine.png'))
        self.get_selection_button.setToolTip('Filter based on selection')
        self.constraint_type_comboBox = QtWidgets.QComboBox()
        self.constraint_type_comboBox.addItem('All')
        self.constraint_type_comboBox.addItems(self.constraints.keys())
        self.refresh_button = QtWidgets.QPushButton()
        self.refresh_button.setMaximumWidth(30)
        self.refresh_button.setIcon(QtGui.QIcon(":refresh.png"))
        self.refresh_button.setToolTip('Refreshes the list')
        self.filtered_item_tree = QtWidgets.QTreeWidget()
        self.filtered_item_tree.setHeaderHidden(True)
        self.constraint_options_button = QtWidgets.QPushButton('Options')
        self.constraint_options_button.setEnabled(False)
        options_tool_tip = 'Opens the options window for the constraint currently selected in the drop down box.'
        self.constraint_options_button.setToolTip(options_tool_tip)
        
    def create_layout(self):
        search_layout = QtWidgets.QHBoxLayout()
        search_layout.addWidget(self.search_bar_field)
        search_layout.addWidget(self.get_selection_button)
        
        combo_refresh_layout = QtWidgets.QHBoxLayout()
        combo_refresh_layout.addWidget(self.constraint_type_comboBox)
        combo_refresh_layout.addWidget(self.refresh_button)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(search_layout)
        main_layout.addLayout(combo_refresh_layout)
        main_layout.addWidget(self.filtered_item_tree)
        main_layout.addWidget(self.constraint_options_button)

    def create_connections(self):
        self.get_selection_button.clicked.connect(self.populate_text_from_selection)
        self.constraint_options_button.clicked.connect(self.open_constraint_option_box)
        self.constraint_type_comboBox.currentTextChanged.connect(self.toggle_options_button)
        self.constraint_type_comboBox.currentTextChanged.connect(self.refresh_filtered_item_tree)
        self.refresh_button.clicked.connect(self.refresh_filtered_item_tree)
        self.filtered_item_tree.doubleClicked.connect(self.select_tree_item_in_outliner)
        self.search_bar_field.textChanged.connect(self.refresh_filtered_item_tree)
    
    def populate_text_from_selection(self):
        selection = cmds.ls(selection=True)
        if selection:
            self.search_bar_field.setText(selection[0])
    
    def toggle_options_button(self):
        self.constraint_options_button.setEnabled(True)
        if self.constraint_type_comboBox.currentText() == 'All':
            self.constraint_options_button.setEnabled(False)
        
    def select_tree_item_in_outliner(self):
        selection = self.filtered_item_tree.selectedItems()
        if selection:
            cmds.select(selection[0].text(0))
        
    def open_constraint_option_box(self):
        selection = self.constraint_type_comboBox.currentText().replace(' ', '')
        mel.eval(f'{selection}ConstraintOptions;')
    
    def refresh_filtered_item_tree(self):
        self.filtered_item_tree.clear()
        
        objs = []
        constraint_type = self.constraint_type_comboBox.currentText()
        if constraint_type == 'All':
            for constraint_command in self.constraints.values():
                objs = objs + (cmds.ls(type=constraint_command) or [])
        else:
            objs = cmds.ls(type=self.constraints[constraint_type]) or []
        
        search_bar_text = self.search_bar_field.text()
        for constraint in objs:
            parents = list(set(cmds.listConnections(f'{constraint}.target')))
            targets = list(set(cmds.listConnections(constraint, source=False, destination=True)))
            if constraint in parents:
                parents.remove(constraint)
            if constraint in targets:
                targets.remove(constraint)
            
            for target in targets:
                if cmds.nodeType(target) != 'transform':
                    continue
                target_valid = False
                
                target_item = QtWidgets.QTreeWidgetItem(None, [target])
                if search_bar_text in target_item.text(0):
                    target_valid = True
                    
                constraint_item = QtWidgets.QTreeWidgetItem(target_item, [constraint])
                constraint_item.setForeground(0, QtGui.QColor('green'))
                if search_bar_text in constraint_item.text(0):
                    target_valid = True
                
                for parent in parents:
                    parent_item = QtWidgets.QTreeWidgetItem(target_item, [parent])
                    if search_bar_text in parent_item.text(0):
                        target_valid = True
                
                if target_valid:
                    self.filtered_item_tree.insertTopLevelItems(0, [target_item])


if __name__ == "__main__":
    try:
        constraint_viewer_window.close()
        constraint_viewer_window.deleteLater()
    except:
        pass

    constraint_viewer_window = constraintViewer()
    constraint_viewer_window.show()
