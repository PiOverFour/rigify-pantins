# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from rna_prop_ui import rna_idprop_ui_prop_get

from rigify.utils import make_mechanism_name, make_deformer_name, strip_org
from rigify.utils import create_bone_widget, create_widget, create_cube_widget
from rigify.utils import connected_children_names, has_connected_children

from . import pantin_utils

from .pantin_template import (UI_IMPORTS, PANTIN_UTILS, PANTIN_REGISTER,
                              REGISTER_PANTIN_DRIVERS, REGISTER_PANTIN_PROPS)

script = """
head = "%s"
if is_selected(head):
    layout.prop(pose_bones[head], \
'["follow"]', \
text="Follow (" + head + ")", \
slider=True)
"""


class Rig:
    def __init__(self, obj, bone_name, params):
        self.obj = obj
        self.params = params

        self.neck = bone_name
        self.head = connected_children_names(self.obj, bone_name)[0]

        self.org_bones = [self.neck, self.head]

    def generate(self):
        bpy.ops.object.mode_set(mode='EDIT')
        ui_script = ""

        ctrl_chain = []
        follow_chain = []

        eb = self.obj.data.edit_bones
        for i, b in enumerate(self.org_bones):

            target = eb[b].parent_recursive[-1].name
            target = strip_org(target)
            ctrl_bone, follow_bone = pantin_utils.make_follow(self.obj, b, target)

            ui_script += script % (ctrl_bone)

            # Add to list
            ctrl_chain += [ctrl_bone]

            eb[ctrl_bone].name = ctrl_bone

            # Def bones
            def_bone = pantin_utils.create_deformation(
                self.obj,
                b,
                self.params.flip_switch,
                member_index=self.params.Z_index,
                bone_index=i)

        # Parenting
        if self.params.detach:
            eb[self.head].use_connect = False

        bpy.ops.object.mode_set(mode='OBJECT')
        pb = self.obj.pose.bones

        # Widgets
        global_scale = self.obj.dimensions[2]
        member_factor = 0.08
        widget_size = global_scale * member_factor

        neck = ctrl_chain[0]
        head = ctrl_chain[1]

        pantin_utils.create_capsule_widget(
            self.obj, neck, length=widget_size, width=widget_size*0.1)
        pantin_utils.create_aligned_circle_widget(
            self.obj, head, radius=widget_size, head_tail=0.5)

        # Constraints

        for org, ctrl in zip(self.org_bones, ctrl_chain):
            con = pb[org].constraints.new('COPY_TRANSFORMS')
            con.name = "copy_transforms"
            con.target = self.obj
            con.subtarget = ctrl

        con = pb[neck].constraints.new('LIMIT_ROTATION')
        con.name = "limit_rotation"
        con.use_limit_z = True
        con.min_z = -1.14
        con.max_z = 1.5
        con.owner_space = 'LOCAL'

        con = pb[head].constraints.new('LIMIT_ROTATION')
        con.name = "limit_rotation"
        con.use_limit_z = True
        con.min_z = -0.5
        con.max_z = 0.68
        con.owner_space = 'LOCAL'

        return {
            'script': [ui_script],
            'imports': UI_IMPORTS,
            'utilities': PANTIN_UTILS,
            'register': PANTIN_REGISTER,
            'register_drivers': REGISTER_PANTIN_DRIVERS,
            'register_props': REGISTER_PANTIN_PROPS,
            }


def add_parameters(params):
    params.Z_index = bpy.props.FloatProperty(
        name="Z index", default=0.0, description="Defines member's Z order")
    params.flip_switch = bpy.props.BoolProperty(
        name="Flip Switch", default=False,
        description="This member may change depth when flipped")
    params.detach = bpy.props.BoolProperty(
        name="Detach Head", default=False,
        description="Off with her head!")


def parameters_ui(layout, params):
    """ Create the ui for the rig parameters.
    """
    r = layout.row()
    r.prop(params, "Z_index")
    r = layout.row()
    r.prop(params, "flip_switch")
    r = layout.row()
    r.prop(params, "detach")


def create_sample(obj):
    # generated by rigify.utils.write_metarig
    bpy.ops.object.mode_set(mode='EDIT')
    arm = obj.data

    bones = {}

    bone = arm.edit_bones.new('Neck')
    bone.head[:] = 0.0005, 0.0000, 1.4038
    bone.tail[:] = 0.0271, 0.0000, 1.4720
    bone.roll = -2.7688
    bone.use_connect = False
    bones['Neck'] = bone.name
    bone = arm.edit_bones.new('Head')
    bone.head[:] = 0.0271, 0.0000, 1.4720
    bone.tail[:] = 0.0592, 0.0000, 1.6173
    bone.roll = -2.9241
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['Neck']]
    bones['Head'] = bone.name
    bone = arm.edit_bones.new('Jaw')
    bone.head[:] = 0.0223, 0.0000, 1.4938
    bone.tail[:] = 0.0964, 0.0000, 1.4450
    bone.roll = -0.9887
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['Head']]
    bones['Jaw'] = bone.name
    bone = arm.edit_bones.new('Eyelid')
    bone.head[:] = 0.0713, -0.0000, 1.5667
    bone.tail[:] = 0.1014, 0.0000, 1.5618
    bone.roll = -1.4091
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['Head']]
    bones['Eyelid'] = bone.name

    bpy.ops.object.mode_set(mode='OBJECT')
    pbone = obj.pose.bones[bones['Neck']]
    pbone.rigify_type = 'pantin.head'
    pbone.lock_location = (True, True, True)
    pbone.lock_rotation = (True, True, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (True, True, True)
    pbone.rotation_mode = 'XZY'
    try:
        pbone.rigify_parameters.Z_index = 0.0
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.flip_switch = False
    except AttributeError:
        pass
    pbone = obj.pose.bones[bones['Head']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, True)
    pbone.lock_rotation = (True, True, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (True, True, True)
    pbone.rotation_mode = 'XZY'
    pbone = obj.pose.bones[bones['Jaw']]
    pbone.rigify_type = ''
    pbone.lock_location = (True, True, True)
    pbone.lock_rotation = (True, True, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (True, True, True)
    pbone.rotation_mode = 'XZY'
    pbone = obj.pose.bones[bones['Eyelid']]
    pbone.rigify_type = ''
    pbone.lock_location = (True, True, True)
    pbone.lock_rotation = (True, True, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'XZY'

    bpy.ops.object.mode_set(mode='EDIT')
    for bone in arm.edit_bones:
        bone.select = False
        bone.select_head = False
        bone.select_tail = False
    for b in bones:
        bone = arm.edit_bones[bones[b]]
        bone.select = True
        bone.select_head = True
        bone.select_tail = True
        arm.edit_bones.active = bone
