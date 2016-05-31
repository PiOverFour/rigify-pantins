import bpy

from ...utils import copy_bone
from ...utils import make_deformer_name, strip_org
from ...utils import create_bone_widget, create_widget, create_cube_widget
from ...utils import connected_children_names, has_connected_children

from . import pantin_utils

class Rig:
    def __init__(self, obj, bone_name, params):
        self.obj = obj
        self.params = params

        self.org_bones = [bone_name] + connected_children_names(self.obj, bone_name)

    def generate(self):
        bpy.ops.object.mode_set(mode='EDIT')
        
        ctrl_chain = []
        # def_chain = []

        eb = self.obj.data.edit_bones

        # if self.params.duplicate_lr:
        #     sides = ['.L', '.R']
        # else:
        sides = [self.params.side]
        if sides[0] == '.C':
            sides[0] = ''

        for s in sides:
            for i, b in enumerate(self.org_bones):
                # Control bones
                ctrl_bone = copy_bone(self.obj, b)
                ctrl_bone_e = eb[ctrl_bone]

                # Name
                ctrl_bone_e.name = strip_org(b) + s

                # Parenting
                if i == 0:
                    # First bone
                    # TODO Check if parent still exists, else check if .L / .R exists, else do nothing
                    # TODO Choose Parent's side in UI(L/R)
                    if eb[b].parent is not None:
                        bone_parent_name = strip_org(eb[b].parent.name) + s
                        ctrl_bone_e.parent = eb[bone_parent_name]
                    else:
                        ctrl_bone_e.parent = eb['MCH-Flip']
                else:
                    # The rest
                    ctrl_bone_e.parent = eb[ctrl_chain[-1]]

                # Add to list
                ctrl_chain += [ctrl_bone_e.name]

                # Def bones
                def_bone = pantin_utils.create_deformation(self.obj, b, self.params.mutable_order, self.params.member_Z_index, self.params.first_bone_Z_index + i)
                # def_chain.append(def_bone)

            bpy.ops.object.mode_set(mode='OBJECT')
            pb = self.obj.pose.bones

            # Constraints
            for org, ctrl in zip(self.org_bones, ctrl_chain):
                con = pb[org].constraints.new('COPY_TRANSFORMS')
                con.name = "copy_transforms"
                con.target = self.obj
                con.subtarget = ctrl
        
def add_parameters(params):
    params.member_Z_index = bpy.props.FloatProperty(name="Indice Z membre", default=0.0, description="Définit l'ordre des membres dans l'espace")
    params.first_bone_Z_index = bpy.props.FloatProperty(name="Indice Z premier os", default=0.0, description="Définit l'ordre des os dans l'espace")
    params.mutable_order = bpy.props.BoolProperty(name="Ordre change", default=True, description="Ce membre peut changer de profondeur")
    # params.duplicate_lr = bpy.props.BoolProperty(name="Duplicate LR",
    #                                              default=True,
    #                                              description="Create two limbs for left and right")
    params.side = bpy.props.EnumProperty(name="Side",
                                         default='.C',
                                         description="If the limb is not to be duplicated, choose its side",
                                         items=(('.L', 'Left', ""),
                                                ('.C', 'Center', ""),
                                                ('.R', 'Right', ""),
                                                ))
    params.layers = bpy.props.BoolVectorProperty(size=32,
                                                       description="Layers for the object")

def parameters_ui(layout, params):
    """ Create the ui for the rig parameters.
    """
    r = layout.row()
    r.prop(params, "member_Z_index")
    r.prop(params, "first_bone_Z_index")
    r = layout.row()
    r.prop(params, "mutable_order")
    # r = layout.row()
    # r.prop(params, "duplicate_lr")
    # if not params.duplicate_lr:
    r = layout.row()
    r.prop(params, "side", expand=True)

    # Layers
    r = layout.row()
    # r.label("Layers")
    col = r.column(align=True)
    row = col.row(align=True)
    row.prop(params, "right_layers", index=0, toggle=True, text="")
    row.prop(params, "right_layers", index=1, toggle=True, text="")
    row.prop(params, "right_layers", index=2, toggle=True, text="")
    row.prop(params, "right_layers", index=3, toggle=True, text="")
    row.prop(params, "right_layers", index=4, toggle=True, text="")
    row.prop(params, "right_layers", index=5, toggle=True, text="")
    row.prop(params, "right_layers", index=6, toggle=True, text="")
    row.prop(params, "right_layers", index=7, toggle=True, text="")
    row = col.row(align=True)
    row.prop(params, "right_layers", index=16, toggle=True, text="")
    row.prop(params, "right_layers", index=17, toggle=True, text="")
    row.prop(params, "right_layers", index=18, toggle=True, text="")
    row.prop(params, "right_layers", index=19, toggle=True, text="")
    row.prop(params, "right_layers", index=20, toggle=True, text="")
    row.prop(params, "right_layers", index=21, toggle=True, text="")
    row.prop(params, "right_layers", index=22, toggle=True, text="")
    row.prop(params, "right_layers", index=23, toggle=True, text="")
    
    col = r.column(align=True)
    row = col.row(align=True)
    row.prop(params, "right_layers", index=8, toggle=True, text="")
    row.prop(params, "right_layers", index=9, toggle=True, text="")
    row.prop(params, "right_layers", index=10, toggle=True, text="")
    row.prop(params, "right_layers", index=11, toggle=True, text="")
    row.prop(params, "right_layers", index=12, toggle=True, text="")
    row.prop(params, "right_layers", index=13, toggle=True, text="")
    row.prop(params, "right_layers", index=14, toggle=True, text="")
    row.prop(params, "right_layers", index=15, toggle=True, text="")
    row = col.row(align=True)
    row.prop(params, "right_layers", index=24, toggle=True, text="")
    row.prop(params, "right_layers", index=25, toggle=True, text="")
    row.prop(params, "right_layers", index=26, toggle=True, text="")
    row.prop(params, "right_layers", index=27, toggle=True, text="")
    row.prop(params, "right_layers", index=28, toggle=True, text="")
    row.prop(params, "right_layers", index=29, toggle=True, text="")
    row.prop(params, "right_layers", index=30, toggle=True, text="")
    row.prop(params, "right_layers", index=31, toggle=True, text="")

def create_sample(obj):
    # generated by rigify.utils.write_metarig
    bpy.ops.object.mode_set(mode='EDIT')
    arm = obj.data

    bones = {}