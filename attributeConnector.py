import time
import pymel.core as pym
import os
from functools import partial
import Qt
from maya import OpenMayaUI as omUI
import json
from maya import cmds


if(Qt.__binding__=='Pyside'):
    #Using Pyside and Shiboken
    from shiboken import wrapInstance
    from Qt.QtCore import Signal

elif(Qt.__binding__.startswith('PyQt')):
    #Using PyQt and Sip
    from sip import wrapinstance as wrapInstance
    from Qt.QtCore import pyqtSignal as Signal

else:
    #Using Pyside2 and Shiboken
    from shiboken2 import wrapInstance
    from Qt.QtCore import Signal


def getMayaMainWindow():
    '''
    This function returns the id of the maya window.
    Returns:

    '''
    win = omUI.MQtUtil_mainWindow()
    ptr = wrapInstance(int(win),Qt.QtWidgets.QMainWindow)

    return ptr


def getDock(name = "AttributeConnector"):
    '''
    Creates a window using Qt and returns the id
    Args:
        name:

    Returns:

    '''
    deleteDock(name) #delete window if existing
    ctrl = pym.workspaceControl(name,dockToMainWindow=('right',1),label='Attribute Connector')

    qtCtrl = omUI.MQtUtil_findControl(ctrl)
    ptr = wrapInstance(int(qtCtrl),Qt.QtWidgets.QWidget)

    return ptr


def deleteDock(name="AttributeConnector"):
    '''
    This function deletes window if it exists.
    Args:
        name:

    Returns:

    '''
    if(pym.workspaceControl(name,query=True,exists=True)):
        pym.deleteUI(name)



