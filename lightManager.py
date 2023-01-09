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

def getDock(name = "LightManager"):
    '''
    Creates a docked window using Qt and returns the id
    Args:
        name:

    Returns:

    '''
    deleteDock(name)
    ctrl = pym.workspaceControl(name,dockToMainWindow=('right',1),label='Light Manager')
    qtCtrl = omUI.MQtUtil_findControl(ctrl)
    ptr = wrapInstance(int(qtCtrl),Qt.QtWidgets.QWidget)
    return ptr

def deleteDock(name="LightManager"):
    '''
    This function deletes window if it exists.
    Args:
        name: The name of the window to be deleted.

    Returns:

    '''
    if(pym.workspaceControl(name,query=True,exists=True)):
        pym.deleteUI(name)

class LightManager(Qt.QtWidgets.QWidget):

    #dictionary of light types to create light
    lightTypes ={
        "Point Light":pym.pointLight,
        "Spot Light":pym.spotLight,
        "Directional Light":pym.directionalLight,
        "Area Light":partial(pym.shadingNode,'areaLight',asLight=True),
        "Volume Light":partial(pym.shadingNode,'volumeLight',asLight=True),
        "Ambient Light":pym.ambientLight
    }


    def __init__(self,dock=True):

        # create window and UI
        if(dock):
            parent = getDock() #get window

        else:
            deleteDock()

            try:
                pym.deleteUI('LightManager')
            except:
                print("No previous UI found.")

            parent = Qt.QtWidgets.QDialog(parent = getMayaMainWindow())
            parent.setObjectName('Light_Manager')
            parent.setWindowTitle('Light Manager')
            layout = Qt.QtWidgets.QVBoxLayout(parent)


        super(LightManager,self).__init__(parent=parent)

        self.buildUI()
        self.populateUI()

        self.parent().layout().addWidget(self)

        if (not dock):
            parent.show()

    def buildUI(self):
        '''
        This function builds the UI structure.
        Returns:

        '''

        layout = Qt.QtWidgets.QGridLayout(self)
        
        
        self.lightTypeCB = Qt.QtWidgets.QComboBox() #create a combo box for light types

        for lightType in sorted(self.lightTypes):
            self.lightTypeCB.addItem(lightType) #populate combo box
            
        layout.addWidget(self.lightTypeCB, 0, 0, 1, 2)

        createBtn = Qt.QtWidgets.QPushButton('Create Light')
        createBtn.clicked.connect(self.createLight)
        layout.addWidget(createBtn, 0, 2)

        #scrollWidget for lights in the scene
        scrollWidget = Qt.QtWidgets.QWidget()
        scrollWidget.setSizePolicy(Qt.QtWidgets.QSizePolicy.Maximum, Qt.QtWidgets.QSizePolicy.Maximum)
        self.scrollLayout = Qt.QtWidgets.QVBoxLayout(scrollWidget)

        scrollArea = Qt.QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(scrollWidget)

        layout.addWidget(scrollArea, 1, 0, 1, 3)

        saveBtn = Qt.QtWidgets.QPushButton("Save Preset")
        layout.addWidget(saveBtn, 2, 0)
        saveBtn.clicked.connect(self.savePreset)

        importBtn = Qt.QtWidgets.QPushButton('Import Preset')
        layout.addWidget(importBtn, 2, 1)
        importBtn.clicked.connect(self.importLights)

        refreshBtn = Qt.QtWidgets.QPushButton("Refresh")
        refreshBtn.clicked.connect(self.populateUI)
        layout.addWidget(refreshBtn, 2, 2)


    def populateUI(self):
        '''
        This function populates the scroll widget with the lights in the scene.
        Returns:

        '''
        
        while self.scrollLayout.count():
            widget = self.scrollLayout.takeAt(0).widget()
            
            if (widget):
                widget.setVisible(False)
                widget.deleteLater()

        for light in pym.ls(type=("areaLight", "pointLight", "volumeLight", "directionalLight",
                                  "spotLight","ambientLight")): #find light type in the scene
            self.addLight(light) #add light in the widget


    def createLight(self, lightType = None,add=True):
        '''
        This function creates the light when the user clicks create light.
        Args:
            lightType: 
            add: 

        Returns:

        '''
        
        if not lightType:
            lightType = self.lightTypeCB.currentText() #light type from combo box
        func = self.lightTypes[lightType] 

        light = func()
        
        if add:
            self.addLight(light)
        return light


    def addLight(self, light):
        '''
        This function adds the provided light as a widget in the scroll widget.
        Args:
            light: 

        Returns:

        '''
        
        widget = LightWidget(light) #creates widget using the light provided
        self.scrollLayout.addWidget(widget)
        
        widget.onSolo.connect(self.onSolo) #connect solo variable to the widget
        

    def onSolo(self,value):
        '''
        This function isolates the light by disabling the remaining lights.
        Args:
            value: 

        Returns:

        '''
        
        lightWidgets = self.findChildren(LightWidget) #all the light widgets in the scene
        
        for widget in lightWidgets:
            if widget != self.sender(): #if the widget is not the sender of the onsolo message disable it
                widget.disableLight(value)


    def savePreset(self):
        '''
        This function allows the user to save the lighting setup as a preset as a external json file.
        Returns:

        '''
        
        if self.findChildren(LightWidget) == []: #no lights in the scene as no widgets
            cmds.warning("The scene has no lights. Please add lights to create a preset.")
            return
        
        properties = {}
        #store all lights properties
        for lightWidget in self.findChildren(LightWidget):
            light = lightWidget.light
            transform = light.getTransform()
            
            properties[str(transform)] = {
                'translate':list(transform.translate.get()),
                'rotation': list(transform.rotate.get()),
                'lightType':pym.objectType(light),
                'intensity':light.intensity.get(),
                'color':light.color.get()
            }

        lightFile = Qt.QtWidgets.QFileDialog().getSaveFileName(self,'Save lighting preset',
                                                               'lightfile_{}.json'.format(time.strftime('%m%d%H')),
                                                               'JSON files (*.json)')[0] #the file selected by the user

        if(lightFile == ''):
            cmds.error("No file selected. Please select a file")
            return

        with(open(lightFile,'w') as f):
            json.dump(properties,f,indent=4)
        print('Saving file to %s' %lightFile)


    def importLights(self):
        '''
        This function imports the lighting setup from the selected file preset.
        Returns:

        '''
        
        #select the file to get setup
        lightFile = Qt.QtWidgets.QFileDialog().getOpenFileName(self,"Open lighting preset",'','JSON files (*.json)')[0]
        
        if (lightFile == ''):
            cmds.error("No file selected. Please select a file")
            return
        
        try:
            with(open(lightFile,'r',encoding='utf-8') as f):
                properties = json.load(f)
            
            #get light type from file
            for light,info in properties.items():
                lightType = info.get('lightType')
                for selected_lightType in self.lightTypes:
                    if '{}light'.format(selected_lightType.split()[0].lower()) == lightType.lower():
                        break
                else:
                    print(("Corresponding light type not found for the light"))
                    continue

                light = self.createLight(lightType=selected_lightType)
                print("Added  " + selected_lightType)

                #set light properties
                light.intensity.set(info.get('intensity'))

                light.color.set(info.get('color'))

                transform = light.getTransform()
                transform.translate.set(info.get('translate'))
                transform.rotate.set(info.get('rotation'))

                self.populateUI() #populate the light widget

        except:
            cmds.error("The file " + lightFile + " is corrupted.") #incase a json file is selected with corrupted data


