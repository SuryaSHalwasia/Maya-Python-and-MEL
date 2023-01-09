from maya import cmds, mel


class wheelsCreator ():
    def __init__(self):

        #wheel variables
        self.l_to_r_dist = 2.0
        self.f_to_b_dist = 4.0
        self.width = 0.25

        self.radius = 1
        self.end_loc_dist = 3
        self.wheels = []

        self.front_back_loc_val = 4
        self.wheel_constraint_angle = 45
        self.use_mesh = None

        #UI variables
        self.sliderX = None
        self.sliderZ = None
        self.sliderScale = None

        self.sliderXRangeMin = None
        self.sliderXRangeMax = None

        self.sliderZRangeMin = None
        self.sliderZRangeMax = None

        self.textX = None
        self.textZ = None
        self.textScale = None

        self.rigBtn = None
        self.createBtn = None
        self.disabled = [None,None,None,None]

        self.UI ()

    def UI(self):
        '''
        This function creates the UI
        Returns:

        '''

        #create the window
        win = "WheelsCreator"
        if (cmds.window(win, exists=True)):
            cmds.deleteUI(win)
        cmds.window(win, rtf=True, nde = True, w=400, h=350, t=win, s=False)
        cmds.columnLayout(adj=True)

        #create UI
        cmds.text(l="Select the mesh to be used a wheel or select the default mesh option.\nThen "
                    "you can adjust the distance and scale to fit correctly to any vehicle mesh.\n"
                    "Finally, you can select the create rig option to create basic rig \n", fn="boldLabelFont")
        cmds.separator(hr=True, style="none", h=50)

        cmds.rowColumnLayout(nc=4)

        self.use_mesh = cmds.checkBox(l = "Use selected mesh as wheel")
        cmds.separator(style="none", w=30)
        self.createBtn = cmds.button(l = "CREATE WHEEL",c= self.Wheel)
        cmds.setParent('..')

        cmds.separator(style="none", h=30)

        #Buttons for using created mesh or using a primitive cyinder mesh
        cmds.rowColumnLayout(nc=5)
        cmds.text(l= "X Wheel Distance", fn="boldLabelFont")
        cmds.separator(style="none", w=10)

        #create Sliders for adjusting wheel properties
        self.sliderX = cmds.floatSlider(value=0, min = -2, max= 2,
                                        dc = lambda x : self.ChangeVal(self.sliderX,self.textX, True), w=300,s=0.05,
                                        en = False)
        cmds.separator(style="none", w=10)

        self.disabled[0] = cmds.button(l="CLEAR", c = lambda x : self.clear(self.sliderX,self.textX, True), en = False)
        cmds.setParent('..')

        cmds.rowColumnLayout(nc=6)
        self.sliderXRangeMin = cmds.textField(w=40, tx=-2,
                                              ec=lambda x: self.EditSlider(slider=self.sliderX,
                                                                           textfield=self.sliderXRangeMin,
                                                                           isPositive=False) , en = False)

        cmds.separator(style="none", w=205)
        self.textX = cmds.text(l = 0,fn="boldLabelFont")

        cmds.separator(style="none", w=160)
        self.sliderXRangeMax = cmds.textField(w=40, tx=2,
                                              ec=lambda x: self.EditSlider(slider=self.sliderX,
                                                                           textfield=self.sliderXRangeMax,
                                                                           isPositive=True), en = False)

        cmds.setParent('..')
        cmds.separator(style="none", h=10)



        cmds.rowColumnLayout(nc=5)
        cmds.text(l="Z Wheel Distance", fn="boldLabelFont")

        self.sliderZ = cmds.floatSlider(value=0, min = -2, max= 2,
                                        dc = lambda x : self.ChangeVal(self.sliderZ,self.textZ, False),
                                        w=300, en = False)

        cmds.separator(style="none", w=10)
        self.disabled[1]= cmds.button(l="CLEAR", c = lambda x : self.clear(self.sliderZ,self.textZ, False), en = False)

        cmds.setParent('..')

        cmds.rowColumnLayout(nc=6)
        self.sliderZRangeMin = cmds.textField(w=40, tx = -2 ,
                                              ec = lambda x : self.EditSlider(slider=self.sliderZ,
                                                                    textfield=self.sliderZRangeMin, isPositive=False)
                                                                    ,en = False)

        cmds.separator(style="none", w=200)
        self.textZ = cmds.text(l=0, fn="boldLabelFont")

        cmds.separator(style="none", w=160)
        self.sliderZRangeMax = cmds.textField(w=40, tx = 2 ,
                                              ec = lambda x : self.EditSlider(slider=self.sliderZ,
                                                                    textfield = self.sliderZRangeMax, isPositive = True)
                                                                    ,en = False)

        cmds.setParent('..')
        cmds.separator(style="none", h=10)



        cmds.rowColumnLayout(nc=5)
        cmds.text(l="Wheels Scale", fn="boldLabelFont")

        cmds.separator(style="none", w=10)
        self.sliderScale = cmds.floatSlider(value=1, min=0.1, max=7, dc=self.Scale,s=0.1, w=300, en = False)

        cmds.separator(style="none", w=10)
        self.disabled[2] = cmds.button(l="CLEAR", c = self.clearScale, en = False)
        cmds.setParent('..')

        self.textScale = cmds.text(l=1, fn="boldLabelFont")
        cmds.separator(style="none", h=30)

        #final accept button
        self.disabled[3] = cmds.button(l="FINALIZE AND RIG", w=200, c=self.rigWheels, en = False)

        cmds.showWindow(win)



    def Wheel(self,*args):
        '''
        This function calls and stores the wheel and activates the sliders for modifying the properties.
        Args:
            *args:

        Returns:

        '''

        #get the value from user whether to use selected mesh or not and create wheels
        val = cmds.checkBox(self.use_mesh, q=True, v=True)
        self.createWheels(val)

        cmds.button(self.createBtn,e=True,en=False) #disable the create button to prevent user from recreating the wheel

        #enable the buttons, text fields and sliders
        for button in self.disabled:
            cmds.button(button, e=True, en= True)

        cmds.floatSlider(self.sliderX,e=True,en=True)
        cmds.floatSlider(self.sliderZ,e=True,en=True)
        cmds.floatSlider(self.sliderScale,e=True,en=True)

        texts = [self.sliderXRangeMin, self.sliderXRangeMax, self.sliderZRangeMin, self.sliderZRangeMax]

        for textfield in texts:
            cmds.textField(textfield, e = True, en = True)



    def clear (self, slider, text, isX):
        '''
        This function resets the slider to the default value as well as the wheel to default x or z position.
        Args:
            slider: The slider to reset
            text: The text to reset
            isX: if isX then x value is reset else z

        Returns:

        '''
        #reset slider
        cmds.floatSlider(slider,v=0,e=True)

        cmds.text(text,e=True,l=0) #edit text
        self.changeTiresDistance(0,isX) #reset position


    def clearScale (self,*args):
        '''
        This function resets the scale
        Args:
            *args:

        Returns:

        '''

        cmds.floatSlider(self.sliderScale,v=1,e=True) #reset the slider

        cmds.text(self.textScale, e=True, l=1)
        self.changeScale(1)


    def ChangeVal(self, slider, text, isX):
        '''
        This function takes the value of the slider and changes the tire distance
        Args:
            slider:
            text:
            isX:

        Returns:

        '''
        val = cmds.floatSlider (slider, q= True, v = True)
        self.changeTiresDistance(val, isX)
        val = round (val, 2)
        cmds.text (text,e=True,l=val)


    def Scale(self, *args):
        '''
        This function changes the scale.
        Args:
            *args:

        Returns:

        '''

        val= cmds.floatSlider(self.sliderScale, q= True, v = True)
        val = round(val, 2)
        cmds.text(self.textScale, e=True, l=val)
        self.changeScale(val)

    def changeScale(self, val):
        '''
        This function changes the scale to the value provided.
        Args:
            val:

        Returns:

        '''
        for i in self.wheels:
            cmds.setAttr("{}.scale".format(i),val,val,val)


    def EditSlider(self, slider, textfield, isPositive):
        '''
        This function can change the range of the slider
        Args:
            slider: The slider to change the range
            textfield: The textfield value to edit range
            isPositive: if isPositive then maximum value is edited else minimum

        Returns:

        '''

        text = cmds.textField (textfield, q=True, tx=True) #get text value

        #convert into integer if error then reset the textfield to previous value
        try:
            number = int(text)
        except:
            cmds.warning ("Invalid literal. Please type again")
            value = cmds.floatSlider(slider,min = True ,q=True)
            cmds.textField (textfield, e= True, tx = str(value))
            return


        if (not isPositive): #change minimum range

            if (number > 0): #min cant be greater than 0
                number = 0
                cmds.textField(textfield, e= True, tx = str(number)) #reset text to 0

            cmds.floatSlider(slider, min = number ,e=True) #change min

        #change max
        else:
            if (number < 0):
                number = 0

                cmds.textField(textfield, e= True, tx = str(number))
            cmds.floatSlider(slider, max = number ,e=True)



    def createWheels(self, useProvidedMesh = False):
        '''
        This function which create wheels. If mesh is provided, that mesh will be used as a wheel
        Args:
            useProvidedMesh: Used the mesh as a wheel

        Returns:

        '''
        #if mesh is provided 
        if(useProvidedMesh is True):
            tire = cmds.ls(selection = True)[0]
            
            if(tire is []):
                cmds.error("No mesh selected. Please select a mesh to instantiate or uncheck use provided mesh")
                return
            
            self.wheels = self.InstantiateProvidedMesh(tire) #instantiate mesh function
            
        else:
            self.wheels = self.createTires()

        cmds.select(cl=True)


    def InstantiateProvidedMesh (self, tire):
        '''
        This function creates and stores the four tires
        Returns:

        '''
        fl_tire = self.createInstaniateTire("front_left_tire",tire, (self.l_to_r_dist * -1),
                                                                    self.f_to_b_dist)
        fr_tire = self.createInstaniateTire("front_right_tire",tire, self.l_to_r_dist,self.f_to_b_dist)
        rl_tire = self.createInstaniateTire("rear_left_tire", tire,  (self.l_to_r_dist * -1),
                                                                    (self.f_to_b_dist * -1))        
        rr_tire = self.createInstaniateTire("rear_right_tire",tire,  self.l_to_r_dist, -1 * self.f_to_b_dist)

        return [fl_tire, fr_tire, rl_tire, rr_tire]

    def createInstaniateTire(self, name, tire, xpos, zpos):
        '''
        This function duplicates the provided mesh at the given position.
        Args:
            tire: The duplicated mesh will be renamed by this name.
            xpos: The x position of the created mesh
            zpos: the z position of the created mesh

        Returns:

        '''
        
        #duplicate and rename
        wheel = mel.eval("duplicate " + tire)[0]
        wheel = cmds.rename(wheel,name)
        
        cmds.setAttr("{}.translate".format(wheel), xpos, 0, zpos) #change pos

        cmds.makeIdentity(wheel, apply=True, t=True, r=True, s=True) 
        return wheel

    def createTires(self):
        '''
        Creates the tire and stores
        Returns:

        '''
        rr_tire = self.createTire ("rear_right_tire",self.l_to_r_dist, (self.f_to_b_dist * -1) )
        fr_tire = self.createTire("front_right_tire",self.l_to_r_dist,self.f_to_b_dist)
        rl_tire = self.createTire("rear_left_tire",(-1 * self.l_to_r_dist),(-1 * self.f_to_b_dist))
        fl_tire = self.createTire("front_left_tire",(-1 * self.l_to_r_dist), self.f_to_b_dist)

        return [fl_tire,fr_tire,rl_tire,rr_tire]

    def createTire(self,name,xpos,zpos):
        '''
        This function creates the primitve cylinder as tire at the position provided
        Args:
            name: The cylinder is renamed as wheel.
            xpos: The x position of the wheel.
            zpos: The z position of the wheel.

        Returns:

        '''
        tire = cmds.polyCylinder(h= self.width, r= self.radius, ax=(0, 0, 1), sc=True, name=name) #create the cylinder
        cmds.setAttr("{}.translate".format(tire[0]), xpos,0,zpos)
        cmds.setAttr("{}.rotate".format(tire[0]),0,90,0)
        
        cmds.makeIdentity(tire, apply=True, t=True, r=True, s=True)
        return tire[0] #return the geometry

    def changeTiresDistance(self, distance = 0.0, changeXnotZ = True):
        '''
        Move the wheels based on distance if not x then z axis
        Args:
            distance:
            changeXnotZ: If true it means to change x position of the wheels

        Returns:

        '''
        if self.wheels == []:
            cmds.error("No wheels found. Please create new wheels.")
            return
        
        #change x position
        if(changeXnotZ is True):
            isLeft = True #all left wheels need to move in one direction
            #The array of wheel is stored in alternate order hence alternating the boolean variable. 
            
            for i in range(0, 4):
                original_distMat = cmds.getAttr("{}.translate".format(self.wheels[i]))[0]  #the distance matrix

                if isLeft:
                    distMat = [distance, original_distMat[1], original_distMat[2]] #change x variable
                    cmds.setAttr("{}.translate".format(self.wheels[i]), distMat[0], distMat[1], distMat[2])

                else:
                    distMat = [-distance, original_distMat[1], original_distMat[2]] #move it in opposite direction
                    cmds.setAttr("{}.translate".format(self.wheels[i]), distMat[0], distMat[1], distMat[2])

                isLeft = not isLeft

        else: #change z position
            for i in range(0,4):
                original_distMat = cmds.getAttr("{}.translate".format(self.wheels[i]))[0]
                #The first two elements of the wheels array are front tires and then the back

                if (i<2):
                    distMat = [original_distMat[0], original_distMat[1], distance]
                    cmds.setAttr("{}.translate".format(self.wheels[i]), distMat[0], distMat[1], distMat[2])

                else:
                    distMat = [original_distMat[0], original_distMat[1], - distance]
                    cmds.setAttr("{}.translate".format(self.wheels[i]), distMat[0], distMat[1], distMat[2])


    def rigWheels(self, *args):
        '''
        This function creates the final rigs of the wheels.
        Args:
            *args:

        Returns:

        '''

        self.GetRadiusAttr() #create the attribute radius for all wheels

        rot_loc = cmds.spaceLocator( name="ROT_LOC_CTRL")[0] #This controls the location and rotates the wheel based on the radius

        for wheel in self.wheels:
            cmds.parentConstraint(rot_loc,wheel, sr = ["x","y","z"], st = ["x","y"], mo = True) #constraint

            #rotate the wheel based on its circumference
            mdl = cmds.createNode('multDoubleLinear', name= wheel + "_" + "MDL")
            rad = cmds.getAttr("{}.radius".format(wheel))
            mult_factor = float(52.325) / rad

            cmds.connectAttr(rot_loc + ".translateZ",mdl + '.input1')
            cmds.setAttr(mdl + '.input2', mult_factor)
            cmds.connectAttr(mdl + '.output', wheel + '.rotateX')

        #creates the locators to control the rotation of front and back wheels at fixed distance based on wheel location
        front_tire_dist = cmds.getAttr(self.wheels[0] + ".boundingBoxMaxZ") + self.end_loc_dist
        back_tire_dist = cmds.getAttr(self.wheels[2] + ".boundingBoxMinZ") - self.end_loc_dist

        front_tires_loc = cmds.spaceLocator(name = "FRONT_ROT_CTRL", p = [0,0,front_tire_dist])[0] #the front controllor
        cmds.xform(front_tires_loc, cpc = True)

        back_tires_loc = cmds.spaceLocator(name = "BACK_ROT_CTRL", p = [0,0,back_tire_dist])[0] #the back controllor
        cmds.xform(back_tires_loc,cpc= True)

        mdl_front = cmds.createNode('multDoubleLinear', name=front_tires_loc + "_" + "MDL")
        mdl_back = cmds.createNode('multDoubleLinear', name=back_tires_loc + "_" + "MDL")

        #connect the translation of the locators to the rotation of the wheels
        cmds.connectAttr(front_tires_loc + ".translateX", mdl_front + '.input1')
        cmds.connectAttr(back_tires_loc + ".translateX", mdl_back + '.input1')

        cmds.setAttr(mdl_front + '.input2', self.front_back_loc_val)
        cmds.setAttr(mdl_back + '.input2', self.front_back_loc_val)


        #the range is the maximum rotation the wheels can rotate
        range_front = cmds.createNode('setRange', name = front_tires_loc + "_" + "range")
        range_back = cmds.createNode('setRange', name = back_tires_loc + "_" + "range")


        #The attribute which can be controlled to change the max and min angle rotation of the wheels
        cmds.addAttr(front_tires_loc, ln = "minAngle", at = "float", dv = -45, max = 0)
        cmds.addAttr(front_tires_loc, ln = "maxAngle", at = "float", dv = 45, min = 0)

        cmds.addAttr(back_tires_loc, ln = "minAngle", at = "float", dv = -45, max = 0)
        cmds.addAttr(back_tires_loc, ln = "maxAngle", at = "float", dv = 45, min = 0)

        self.rigRot(range_front, front_tires_loc, mdl_front,0,1) #the front wheels
        self.rigRot(range_back, back_tires_loc, mdl_back,2,3) #the back wheels

        win = "WheelsCreator"
        if (cmds.window(win, exists=True)):
            cmds.deleteUI(win) #close the main window


    def rigRot(self, range_front, tires_loc, mdl, index1, index2):
        '''
        This functions sets the rotation range of the wheels controlled by the locator
        Args:
            range_front:
            tires_loc:
            mdl:
            index1:
            index2:

        Returns:

        '''
        #connect the range to maximum and minimum rotation using attribute from the locator
        cmds.connectAttr(mdl + '.output', range_front + '.valueX')
        cmds.connectAttr(tires_loc + '.minAngle', range_front + '.minX')

        cmds.connectAttr(tires_loc + '.minAngle', range_front + '.oldMinX')
        cmds.connectAttr(tires_loc + '.maxAngle',  range_front + '.maxX')
        cmds.connectAttr(tires_loc + '.maxAngle', range_front + '.oldMaxX')

        cmds.connectAttr(range_front + '.outValueX', self.wheels[index1] + '.rotateY')
        cmds.connectAttr(range_front + '.outValueX', self.wheels[index2] + '.rotateY')


    def GetRadiusAttr(self):
        '''
        This function creates the radius attribute of the wheel. Updates if already created
        Returns:

        '''
        for wheel in self.wheels:
            yMin = cmds.getAttr(wheel + ".boundingBoxMinY")
            yMax = cmds.getAttr(wheel + ".boundingBoxMaxY")

            rad = (yMax - yMin)/2
            lst = cmds.listAttr(wheel)

            if "radius" not in lst:
                cmds.addAttr(wheel, ln = "radius", at = "float", dv = rad)
            else:
                cmds.setAttr(wheel + ".radius", rad)



Wheels = wheelsCreator ()