class AttributeConnector(Qt.QtWidgets.QWidget):

    def __init__(self,dock=True):

        #create window and UI
        if(dock):
            parent = getDock() #get window

        else:
            deleteDock()

            try:
                pym.deleteUI('AttributeConnector')
            except:
                print("No previous UI found.")

            parent = Qt.QtWidgets.QDialog(parent=getMayaMainWindow())
            parent.setObjectName('Attribute_Connector')
            parent.setWindowTitle('Attribute Connector')
            layout = Qt.QtWidgets.QVBoxLayout(parent)

        super(AttributeConnector, self).__init__(parent=parent)

        #dictionary for driver attributes
        self.driver = {'translateX' : None, 'translateY' : None, 'translateZ' : None,
                       'rotateX' : None, 'rotateY' : None, 'rotateZ' : None,
                       'scaleX' : None, 'scaleY' : None, 'scaleZ' : None,
                       'other' : None }

        #list for driven objects
        self.driven_objects = []

        #driver object
        self.driver_object = None


        self.buildUI()


        self.parent().layout().addWidget(self)

        if (not dock):
            parent.show()


    def buildUI(self):
        '''
        This function builds the UI structure.
        Returns:

        '''

        layout = Qt.QtWidgets.QGridLayout(self)

        #button to select the driver object
        driverBtn = Qt.QtWidgets.QPushButton("Select Driver")
        layout.addWidget(driverBtn, 0, 0)
        driverBtn.clicked.connect(self.selectDriver)

        #selected driver name and attributes
        selected_driver_text = Qt.QtWidgets.QLabel("SELECTED DRIVER :")
        layout.addWidget(selected_driver_text, 1, 0)

        self.driver_text = Qt.QtWidgets.QLabel("")
        layout.addWidget(self.driver_text, 1, 1)

        self.driver['translateX'] = Qt.QtWidgets.QRadioButton("Location X")
        layout.addWidget(self.driver['translateX'], 2, 1)

        self.driver['translateY'] = Qt.QtWidgets.QRadioButton("Location Y")
        layout.addWidget(self.driver['translateY'], 2, 2)

        self.driver['translateZ'] = Qt.QtWidgets.QRadioButton("Location Z")
        layout.addWidget(self.driver['translateZ'], 2, 3)

        self.driver['rotateX'] = Qt.QtWidgets.QRadioButton("Rotation X")
        layout.addWidget(self.driver['rotateX'], 3, 1)

        self.driver['rotateY'] = Qt.QtWidgets.QRadioButton("Rotation Y")
        layout.addWidget(self.driver['rotateY'], 3, 2)

        self.driver['rotateZ'] = Qt.QtWidgets.QRadioButton("Rotation Z")
        layout.addWidget(self.driver['rotateZ'], 3, 3)

        self.driver['scaleX'] = Qt.QtWidgets.QRadioButton("Scale X")
        layout.addWidget(self.driver['scaleX'], 4, 1)

        self.driver['scaleY'] = Qt.QtWidgets.QRadioButton("Scale Y")
        layout.addWidget(self.driver['scaleY'], 4, 2)

        self.driver['scaleZ'] = Qt.QtWidgets.QRadioButton("Scale Z")
        layout.addWidget(self.driver['scaleZ'], 4, 3)

        self.driver['other'] = Qt.QtWidgets.QRadioButton("Other")
        layout.addWidget(self.driver['other'], 5, 1)

        self.other_attr = Qt.QtWidgets.QLineEdit()
        layout.addWidget(self.other_attr, 5, 2, 1, 2)


        #button to select driven object
        addDrivenBtn = Qt.QtWidgets.QPushButton('Add Driven Object')
        addDrivenBtn.clicked.connect(self.appendDriven)
        layout.addWidget(addDrivenBtn, 6, 1)

        #add driven objects and attributes panel
        scrollWidget = Qt.QtWidgets.QWidget()
        scrollWidget.setSizePolicy(Qt.QtWidgets.QSizePolicy.Maximum, Qt.QtWidgets.QSizePolicy.Maximum)
        self.scrollLayout = Qt.QtWidgets.QVBoxLayout(scrollWidget)

        scrollArea = Qt.QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(scrollWidget)
        layout.addWidget(scrollArea, 7, 0, 1, 4)

        while self.scrollLayout.count():
            widget = self.scrollLayout.takeAt(0).widget()
            if (widget):
                widget.setVisible(False)
                widget.deleteLater()




    def selectDriver(self):
        '''
        This function selects the selected object as the driver
        Returns:

        '''

        selection = cmds.ls(sl=True)
        if (len(selection) != 1):
            cmds.warning("Please select one object only")
        else:
            self.driver_object = selection[0]

        self.driver_text.setText(self.driver_object)

    def connectAttributes(self):
        '''
        This functions connects the selected driven attribute to the select driver attribute.
        Returns:

        '''
        #get the selected attribute from radiobox
        self.driver_attr = None
        for attr, driver in self.driver.items():
            if(driver.isChecked() == True):
                self.driver_attr = attr


        #if other get text
        if (self.driver_attr == "other"):
            self.driver_attr = self.other_attr.text()
            #if text field is empty
            if (self.driver_attr == ""):
                cmds.error("Please type the attribute name or select from the above options")

        #concat with driver object. If none selected throw error
        if self.driver_object == None:
            cmds.error("Please select a driver object. No driver selected.")
        elif self.driver_attr == None:
            cmds.error("Please select a driver attribute.")
        else:
            self.driver_attr = self.driver_object + '.' + self.driver_attr


    def appendDriven(self):
        '''
        This function creates a widget for selected driven object to select attributes
        Returns:

        '''

        selection = cmds.ls(sl=True) #get selected objects

        for object in selection:
            if object in self.driven_objects: #if object is already present in list
                continue

            self.driven_objects.append(object) #append in list

            widget = AppendWidget(object, self)
            self.scrollLayout.addWidget(widget)

            widget.deleteSelected.connect(self.deleteSelected) #providing option for deleting

    def deleteSelected(self, val):
        '''
        Delete the selected driven object from list to avoid repetition
        Args:
            val:

        Returns:

        '''
        self.driven_objects.remove(val)


    def result(self):
        '''

        Returns: This function returns the name of the driver and the attribute

        '''
        self.connectAttributes()
        return (self.driver_attr)