#the single light widget
class LightWidget(Qt.QtWidgets.QWidget):

    onSolo = Signal(bool)

    def __init__(self,light):
        super(LightWidget, self).__init__()

        if isinstance(light,str):
            light = pym.PyNode(light)

        if isinstance(light,pym.nodetypes.Transform):
            light = light.getShape() #get the light reference

        self.light = light
        self.buildUI()


    def buildUI(self):
        '''
        This function builds the widget with information and buttons
        Returns:

        '''

        layout = Qt.QtWidgets.QGridLayout(self)
        self.name = Qt.QtWidgets.QCheckBox(str(self.light.getTransform()))
        self.name.setChecked(self.light.visibility.get())

        self.name.toggled.connect(lambda val: self.light.getTransform().visibility.set(val)) #option to disable light
        layout.addWidget(self.name, 0, 0)

        soloBtn = Qt.QtWidgets.QPushButton('Solo') #option to isolate the light
        soloBtn.setCheckable(True)
        soloBtn.toggled.connect(lambda val: self.onSolo.emit(val))
        layout.addWidget(soloBtn, 0, 1)

        deleteBtn = Qt.QtWidgets.QPushButton('Delete') #option to delete light from scene
        deleteBtn.clicked.connect(self.deleteLight)
        deleteBtn.setMaximumWidth(50)
        layout.addWidget(deleteBtn, 0, 2)

        intensity = Qt.QtWidgets.QSlider(Qt.QtCore.Qt.Horizontal) #intensity slider
        intensity.setMinimum(1)
        intensity.setMaximum(1000)

        intensity.setValue(self.light.intensity.get())
        intensity.valueChanged.connect(lambda val: self.light.intensity.set(val))
        layout.addWidget(intensity, 1, 0, 1, 2)

        self.colorBtn = Qt.QtWidgets.QPushButton() #color of the light
        self.colorBtn.setMaximumWidth(20)
        self.colorBtn.setMaximumHeight(20)

        self.setButtonColor()
        self.colorBtn.clicked.connect(self.setColor)
        layout.addWidget(self.colorBtn, 1, 2)


    def deleteLight(self):
        '''
        This function deletes the light from the scene as well as the widget.
        Returns:

        '''

        self.setParent(None)
        self.setVisible(False)
        self.deleteLater()

        pym.delete(self.light.getTransform())


    def setColor(self):
        '''
        This function sets the color of the light.
        Returns:

        '''

        lightColor = self.light.color.get()
        color = pym.colorEditor(rgbValue=lightColor)
        r, g, b, a = [float(x) for x in color.split()]
        color = (r, g, b)

        self.light.color.set(color)
        self.setButtonColor(color)


    def setButtonColor(self,color=None):
        '''
        This function sets the color of the button as the color of the light.
        Args:
            color:

        Returns:

        '''

        if not color:
            color = self.light.color.get()

        assert len(color)==3,"Colors not provided"
        r,g,b = [c*255 for c in color]

        self.colorBtn.setStyleSheet('background-color:rgba(%s, %s,%s,1.0)' %(r,g,b))

    def disableLight(self,value):
        '''
        This function disables the light.
        Args:
            value:

        Returns:

        '''
        self.name.setChecked(not value)

lightManager = LightManager ()
