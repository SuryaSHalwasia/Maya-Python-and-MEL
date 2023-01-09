from maya import cmds
import math

class rigChains():

    def __init__(self):

        #initialize the joint list and pole vector
        self.joint_list =[]
        self.pole_vector = None


        #UI function
        self.UI()


    def UI(self):
        '''

        Returns:

        '''

        #UI Window Creation
        win = "RigChains"
        if (cmds.window(win, exists=True)):
            cmds.deleteUI(win)

        self.window = cmds.window (win, rtf=True, nde=True, w=400, h=500, t=win, s=False)
        cmds.columnLayout (adj=True)

        #Info about the program
        cmds.text (l="This program will create the fk, ik and bind chains based on the selected joint chain. \n"
                    "Please select the joint chain and the pole vector to create chains ", fn="boldLabelFont")
        cmds.separator(hr=True, style="none", h=50)

        #select chain
        cmds.text (l= "Select all the joints in order")
        cmds.button (l="SELECT JOINTS", c= lambda x : self.select_jnt())

        #selected chain
        self.joint_label = cmds.text (l= "SELECTED JOINTS : " , fn="boldLabelFont")
        cmds.separator(hr=True, style="none", h=30)


        #select pole vector
        cmds.button (l="SELECT POLE VECTOR", c= lambda x : self.select_pole_vector())

        # selected pole vector
        self.pv_label = cmds.text(l="SELECTED POLE VECTOR : ", fn="boldLabelFont")
        cmds.separator(hr=True, style="none", h=30)

        # Frame UI for rig options
        self.rig_options = cmds.frameLayout(label='Rig Options', width=400, height=100, collapsable=True,
                                              collapseCommand=lambda: self.collapse_cmd(self.rig_options, 100),
                                              expandCommand=lambda: self.expand_cmd(self.rig_options, 100))

        #option to remove guides
        cmds.rowColumnLayout(nc=7)

        cmds.text (l= "Remove Guides")
        cmds.separator(hr=True, style="none", w=80)
        self.rmvguides_col = cmds.radioCollection(numberOfCollectionItems=2)
        rmv_yes = cmds.radioButton(label='Yes')
        rmv_no = cmds.radioButton(label='No')

        cmds.radioCollection(self.rmvguides_col, edit=True, select=rmv_yes)

        cmds.setParent('..')

        # option to add stretch
        cmds.rowColumnLayout(nc=7)

        cmds.text(l="Add Stretch")
        cmds.separator(hr=True, style="none", w=98)
        self.stretch_col = cmds.radioCollection(numberOfCollectionItems=2)
        stretch_yes = cmds.radioButton(label='Yes')
        stretch_no = cmds.radioButton(label='No')

        cmds.radioCollection(self.stretch_col, edit=True, select= stretch_yes)

        cmds.setParent('..')

        # select primary axis
        cmds.rowColumnLayout(nc=9)

        cmds.text(l="Primary Axis")
        cmds.separator(hr=True, style="none", w=98)
        self.primary_col = cmds.radioCollection(numberOfCollectionItems=6)
        primary_x = cmds.radioButton(label='X')
        primary_y = cmds.radioButton(label='Y')
        primary_z = cmds.radioButton(label='Z')
        cmds.separator( style="none", w=20)
        primary_neg_x = cmds.radioButton(label='-X')
        primary_neg_y = cmds.radioButton(label='-Y')
        primary_neg_z = cmds.radioButton(label='-Z')
        cmds.radioCollection(self.primary_col, edit=True, select= primary_x)

        cmds.setParent('..')

        #select up axis
        cmds.rowColumnLayout(nc=9)

        cmds.text(l="Up Axis")
        cmds.separator(hr=True, style="none", w=120)
        self.up_col = cmds.radioCollection(numberOfCollectionItems=3)
        up_x = cmds.radioButton(label='X')
        up_y = cmds.radioButton(label='Y')
        up_z = cmds.radioButton(label='Z')
        cmds.separator( style="none", w=20)
        up_neg_x = cmds.radioButton(label='-X')
        up_neg_y = cmds.radioButton(label='-Y')
        up_neg_z = cmds.radioButton(label='-Z')

        cmds.radioCollection(self.up_col, edit=True, select=up_y)

        cmds.setParent('..')

        cmds.setParent('..')
        cmds.separator(hr=True, style="none", h=30)

        # Frame UI for rig options
        self.color_options = cmds.frameLayout(label='Color Options', width=400, height=150, collapsable=True,
                                            collapseCommand=lambda: self.collapse_cmd(self.color_options, 100),
                                            expandCommand=lambda: self.expand_cmd(self.color_options, 100))

        #option to change color for locator chains
        self.pr_color = cmds.colorSliderGrp(label='Primary:       ', adjustableColumn=5,rgb=(1, 1, 0))

        self.fk_color = cmds.colorSliderGrp(label='FK:       ', adjustableColumn=3,rgb=(0, 0, 1))

        self.sc_color = cmds.colorSliderGrp(label='Secondary:       ', adjustableColumn=3,rgb= (0, 0.2, 1))

        self.pv_color = cmds.colorSliderGrp(label='Pole Vector:       ', adjustableColumn=3,rgb= (0, 1, 1))

        cmds.separator(hr=True, style="none", h=30)

        cmds.setParent('..')

        #final button to create
        cmds.button (l="CREATE CHAINS", c= lambda x : self.create_rig())




        cmds.showWindow(win)


    def select_jnt(self):
        '''

        Returns:

        '''

        #select the joints
        self.joint_list = cmds.ls(selection = True)


        joint_tex = ''

        #check if everything selected is a joint else throw error. Also create joint text
        for joint in self.joint_list:
            objType = cmds.objectType(joint)
            if (objType != "joint"):
                self.joint_list = []
                cmds.error("Please select joints only.")
                break
            joint_tex = joint_tex + ' -> ' + joint

        joint_tex = joint_tex.lstrip( " -> ")


        #change the text in joint label to display new selected joints
        cmds.text (self.joint_label, e = True, l = "SELECTED JOINTS : " + joint_tex)



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


    def select_pole_vector(self):
        '''

        Returns:

        '''

        #select the pole vector
        self.pole_vector = cmds.ls (selection = True)[0]

        #check if the pole vector is a locator
        objType = cmds.objectType(self.pole_vector)

        if (objType != "transform"):
            self.pole_vector = None
            cmds.error("Please select proper pole vector")


        #change the text in pole vector label to display new selected pole vector
        cmds.text (self.pv_label, e = True, l = "SELECTED POLE VECTOR : " + self.pole_vector)




    def create_rig(self):
        '''

        Returns:

        '''

        #check if user has provided joints and pole vector

        if (self.joint_list == []):
            cmds.error ("Please select the joints to create the rig")

        if (self.pole_vector == None):
            cmds.error ("Please provide the pole vector")

        #get primary axis
        primary_axis_btn  =  cmds.radioCollection(self.primary_col, query = True, select = True)
        primary_axis = cmds.radioButton(primary_axis_btn, query=True, label=True)
        pa = self.define_axis(primary_axis)

        # create chains
        ik_chain = self.create_chain('IK')
        fk_chain = self.create_chain('FK')
        bind_chain = self.create_chain('bind')

        # optimize control size
        r = self.distance_between(fk_chain[0], fk_chain[-1]) / float(5)

        # create fk controls and connection to fk chain
        fk_ctrls = []

        for i, j in enumerate(self.joint_list):

            joint_name = str(j)

            # if joint name ends with _jnt strip it
            if (joint_name.endswith('_JNT')):
                joint_name = joint_name.rstrip('_JNT')

            # create controls
            ctrl = cmds.circle(radius=r, normal=pa, degree=3,
                               name='{}_FK_CTRL'.format(joint_name))[0]

            self.tag_control(ctrl, 'rig_fk')

            if i != 0:
                cmds.parent(ctrl, par)

            # align control to joint
            ctrl_off = self.align_lras(snap_align=True, sel=[ctrl, fk_chain[i]])

            if i == 0:
                fk_top_grp = ctrl_off

            # define parent control
            par = ctrl

            # connect control to joint
            cmds.pointConstraint(ctrl, fk_chain[i])
            cmds.connectAttr(ctrl + '.rotate', fk_chain[i] + '.rotate')
            fk_ctrls.append(ctrl)

        # Create IK controls
        world_ctrl = cmds.circle(radius=r * 1.2, normal=pa, degree=1, sections=4,
                                 constructionHistory=False, name='rig_IK_CTRL')[0]
        cmds.setAttr(world_ctrl + '.rotate' + primary_axis[-1], 45)

        self.a_to_b(is_trans=True, is_rot=False, sel=[world_ctrl, ik_chain[-1]], freeze=True)
        self.tag_control(world_ctrl, 'rig_primary')

        #local IK ctrl
        local_ctrl = cmds.circle(radius=r, normal=pa, degree=1, sections=4,
                                 name='rig_local_IK_CTRL')[0]
        cmds.setAttr(local_ctrl + '.rotate' + primary_axis[-1], 45)

        cmds.makeIdentity(local_ctrl, apply=True, rotate=True)
        local_off = self.align_lras(snap_align=True, sel=[local_ctrl, ik_chain[-1]])
        cmds.parent(local_off, world_ctrl)

        self.tag_control(local_ctrl, 'rig_secondary')
        loc_points = [[0.0, 1.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 0.0],
                      [-1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 0.0],
                      [0.0, 0.0, -1.0], [0.0, 0.0, 1.0]]

        #create pole vector control
        pv_ctrl = self.curve_control(loc_points, name= 'rig_PV_CTRL')
        cmds.setAttr(pv_ctrl + '.scale', r * 0.25, r * 0.25, r * 0.25)

        self.a_to_b(is_trans=True, is_rot=True, sel=[pv_ctrl, self.pole_vector])
        cmds.makeIdentity(pv_ctrl, apply=True, translate=True, rotate=True,
                          scale=True, normal=False)
        self.tag_control(pv_ctrl, 'rig_pv')


        #create base ik control
        jnt = self.joint_list[0]
        # if joint name ends with _jnt strip it
        if (jnt.endswith('_JNT')):
            jnt = jnt.rstrip('_JNT')

        base_ctrl = cmds.circle(radius=r * 1.2, normal=pa, degree=1, sections=4, constructionHistory=False,
                                name='{}_IK_CTRL'.format(jnt))[0]
        cmds.setAttr(base_ctrl + '.rotate' + primary_axis[-1], 45)

        self.a_to_b(is_trans=True, is_rot=True, sel=[base_ctrl, ik_chain[0]])
        cmds.makeIdentity(base_ctrl, apply=True, translate=True, rotate=True,
                          scale=True, normal=False)
        cmds.parentConstraint(base_ctrl, ik_chain[0], mo=True)

        self.tag_control(base_ctrl, 'rig_primary')

        # create IK Handle
        ik_handle = cmds.ikHandle(name= 'rig_IKH', startJoint=ik_chain[0], endEffector=ik_chain[-1],
                                  sticky='sticky', solver='ikRPsolver', setupForRPsolver=True)[0]
        cmds.parentConstraint(local_ctrl, ik_handle, mo=True)
        cmds.poleVectorConstraint(pv_ctrl, ik_handle)

        no_xform_list = [ik_handle]

        #create the settings ctrl
        plus_points = [[-0.333, 1, 0], [0.333, 1, 0],
                       [0.333, 0.333, 0], [1, 0.333, 0],
                       [1, -0.333, 0], [0.333, -0.333, 0],
                       [0.333, -1, 0], [-0.333, -1, 0.0],
                       [-0.333, -0.333, 0], [-1, -0.333, 0],
                       [-1, 0.333, 0], [-0.333, 0.333, 0],
                       [-0.333, 1, 0]]

        settings_ctrl = self.curve_control(point_list= plus_points, name= 'rig_settings_CTRL')
        self.tag_control(settings_ctrl, 'rig_primary')

        settings_off = self.align_lras(snap_align=True, sel=[settings_ctrl, bind_chain[-1]])
        cmds.setAttr(settings_ctrl + '.scale', r * 0.25, r * 0.25, r * 0.25)

        # get up axis
        up_axis_btn = cmds.radioCollection(self.up_col, query=True, select=True)
        up_axis = cmds.radioButton(primary_axis_btn, query=True, label=True)


        if up_axis[0] == '-':
            cmds.setAttr(settings_ctrl + '.translate' + up_axis[-1], r * -1.5)
        else:
            cmds.setAttr(settings_ctrl + '.translate' + up_axis[-1], r * 1.5)

        cmds.makeIdentity(settings_ctrl, apply=True, translate=True, rotate=True, scale=True, normal=False)
        cmds.parentConstraint(bind_chain[-1], settings_ctrl, mo=True)

        #create blend attr for fk ik
        cmds.addAttr(settings_ctrl, attributeType='double', min=0, max=1, defaultValue=1, keyable=True, longName='fkIk')

        self.blend_chains(ik_chain, fk_chain, bind_chain)

        #checking to add stretch
        stretch_btn  =  cmds.radioCollection(self.stretch_col, query = True, select = True)
        stretch = cmds.radioButton(stretch_btn, query=True, label=True)

        if(stretch == "Yes"):
            #add stretch
            ik_stretch = self.add_ik_stretch (ik_chain, base_ctrl, local_ctrl, world_ctrl, primary_axis)
            self.add_fk_stretch(fk_ctrls, fk_chain, primary_axis)
            no_xform_list += ik_stretch['measure_locs']

        # creating groups for cleanup
        fk_ctrl_grp = cmds.group(em=True, name= 'rig_FK_CTRL_GRP')
        ik_ctrl_grp = cmds.group(em=True, name= 'rig_IK_CTRL_GRP')

        skeleton_grp = cmds.group(em=True, name= 'rig_skeleton_GRP')
        no_xform_grp = cmds.group(em=True, name= 'rig_noXform_GRP')

        limb_rig_grp = cmds.group(em=True, name= 'rig_GRP')
        all_grp = cmds.group(em=True, name= "RIG")


        #parenting
        cmds.parent(world_ctrl, pv_ctrl, base_ctrl, ik_ctrl_grp)
        cmds.parent(fk_top_grp, fk_ctrl_grp)

        cmds.parent(bind_chain[0], skeleton_grp)
        cmds.parent(no_xform_list, no_xform_grp)

        cmds.parent(fk_ctrl_grp, ik_ctrl_grp, no_xform_grp, fk_chain[0], ik_chain[0], settings_off, limb_rig_grp)
        cmds.parent(skeleton_grp, limb_rig_grp, all_grp)

        self.transfer_pivots(sel=[bind_chain[0], skeleton_grp, limb_rig_grp, fk_ctrl_grp, ik_ctrl_grp])

        #add global scale attribute allowing everything to be uniformly scaled
        cmds.addAttr(all_grp, attributeType='double', min=0.001, dv=1, keyable=True,
                     ln="globalScale")
        [cmds.connectAttr(all_grp + '.globalScale', all_grp + '.scale' + axis) for axis in 'XYZ']

        if (stretch == "Yes"):
            gs_mdl = cmds.createNode('multDoubleLinear', name= 'rig_globalScale_MDL')
            cmds.setAttr(gs_mdl + '.input1', ik_stretch['length_total'])

            cmds.connectAttr(all_grp + '.globalScale', gs_mdl + '.input2')
            cmds.connectAttr(gs_mdl + '.output', ik_stretch['mdn'] + '.input2X')

            cmds.connectAttr(gs_mdl + '.output', ik_stretch['cnd'] + '.secondTerm')


        #creating color dict
        color = {'rig_primary' : cmds.colorSliderGrp(self.pr_color, q = True, rgb= True),
                 'rig_pv' : cmds.colorSliderGrp(self.pv_color, q = True, rgb= True),
                 'rig_fk' : cmds.colorSliderGrp(self.fk_color, q = True, rgb= True),
                 'rig_secondary' : cmds.colorSliderGrp(self.sc_color, q = True, rgb= True) }

        #adding color to created joint controls based on control type
        for color_tag in cmds.ls('*.controlType'):
            ctrl = color_tag.split('.')[0]
            ctrl_type = cmds.getAttr(color_tag)

            if 'rig' in ctrl_type:
                cmds.setAttr(ctrl + '.overrideEnabled', 1)
                cmds.setAttr(ctrl + '.overrideRGBColors', 1)

                cmds.setAttr(ctrl + '.overrideColorRGB', color[ctrl_type][0],
                             color[ctrl_type][1], color[ctrl_type][2])

        # lock and hide attributes
        self.lock_and_hide(fk_ctrls, attributes_list=['translate', 'scale', 'visibility'])
        self.lock_and_hide([world_ctrl, local_ctrl, base_ctrl], attributes_list=['scale', 'visibility'])
        self.lock_and_hide(pv_ctrl, attributes_list=['rotate', 'scale', 'visibility'])
        self.lock_and_hide(settings_ctrl)

        vis_res = cmds.createNode('reverse', name= 'self_fkIK_vis_REV')
        cmds.connectAttr(settings_ctrl + '.fkIk', vis_res + '.inputX')
        cmds.connectAttr(settings_ctrl + '.fkIk', ik_ctrl_grp + '.visibility')
        cmds.connectAttr(vis_res + '.outputX', fk_ctrl_grp + '.visibility')

        pv_gde = self.add_guides(pv_ctrl, ik_chain[1])
        cmds.parent(pv_gde[0], no_xform_grp)
        cmds.parent(pv_gde[1], ik_ctrl_grp)

        # remove guide option

        rmvguides = cmds.radioCollection(self.rmvguides_col, query=True, select=True)
        remove_guides = cmds.radioButton(rmvguides, query=True, label=True)

        if remove_guides:
            cmds.delete(self.joint_list, self.pole_vector)



    def define_axis(self,axis):
        '''
        This function returns the vector form of the axis
        Args:
            axis:

        Returns:

        '''

        #check if axis is X, Y or Z
        if axis[-1] == "X":
            vector_axis = (1, 0, 0)
        elif axis[-1] == "Y":
            vector_axis = (0, 1, 0)
        elif axis[-1] == "Z":
            vector_axis = (0, 0, 1)
        else:
            cmds.error("No axis provided.")

        #check if axis is negative
        if '-' in axis:
            vector_axis = tuple(va * -1 for va in vector_axis)

        #return the vector
        return vector_axis


    def create_chain(self, suffix):
        '''
        This function creates the chain with the suffix.
        Args:
            suffix:

        Returns:

        '''

        #create the chain with the suffix
        chain = []

        for j in self.joint_list:
            if (j == self.joint_list[0]):
                par = None
            else:
                par = jnt

            joint_name = str(j)

            #if joint name ends with _jnt strip it
            if (joint_name.endswith('_JNT')):
                joint_name = joint_name.rstrip('_JNT')

            #create the joint and move position
            jnt = cmds.joint(par, n='{}_{}_JNT'.format(joint_name,suffix))
            self.a_to_b(sel=[jnt, j])

            #freeze transformation and append jnt
            cmds.makeIdentity(jnt, apply=True, translate=True, rotate=True,
                              scale=True, normal=False)
            chain.append(jnt)

        #return the final chain
        return chain



    def a_to_b(self, is_trans=True, is_rot=True, sel=None, freeze=False):
        # if selection list is not provides, select from scene
        if not sel:
            sel = cmds.ls(selection=True)


        for s in sel:

            # checking if translation/rotation attributes are not locked
            tr_list = []
            if is_trans:
                tr_list.append('translate')
                if any(cmds.getAttr(s + '.translate' + attr, lock=True) for attr in 'XYZ'):
                    cmds.error('Translate attributes are locked!')
            if is_rot:
                tr_list.append('rotate')
                if any(cmds.getAttr(s + '.rotate' + attr, lock=True) for attr in 'XYZ'):
                    cmds.error('Rotate attributes are locked!')


            #check for objects with any transformation connections
            if s != sel[-1]:
                con_list = []
                for tr in tr_list:
                    con = cmds.listConnections(s + '.' + tr, destination=False,
                                               source=True, plugs=True)
                    if con:
                        [con_list.append(c) for c in con]
                    for attr in 'XYZ':
                        con = cmds.listConnections(s + '.' + tr + attr,
                                                   destination=False, source=True,
                                                   plugs=True)
                        if con:
                            [con_list.append(c) for c in con]


                #check for translate/rotate attribute string in lists
                has_trans = any('ranslate' in con for con in con_list)
                has_rot = any('otate' in con for con in con_list)

                # skip if there are connections
                if has_trans and has_rot:
                    continue
                elif has_trans and not has_rot:
                    continue
                elif has_rot and not has_trans:
                    continue

                # if their attributes are not locked then move
                else:
                    if is_trans:
                        cmds.delete(cmds.pointConstraint(sel[-1], s,
                                                         maintainOffset=False))
                    if is_rot:
                        cmds.delete(cmds.orientConstraint(sel[-1], s,
                                                          maintainOffset=False))
            if freeze:
                cmds.makeIdentity(s, apply=True, translate=True, rotate=True,
                                  scale=True, normal=False)

    def distance_between(self, node_a, node_b):
        '''
        This function returns the distance between two points
        Args:
            node_a: point a
            node_b: point b

        Returns:
            The distance between
        '''

        #calculate the distance between two points in space
        point_a = cmds.xform(node_a, query=True, worldSpace=True, rotatePivot=True)
        point_b = cmds.xform(node_b, query=True, worldSpace=True, rotatePivot=True)
        dist = 0


        for b, a in zip(point_b, point_a):
            dist = dist + pow((b - a), 2)
        dist = math.sqrt(dist)

        #return the result
        return dist

    def tag_control(self, ctrl, tag_name):
        '''
        Adds attribute to the control with the tag_name as the default value
        Args:
            tag_name:

        Returns:

        '''

        cmds.addAttr(ctrl, ln='controlType', dataType='string')
        cmds.setAttr(ctrl + '.controlType', tag_name, type='string')

    def align_lras(self, snap_align=False, delete_history=True, sel=None):
        # if no selection then select
        if not sel:
            sel = cmds.ls(selection=True)

        if len(sel) <= 1:
            cmds.error('Select the control first, then the joint to align.')

        ctrl = sel[0]
        jnt = sel[1]

        # check to see if the control has a parent and unparent it by parenting it to the world
        parent_node = cmds.listRelatives(ctrl, parent=True)
        if parent_node:
            cmds.parent(ctrl, world=True)

        # store the ctrl/joint's world space position, rotation, and matrix
        jnt_matrix = cmds.xform(jnt, query=True, worldSpace=True, matrix=True)
        jnt_pos = cmds.xform(jnt, query=True, worldSpace=True, rotatePivot=True)
        jnt_rot = cmds.xform(jnt, query=True, worldSpace=True, rotation=True)
        ctrl_pos = cmds.xform(ctrl, query=True, worldSpace=True, rotatePivot=True)
        ctrl_rot = cmds.xform(ctrl, query=True, worldSpace=True, rotation=True)

        #using the offsetParentMatrix instead of using an offset group
        if cmds.objExists(ctrl + '.offsetParentMatrix'):
            off_grp = False
            # ensure offset matrix has default values
            cmds.setAttr(ctrl + '.offsetParentMatrix',
                         [1.0, 0.0, 0.0, 0.0, 0.0,
                          1.0, 0.0, 0.0, 0.0, 0.0,
                          1.0, 0.0, 0.0, 0.0, 0.0,
                          1.0], type='matrix')
            self.reset_to_origin(ctrl)
            # copy joints matrix to control offsetParentMatrix
            cmds.setAttr(ctrl + '.offsetParentMatrix', jnt_matrix, type='matrix')

            if parent_node:
                # make temporary joints to help calculate offset matrix
                tmp_parent_jnt = cmds.joint(None, name='tmp_01_JNT')
                tmp_child_jnt = cmds.joint(tmp_parent_jnt, name='tmp_02_JNT')
                self.a_to_b(sel=[tmp_parent_jnt, parent_node[0]])
                self.a_to_b(sel=[tmp_child_jnt, jnt])
                cmds.parent(ctrl, parent_node[0])
                self.reset_transforms(ctrl)

                child_matrix = cmds.getAttr(tmp_child_jnt + '.matrix')
                cmds.setAttr(ctrl + '.offsetParentMatrix', child_matrix, type='matrix')
                cmds.delete(tmp_parent_jnt)
        #if offsetParentMatrix doesn't exist
        else:
            self.reset_to_origin(ctrl)
            # create offset group
            off_grp = cmds.createNode('transform', name=ctrl + '_OFF_GRP')

            # move offset group to joint position, parent ctrl to it, zero channels
            cmds.xform(off_grp, worldSpace=True, translation=jnt_pos, rotation=jnt_rot)
            if parent_node:
                cmds.parent(off_grp, parent_node[0])

        # move the control back into place
        cmds.xform(ctrl, worldSpace=True, translation=ctrl_pos)
        cmds.xform(ctrl, worldSpace=True, rotation=ctrl_rot)

        # parent control to offset group, if it exists
        if off_grp:
            cmds.parent(ctrl, off_grp)

        # freeze transforms again, then move pivot to match joint's
        if snap_align:
            self.reset_transforms(ctrl)
        else:
            cmds.makeIdentity(ctrl, apply=True, translate=True, rotate=True,
                              scale=False, normal=False)
        cmds.xform(ctrl, worldSpace=True, pivots=jnt_pos)

        # delete construction history
        if delete_history:
            cmds.delete(ctrl, ch=True)

        if off_grp:
            return off_grp
        else:
            return ctrl


    def reset_to_origin(self, node, node_pos=False):
        # get the node's position
        if not node_pos:
            node_pos = cmds.xform(node, query=True, worldSpace=True, rotatePivot=True)

        # freeze translation
        cmds.makeIdentity(node, apply=True, translate=True, rotate=False,
                          scale=False, normal=False)

        # offset to origin
        node_offset = [p * -1 for p in node_pos]
        cmds.xform(node, worldSpace=True, translation=node_offset)

        # set rotation to 0, then freeze all transforms
        cmds.setAttr(node + '.rotate', 0, 0, 0)
        cmds.makeIdentity(node, apply=True, translate=True, rotate=True,
                          scale=False, normal=False)

    def reset_transforms(self, nodes):
        '''
        Reset the transformations
        Returns:

        '''


        if not nodes:
            nodes = cmds.ls(selection=True)

        # if nodes isn't a list, make it one
        if not isinstance(nodes, list):
            nodes = [nodes]

        for node in nodes:
            cmds.setAttr(node + '.translate', 0, 0, 0)
            cmds.setAttr(node + '.rotate', 0, 0, 0)
            cmds.setAttr(node + '.scale', 1, 1, 1)

    def curve_control(self,point_list, name, degree=1):
        '''
        This function returns the curve from the points provided.
        Args:
            name:
            degree:

        Returns:

        '''

        #create curve from the points and rename the shape
        crv = cmds.curve(degree=degree, editPoint=point_list, name=name)
        shp = cmds.listRelatives(crv, shapes=True)[0]
        cmds.rename(shp, crv + 'Shape')

        #return the curve
        return crv

    def blend_chains(self, ik_chain, fk_chain, bind_chain):
        '''
        This function returns the atrribute created for blend
        Args:
            ik_chain:
            fk_chain:
            bind_chain:

        Returns:

        '''

        #going through each chain
        for ik, fk, bind in zip(ik_chain, fk_chain, bind_chain):
            for attr in ['translate', 'rotate', 'scale']:
                #blend node for each attribute using blend colors node and both ik and fk chain
                bcn = cmds.createNode('blendColors', name= bind.replace('bind_JNT', attr + '_BCN'))
                cmds.connectAttr(ik + '.' + attr, bcn + '.color1')
                cmds.connectAttr(fk + '.' + attr, bcn + '.color2')


                cmds.connectAttr('rig_settings_CTRL.fkIk', bcn + '.blender')
                cmds.connectAttr(bcn + '.output', bind + '.' + attr)


    def add_ik_stretch(self, ik_chain, base_ctrl, local_ctrl, world_ctrl, primary_axis):
        '''

        Args:
            ik_chain:
            base_ctrl:
            local_ctrl:
            world_ctrl:
            primary_axis:

        Returns:

        '''
        base_name = 'rig'

        # creating noes for measuring stretch
        limb_dst = cmds.createNode('distanceBetween', name=base_name + "_DST")
        limb_cnd = cmds.createNode('condition', name=base_name + '_CND')
        start_loc = cmds.spaceLocator(name=base_name + "_start_LOC")[0]
        end_loc = cmds.spaceLocator(name=base_name + "_end_LOC")[0]
        stretch_mdn = cmds.createNode('multiplyDivide', name=base_name + '_stretch_MDN')

        # calculate length
        total_count = len(ik_chain)
        count = 0

        total_length = 0

        for ik in ik_chain:
            if (count == total_count - 1):
                break
            length_a = self.distance_between(ik, ik_chain[count + 1])
            total_length = length_a + total_length
            count = count + 1

        #measure limb length
        cmds.pointConstraint(base_ctrl, start_loc, mo=False)
        cmds.pointConstraint(local_ctrl, end_loc, mo=False)
        cmds.connectAttr(start_loc + '.worldMatrix[0]', limb_dst + '.inMatrix1')
        cmds.connectAttr(end_loc + '.worldMatrix[0]', limb_dst + '.inMatrix2')

        #calculate length ratio
        cmds.connectAttr(limb_dst + '.distance', stretch_mdn + '.input1X')
        cmds.setAttr(stretch_mdn + '.input2X', total_length)
        cmds.setAttr(stretch_mdn + '.operation', 2)

        cmds.connectAttr(limb_dst + '.distance', limb_cnd + '.firstTerm')
        cmds.connectAttr(stretch_mdn + '.outputX', limb_cnd + '.colorIfTrueR')
        cmds.setAttr(limb_cnd + '.secondTerm', total_length)
        cmds.setAttr(limb_cnd + '.operation', 3)

        # toggle stretch
        cmds.addAttr(world_ctrl, attributeType='double', min=0, max=1, dv=1,
                     keyable=True, longName="stretch")
        up_name = "up_rig"
        low_name = "low_rig"

        cmds.addAttr(world_ctrl, attributeType="double", dv=1, min=0.001, keyable=True, longName=up_name)
        cmds.addAttr(world_ctrl, attributeType="double", dv=1, min=0.001, keyable=True, longName=low_name)
        stretch_bta = cmds.createNode('blendTwoAttr', name=base_name + '_stretch_BTA')

        cmds.setAttr(stretch_bta + '.input[0]', 1)
        cmds.connectAttr(limb_cnd + '.outColorR', stretch_bta + '.input[1]')
        cmds.connectAttr(world_ctrl + '.stretch', stretch_bta + '.attributesBlender')

        up_pma = cmds.createNode('plusMinusAverage', name=up_name + '_PMA')
        lo_pma = cmds.createNode('plusMinusAverage', name=low_name + '_PMA')
        cmds.connectAttr(world_ctrl + '.' + up_name, up_pma + '.input1D[0]')
        cmds.connectAttr(world_ctrl + '.' + low_name, lo_pma + '.input1D[0]')

        cmds.connectAttr(stretch_bta + '.output', up_pma + '.input1D[1]')
        cmds.connectAttr(stretch_bta + '.output', lo_pma + '.input1D[1]')
        cmds.setAttr(up_pma + '.input1D[2]', -1)
        cmds.setAttr(lo_pma + '.input1D[2]', -1)

        cmds.connectAttr(up_pma + '.output1D', ik_chain[0] + '.scale' + primary_axis[-1])
        cmds.connectAttr(lo_pma + '.output1D', ik_chain[1] + '.scale' + primary_axis[-1])

        # return dict
        return_dict = {'measure_locs': [start_loc, end_loc],
                       'length_total': total_length,
                       'mdn': stretch_mdn,
                       'cnd': limb_cnd}
        return return_dict

    def add_fk_stretch(self, fk_ctrls, fk_chain, primary_axis):
        '''

        Args:
            fk_ctrls:
            fk_chain:
            primary_axis:

        Returns:

        '''

        #travesing each fk ctrl and add stech attrobute
        for i, ctrl in enumerate(fk_ctrls):
            if not ctrl == fk_ctrls[-1]:
                cmds.addAttr(ctrl, attributeType='double', min=0.001, dv=1, keyable=True, ln="stretch")
                mdl = cmds.createNode('multDoubleLinear', name=ctrl.replace('CTRL', '_stretch_MDL'))

                loc = cmds.spaceLocator(name=fk_chain[i + 1].replace('JNT', 'OFF_LOC'))[0]
                cmds.parent(loc, fk_chain[i])
                self.a_to_b(sel=[loc, fk_chain[i + 1]])

                offset_val = cmds.getAttr(loc + '.translate' + primary_axis[-1])
                cmds.setAttr(mdl + '.input1', offset_val)
                cmds.connectAttr(ctrl + '.stretch', mdl + '.input2')

                cmds.connectAttr(mdl + '.output', loc + '.translate' + primary_axis[-1])
                cmds.connectAttr(ctrl + '.stretch', fk_chain[i] + '.scale' + primary_axis[-1])


                if cmds.objExists(fk_ctrls[i + 1] + '.offsetParentMatrix'):
                    cmds.connectAttr(loc + '.matrix', fk_ctrls[i + 1] + '.offsetParentMatrix')
                else:
                    dcm = cmds.createNode('decomposeMatrix', name=loc + '_DCM')

                    cmds.connectAttr(loc + '.matrix', dcm + '.inputMatrix1')
                    for attr in ['translate', 'rotate', 'scale']:
                        cmds.connectAttr(dcm + '.output' + attr.title(),
                                         fk_ctrls[i + 1] + '_OFF_GRP.' + attr)

    def transfer_pivots(self, origin=False, sel=False):
        '''
        Transfers the pivot of selected object to either origin or first object
        Args:
            origin:
            sel:

        Returns:

        '''

        # if selection is not provided, them select
        if not sel:
            sel = cmds.ls(selection=True)

        # move pivot to origin
        if origin:
            for s in sel:
                cmds.xform(s, worldSpace=True, pivots=(0, 0, 0))

        # move pivot to first selected object
        else:
            first_piv = cmds.xform(sel[0], query=True, worldSpace=True,
                                   rotatePivot=True)
            for s in sel[1:]:
                cmds.xform(s, worldSpace=True, pivots=first_piv)

    def lock_and_hide(self, nodes, attributes_list=None):
        '''
        This function hides the attributes from the selected nodes
        Args:
            attributes_list:

        Returns:

        '''

        #hide attribute list
        if not attributes_list:
            attributes_list = ['translate', 'rotate', 'scale', 'visibility']

        if not isinstance(nodes, list):
            nodes = [nodes]

        for node in nodes:
            for attr in attributes_list:
                if any(t == attr for t in ['translate', 'rotate', 'scale']):
                    [cmds.setAttr(node + '.' + attr + axis, lock=True, keyable=False) for axis in 'XYZ']
                else:
                    [cmds.setAttr(node + '.' + attr, lock=True, keyable=True)]

    def add_guides(self, start, end):
        '''
        Create a guide from start to end vector
        Args:
            start:
            end:

        Returns:

        '''
        start_pos = cmds.xform(start, query=True, worldSpace=True, rotatePivot=True)
        end_pos = cmds.xform(end, query=True, worldSpace=True, rotatePivot=True)

        gde = self.curve_control([start_pos, end_pos], name=start + '_GDE')
        start_cls = cmds.cluster(gde + '.cv[0]', name=start + '_CLS')[1]
        end_cls = cmds.cluster(gde + '.cv[1]', name=end + '_CLS')[1]

        cmds.pointConstraint(start, start_cls)
        cmds.pointConstraint(end, end_cls)

        cmds.setAttr(gde + '.template', True)
        cmds.setAttr(gde + '.inheritsTransform', False)

        return [[start_cls, end_cls], gde]

#create instance of the class
rigChainInst = rigChains ()

