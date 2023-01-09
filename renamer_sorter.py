from maya import cmds

class Organizer ():

    def __init__(self):

        #groups created for prefixes and suffixes
        self.groups = {
            "mesh":"geo",
            "nurbsSurface":"nurbs",
            "joint":"jnt",
            "camera": "cam",
            "ambientLight":"lgt",
            "directionalLight" : "lgt",
            "pointLight":"lgt",
            "spotLight":"lgt",
            "volumeLight":"lgt",
            "areaLight":"lgt"
        }

        #default suffix/prefix
        self.default = "grp"

        #global variables
        self.window = None
        self.renamer_frame = None
        self.sorter_frame = None

        self.word = None
        self.rename_col = None
        self.folders_col = None

        #name of radiobox
        self.radio_object_type = 'By object type'
        self.radio_suffix_type = "Make groups by suffix"

        self.UI()

    def UI(self):
        '''
        This function creates the UI.
        Returns:

        '''

        #create window
        win = 'RenamerSorter'
        if (cmds.window(win, exists=True)):
            cmds.deleteUI(win)
        self.window = cmds.window(win, rtf=True, nde = True,  w=490, h= 490, t=win, s=False)

        # create main layout
        main_layout = cmds.columnLayout(width=503, height= 490, adj = True)
        
        #Frame UI for renaming
        self.renamer_frame = cmds.frameLayout(label='Renamer', width=490, height=230, collapsable=True,
                                collapseCommand=lambda: self.collapse_cmd(self.renamer_frame, 230),
                                expandCommand=lambda: self.expand_cmd(self.renamer_frame, 230))

        cmds.text(l="Select the objects you want to add prefix/suffix or all objects will be considered.\n"
                    "You can either add prefix/suffix based on the object's type or provide a word.",
                  fn="boldLabelFont", h=40)
        cmds.separator(style="none", h=10)
        cmds.rowColumnLayout(nc=4)


        self.rename_col = cmds.radioCollection(numberOfCollectionItems=2)
        rename_type = cmds.radioButton(label = self.radio_object_type)

        cmds.separator(style="none", w = 100)
        rename_word = cmds.radioButton(label = 'By this word')

        cmds.radioCollection(self.rename_col, edit=True, select=rename_type)
        self.word = cmds.textField(w = 100)

        cmds.setParent('..')
        cmds.separator(style="none", h=20)

        cmds.rowColumnLayout(nc=4)
        cmds.separator(style="none", w = 50)

        cmds.button(l = "ADD PREFIX", w = 150 , c = lambda x : self.Rename(addPrefix = True) )
        cmds.separator(style="none", w=50)
        cmds.button(l = "ADD SUFFIX", w = 150 , c = lambda x : self.Rename(addPrefix = False))
        
        cmds.setParent('..')
        cmds.separator(hr=True, style="none", h=50)
        
        #Frame UI for sorting
        self.sorter_frame = cmds.frameLayout(label='Sorter', width=490, height=230, collapsable=True,
                                collapseCommand=lambda: self.collapse_cmd(self.sorter_frame, 230),
                                expandCommand=lambda: self.expand_cmd(self.sorter_frame, 230), parent = self.window)
        cmds.separator(style="none", h=20)

        cmds.text(l="This will sort all objects in the scene creating groups either by selecting prefix/suffix \n"
                  "or by the object type.",
                  fn="boldLabelFont", h=40)
        cmds.separator(style="none", h=10)

        cmds.rowColumnLayout(nc=4)
        self.folders_col = cmds.radioCollection(numberOfCollectionItems=2)

        folder_suffix = cmds.radioButton(label=self.radio_suffix_type)
        cmds.separator(style="none", w=50)
        folder_prefix = cmds.radioButton(label="Make groups by prefix")

        cmds.radioCollection(self.folders_col, edit=True, select=folder_suffix)
        cmds.setParent('..')

        cmds.separator(style="none", w=20)
        cmds.button (l = "CREATE GROUPS BY PREFIX/SUFFIX",c= self.FolderByName)

        cmds.separator(style="none", h=50)
        cmds.button (l = "CREATE GROUPS BY OBJECT TYPE", c= lambda x : self.sorter(byType=True))
        cmds.setParent('..')

        cmds.showWindow(win)

    def collapse_cmd(self, frame, height):
        '''
        This function collapes the frame provided.
        Args:
            frame: The frame provided.
            height: The height of the frame

        Returns:

        '''
        window_height = cmds.window(self.window, query=True, height=True)
        frame_height = cmds.frameLayout(frame, query=True, height=True)
        cmds.window(self.window, edit=True, height=window_height - height + 25)
        cmds.frameLayout(frame, edit=True, height=frame_height - height + 25)

    def expand_cmd(self, frame,  height):
        '''
        This function expands the frame provided.
        Args:
            frame: The frame provided.
            height: The height of the frame

        Returns:

        '''
        window_height = cmds.window(self.window, query=True, height=True)
        frame_height = cmds.frameLayout(frame, query=True, height=True)
        cmds.window(self.window, edit=True, height = window_height + height - 25)
        cmds.frameLayout(frame, edit=True, height=frame_height + height - 25)


    def Rename(self, addPrefix = True):
        '''
        This function adds a prefix/suffix to the object by the word provided or by the object type.
        Args:
            addPrefix:

        Returns:

        '''


        #get option selected
        rename_col = cmds.radioCollection(self.rename_col, query=True, select=True)
        selected = cmds.radioButton(rename_col, query=True, label=True)

        if(selected == self.radio_object_type):
            byObject = True
        else:
            byObject = False

        #get provided word and rename
        if(not byObject):
            word_text = cmds.textField (self.word, q=True, tx=True)
            if (word_text == ''):
                cmds.error("The text field is empty. Please type the word you want prefixed")
                return

            if(addPrefix):
                self.addPrefix(word_text, byType= False)
            else:
                self.addSuffix(word_text, byType=False)

        #rename by type
        else:
            if (addPrefix):
                self.addPrefix(byType=True)
            else:
                self.addSuffix(byType=True)


    def FolderByName (self,*args):
        '''
        This function creates a folder based on the prefix/suffix of the objects.
        Args:
            *args: 

        Returns:

        '''

        # get option selected
        folders_col = cmds.radioCollection(self.folders_col, query=True, select=True)
        selected = cmds.radioButton(folders_col, query=True, label=True)

        if (selected == self.radio_suffix_type):
            bySuffix = True
        else:
            bySuffix = False

        if(bySuffix):
            self.sorter(byName=True,bySuffix=True)
        else:
            self.sorter(byName=True,bySuffix=False)


    def addPrefix(self, prefix = None ,byType = False):
        '''
        This function adds prefix to the selected objects. If no objects are selected, every object will get a
        prefix. If byType is ticked object will get prefix by the object type.

        Args:
            prefix: The prefix to be added.
            byType: The prefix added by type.
        Returns:

        '''

        # select the objects. If nothing is selected, select everything
        objects = []
        objects = cmds.ls(sl=True, long=True)
        
        if (objects == []):
            objects = cmds.ls(dag=True, long = True)

        objects.sort(key=len, reverse = True)

        #prefixing each object
        for object in objects:
            shortName = object.split("|")[-1]

            if (byType is True):
                objType = self.getType(object)
                prefix = self.groups.get (objType,self.default)
                
            if (shortName.startswith(prefix)):
                continue
                
            #Incase user adds _ at the end, strip it
            if (prefix.endswith('_')):
                prefix = prefix[:-1]

            #rename
            try:
                newName = "{}_{}".format(prefix, shortName)
                oldName = object
                cmds.rename(object, newName)
                print("Successfully renamed " + oldName + " to " + newName)
            except:
                cmds.warning(object + ' cannot be renamed.')
                continue


    def addSuffix (self, suffix = None, byType = False):
        '''
        This function adds suffix to the selected objects. If no objects are selected, every object will get a
        suffix. If byType is ticked object will get suffix by the object type.
        Args:
            suffix: The suffix to be added.
            byType: The suffix added by type.

        Returns:

        '''

        # select the objects
        objects = []
        objects = cmds.ls(sl=True, long=True)
        if (objects == []):
            objects = cmds.ls(dag=True, long=True)

        objects.sort(key=len, reverse=True)

        # suffixing each object
        for object in objects:
            shortName = object.split("|")[-1]

            if (byType is True):
                objType = self.getType(object)
                suffix = self.groups.get(objType, self.default)
                
            if (shortName.endswith(suffix)):
                continue

            if (suffix.endswith('_')):
                suffix = suffix[:-1]

            #rename
            try:
                newName = "{}_{}".format( shortName, suffix)
                oldName = object
                cmds.rename(object, newName)
                print("Successfully renamed " + oldName + " to " + newName)
            except:
                cmds.warning(object + ' cannot be renamed.')
                continue

    def getType (self,object):
        '''
        This fuction returns the tyoe of object. If grouped then the first element is considered
        as the main type.
        Args:
            object: The object that the type

        Returns:

        '''
        
        #get children of the object
        children = cmds.listRelatives(object, children=True, fullPath=True) or []
        
        if (len(children) >= 1):
            child = children[0] #first children object type
            objType = cmds.objectType(child)
        else:
            objType = cmds.objectType(object)  #selected object type
            
        return objType


    def sorter (self, byName = False, byType = False, bySuffix = False):
        '''
        Sort all assets into groups either by the name before the first _ appears or by the type.
        Args:
            byName:
            byType:

        Returns:

        '''
        
        # select the objects
        selected_objects = []
        objects = []
        
        selected_objects = cmds.ls(sl=True, long=True)
        if (selected_objects == []):
            selected_objects = cmds.ls(dag=True, long=True)
            
        # We need all objects in the case the user decides selected objects to be grouped and there is a group
        # present in the hierarchy.
        all_objs_list = cmds.ls(dag = True,long=True)
        all_objs = []

        #creating a list of objects to be sorted
        for object in selected_objects:
            if (cmds.listRelatives(object, parent=True) is not None): #Object is a  child
                continue
            objType = self.getType(object)
            if (objType == 'camera'): #No folder created for camera
                continue

            objName = object[1:] #strip the | from the name
            objName = objName.lower()

            if(objName in self.groups.values()): #Its already a folder of object type
                continue

            if (cmds.listRelatives(object, children = True)): #appending it into the list of objects to be sorted
                objects.append(object)

        #create list for all objects
        for object in all_objs_list:
            if (cmds.listRelatives(object, p=True) is not None): #Object is a  child
                continue
            object = object[1:]
            all_objs.append(object)

        for object in objects:
            if (byName):

                if (bySuffix):
                    grpName = object.split("_")[-1] #get the suffix
                else:
                    grpName = object.split("_")[0] #get the prefix
                    grpName = grpName[1:] #strip |

            if (byType):
                objType = self.getType(object)
                grpName = self.groups.get(objType, self.default)


            grpName = grpName.upper()

            if grpName in all_objs: #folder is already created
                index = all_objs.index(grpName)
                grp = all_objs[index] #getting the folder
            #creating the folder
            else:
                grp = cmds.group(n=grpName, em=True)
                print ("Successfully created new group " + grp)
                all_objs.append(grp)

            if (grp != None):
                cmds.parent(object, grp)
                print("Succesffuly moved {} to the group {}".format(object,grp))

organizer = Organizer()