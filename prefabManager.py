from maya import cmds
from Qt import QtWidgets, QtCore, QtGui
import os
import json
import pprint

USERAPPDIR = cmds.internalVar(userAppDir=True) #the maya documents folder
DIRECTORY = os.path.join(USERAPPDIR, "Prefabs") #the folder to store prefabs

if not os.path.exists(DIRECTORY):
    os.mkdir(DIRECTORY) #create if not existing


#class which gets and provides the list of prefabs from the folder
class prefabManager(dict):

    def save(self,name,directory=DIRECTORY,screenshot = True, **info):
        '''
        This function saves the selected items as a prefab.
        Args:
            name: The name of the saved file.
            directory: The directory to save the file.
            screenshot: To take screenshot of the scene as a visual refrence
            **info: the dictionary to store name and path

        Returns:

        '''

        path = os.path.join(directory,'{}.ma'.format(name))  #the saved file stored as .ma maya file
        infoFile = os.path.join(directory,"{}.json".format(name)) #the screenshot, name and path information will be stored here

        info['name']=name
        info['path']=path
        cmds.file(rename=path) #rename file

        #save selected and if not selected then select everything
        if(cmds.ls(selection=True)):
            cmds.file(force=True,type="mayaAscii",exportSelected=True)
        else:
            cmds.file(save=True,type="mayaAscii",force=True)

        if(screenshot):
            info['screenshot'] = self.saveScreenshot(name,directory=directory)

        with open(infoFile,'w') as f:
            json.dump(info,f,indent=4) #writing the dictionary into json

        self[name] = info #the dictionary containing all objects as keys with will all info of the object

    def find(self,directory=DIRECTORY):
        '''
        This function reloads the list of prefabs from the file location
        Args:
            directory:

        Returns:

        '''

        self.clear()

        if not os.path.exists(directory):
            return                      #no directory exist


        files = os.listdir(directory) #files from directory
        mayaFiles = [f for f in files if f.endswith('.ma')] #all maya files

        for ma in mayaFiles:
            name,ext = os.path.splitext(ma)
            path = os.path.join(directory,ma)

            infoFile = "{}.json".format(name)

            if infoFile in files:
                infoFile = os.path.join(directory,infoFile) #get the infofile in folder

                with open(infoFile, 'r') as f:
                    info = json.load(f) #load data

            else:
                info = {}

            screenshot = "{}.jpg".format(name)

            if screenshot in files:
                info['screenshot'] = os.path.join(directory,name)

            info['name']=name
            info['path']=path

            self[name] =info

    def load(self,name):
        '''
        This function loads the provided item.
        Args:
            name:

        Returns:

        '''

        self.find() #reload the dictionary

        path = self[name]['path'] #get the path from the dict
        cmds.file(path,i=True,usingNamespaces=False) #import the asset

    def saveScreenshot(self, name,directory=DIRECTORY):
        '''
        This function saves the screenshot of the scene.
        Args:
            name:
            directory:

        Returns:

        '''
        path = os.path.join(directory,"{}.jpg".format(name)) #get the path

        #save the screenshot
        cmds.viewFit()
        cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
        cmds.playblast (completeFilename = path, forceOverwrite = True, format= 'image',
                        width = 200,height=200,showOrnaments = False,startTime = 1,
                        endTime =1 ,viewer=False)

        return path #return the path of the screenshot



#the UI window
class PrefabUI(QtWidgets.QDialog):
    def __init__(self):
        super(PrefabUI, self).__init__()
        self.setWindowTitle("Prefab Manager")
        self.library = prefabManager() #instance of the library containing info

        self.buildUI()
        self.populate()

    def buildUI(self):
        '''
        This function builds the UI structure of the prefab manager.
        Returns:

        '''

        layout = QtWidgets.QVBoxLayout(self) #vertical box layout

        saveWidget = QtWidgets.QWidget()
        saveLayout = QtWidgets.QHBoxLayout(saveWidget) #horizontal box layout for save option and save name
        layout.addWidget(saveWidget)

        self.saveNameField = QtWidgets.QLineEdit()
        saveLayout.addWidget(self.saveNameField)

        saveBtn = QtWidgets.QPushButton('Save')
        saveBtn.clicked.connect(self.save)
        saveLayout.addWidget(saveBtn)

        #list of saved prefabs
        size = 64
        buffer = 12

        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setViewMode(QtWidgets.QListWidget.IconMode)
        self.listWidget.setIconSize(QtCore.QSize(size,size))

        self.listWidget.setResizeMode(QtWidgets.QListWidget.Adjust)
        self.listWidget.setGridSize(QtCore.QSize(size+buffer,size+buffer))
        layout.addWidget(self.listWidget)

        btnWidget = QtWidgets.QWidget()
        btnLayout = QtWidgets.QHBoxLayout(btnWidget) #button which displays and select
        layout.addWidget(btnWidget)

        importBtn = QtWidgets.QPushButton("Import") #button to import the selected prefab
        importBtn.clicked.connect(self.load)
        btnLayout.addWidget(importBtn)

        refreshBtn = QtWidgets.QPushButton("Refresh") #button to refresh the prefab list
        refreshBtn.clicked.connect(self.populate)
        btnLayout.addWidget(refreshBtn)

        closeBtn = QtWidgets.QPushButton("Close") #close the dialog
        closeBtn.clicked.connect(self.close)
        btnLayout.addWidget(closeBtn)

    def populate(self):
        '''
        This function populates the list widget with the prefabs.
        Returns:

        '''

        self.listWidget.clear() #empty the list widget
        self.library.find() #reload the list from the folder

        #load the items in the list
        for name, info in self.library.items():
            item = QtWidgets.QListWidgetItem(name)
            self.listWidget.addItem(item)

            screenshot = info.get('screenshot')
            if screenshot:
                icon = QtGui.QIcon(screenshot)
                item.setIcon(icon)

            item.setToolTip(pprint.pformat(info))

    def load(self):
        '''
        This function loads the selected prefab into the scene.
        Returns:

        '''
        currentItem = self.listWidget.currentItem() #selected item
        if not currentItem:
            return

        name = currentItem.text()
        self.library.load(name)


    def save(self):
        '''
        This function saves the selected item as a prefab
        Returns:

        '''

        name = self.saveNameField.text() #name from save text field

        if not name.strip():
            cmds.warning("Name field empty.")
            return

        self.library.save(name)
        self.populate()
        self.saveNameField.setText('')


UI = PrefabUI()
UI.show()