#widget for the driven object
class AppendWidget(Qt.QtWidgets.QWidget):

    deleteSelected = Signal(str)
    result = Signal()

    def __init__(self,object, attributesConnector):

        super(AppendWidget, self).__init__()
        self.object = object
        self.attributesConnector = attributesConnector
        # dictionary for driven attributes
        self.driven = {'translateX': None, 'translateY': None, 'translateZ': None,
                       'rotateX': None, 'rotateY': None, 'rotateZ': None,
                       'scaleX': None, 'scaleY': None, 'scaleZ': None,
                       'other': None}


        self.buildUI()


    def buildUI(self):
        '''
        This function creates the widget along with the attributes
        Returns:

        '''

        layout = Qt.QtWidgets.QGridLayout(self)

        # selected driven object name and attributes
        self.name = Qt.QtWidgets.QLabel("Object: " + self.object)
        layout.addWidget(self.name, 0, 0, 3, 1)

        self.driven['translateX'] = Qt.QtWidgets.QCheckBox("Location X")
        layout.addWidget(self.driven['translateX'], 0, 1)

        self.driven['translateY'] = Qt.QtWidgets.QCheckBox("Location Y")
        layout.addWidget(self.driven['translateY'], 0, 2)

        self.driven['translateZ'] = Qt.QtWidgets.QCheckBox("Location Z")
        layout.addWidget(self.driven['translateZ'], 0, 3)

        self.driven['rotateX'] = Qt.QtWidgets.QCheckBox("Rotation X")
        layout.addWidget(self.driven['rotateX'], 1, 1)

        self.driven['rotateY'] = Qt.QtWidgets.QCheckBox("Rotation Y")
        layout.addWidget(self.driven['rotateY'], 1, 2)

        self.driven['rotateZ'] = Qt.QtWidgets.QCheckBox("Rotation Z")
        layout.addWidget(self.driven['rotateZ'], 1, 3)

        self.driven['scaleX'] = Qt.QtWidgets.QCheckBox("Scale X")
        layout.addWidget(self.driven['scaleX'], 2, 1)

        self.driven['scaleY'] = Qt.QtWidgets.QCheckBox("Scale Y")
        layout.addWidget(self.driven['scaleY'], 2, 2)

        self.driven['scaleZ'] = Qt.QtWidgets.QCheckBox("Scale Z")
        layout.addWidget(self.driven['scaleZ'], 2, 3)

        self.driven['other'] = Qt.QtWidgets.QCheckBox("Other")
        layout.addWidget(self.driven['other'], 3, 1)

        self.other_attr = Qt.QtWidgets.QLineEdit()
        layout.addWidget(self.other_attr, 3, 2, 1, 2)

        #connect attributes object
        connectBtn = Qt.QtWidgets.QPushButton('Connect Attributes')
        layout.addWidget(connectBtn, 0, 5)
        connectBtn.clicked.connect(self.connectAttrs)
        connectBtn.setMaximumWidth(200)

        # delete driven object
        deleteBtn = Qt.QtWidgets.QPushButton('Remove')
        layout.addWidget(deleteBtn, 2, 5)
        deleteBtn.clicked.connect(self.deleteObject)
        deleteBtn.setMaximumWidth(50)

    def deleteObject(self):
        '''
        This function removes the driven object from the list.
        Returns:

        '''
        self.deleteSelected.emit(self.object)
        self.setParent(None)
        self.setVisible(False)
        self.deleteLater()

    def connectAttrs(self):
        '''
        This function connects the driver attribute to selected driven attribute
        Returns:

        '''
        #get the driver attribute
        driver_attr = AttributeConnector.result(self.attributesConnector)

        # get the selected attribute from checkbox
        self.driven_attr = None
        for attr, driven in self.driven.items():
            if (driven.isChecked() == True):
                self.driven_attr = self.object + '.' + attr
                cmds.connectAttr(driver_attr, self.driven_attr)
                print("Attribute " + self.driven_attr + " connected to " + driver_attr)









