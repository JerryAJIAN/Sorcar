print("______________________________________________________")
bl_info = {
    "name": "ProcGenMod",
    "author": "Punya Aachman",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "Node Editor",
    "description": "Create procedural meshes using Node Editor",
    "category": "PCG"}

import bpy
import bmesh
import nodeitems_utils

from bpy.types import NodeTree, Node, NodeSocket, Operator
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty, FloatVectorProperty, PointerProperty, BoolVectorProperty
from nodeitems_utils import NodeCategory, NodeItem

class PcgNodeTree(NodeTree):
    bl_idname = 'PcgNodeTree'
    bl_label = 'PCG node tree'
    bl_icon = 'NODETREE'
class PcgNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'PcgNodeTree'
class PcgNode:
    mesh = StringProperty()
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'PcgNodeTree'
    def update_value(self, context):
        bpy.ops.pcg.refresh_mesh_op()
        return None

class PcgInputNode(PcgNode):
    prop_location = FloatVectorProperty(name="Location", update=PcgNode.update_value)
    prop_rotation = FloatVectorProperty(name="Rotation", subtype="EULER", unit="ROTATION", update=PcgNode.update_value)
    def init(self, context):
        self.outputs.new("MeshSocket", "Mesh")
        self.hide = True
        self.use_custom_color = True
        self.color = (0.5, 0.0, 0.0)
    def execute(self):
        if (not self.mesh == ""):
            try:
                bpy.data.objects.remove(bpy.data.objects[self.mesh])
            except:
                print("Debug: " + self.name + ": Mesh object non-existant")
        self.functionality()
        self.mesh = bpy.context.active_object.name
        return self.mesh
    def functionality(self):
        print("Debug: PcgInputNode: Main functionality of the node")
class PcgTransformNode(PcgNode):
    def init(self, context):
        self.inputs.new("UniversalSocket", "Mesh")
        self.outputs.new("UniversalSocket", "Mesh")
        self.hide = True
        self.use_custom_color = True
        self.color = (0.0, 0.5, 0.0)
    def execute(self):
        if (not self.inputs[0].is_linked):
            print("Debug: " + self.name + ": Not linked")
            return ""
        self.mesh = self.inputs[0].links[0].from_node.execute()
        if (self.mesh == ""):
            print("Debug: " + self.name + ": Empty object recieved")
            return ""
        self.functionality()
        return self.mesh
    def functionality(self):
        print("Debug: PcgTransformNode: Main functionality of the node")
class PcgModifierNode(PcgNode):
    def init(self, context):
        self.inputs.new("MeshSocket", "Mesh")
        self.outputs.new("MeshSocket", "Mesh")
        self.hide = True
        self.use_custom_color = True
        self.color = (0.0, 0.0, 0.5)
    def execute(self):
        if (not self.inputs[0].is_linked):
            print("Debug: " + self.name + ": Not linked")
            return ""
        self.mesh = self.inputs[0].links[0].from_node.execute()
        if (self.mesh == ""):
            print("Debug: " + self.name + ": Empty object recieved")
            return ""
        bpy.context.scene.objects.active = bpy.data.objects[self.mesh]
        if (not self.functionality()):
            print("Debug: " + self.name + ": Error: Modifier failed to execute")
            return ""
        self.name = bpy.data.objects[self.mesh].modifiers[0].name
        bpy.ops.object.modifier_apply(modifier=bpy.data.objects[self.mesh].modifiers[0].name)
        return self.mesh
    def functionality(self):
        print("Debug: PcgModifierNode: Main functionality of the node")
        return True
class PcgSelectionNode(PcgNode):
    def init(self, context):
        self.inputs.new("ComponentSocket", "Component")
        self.outputs.new("ComponentSocket", "Component")
        self.hide = True
        self.use_custom_color = True
        self.color = (0.0, 0.5, 0.5)
    def execute(self):
        if (not self.inputs[0].is_linked):
            print("Debug: " + self.name + ": Not linked")
            return ""
        self.mesh = self.inputs[0].links[0].from_node.execute()
        if (self.mesh == ""):
            print("Debug: " + self.name + ": Empty object recieved")
            return ""
        self.functionality()
        return self.mesh
    def functionality(self):
        print("Debug: PcgSelectionNode: Main functionality of the node")
class PcgOperatorNode(PcgNode):
    def init(self, context):
        self.inputs.new("ComponentSocket", "Component")
        self.outputs.new("ComponentSocket", "Component")
        self.hide = True
        self.use_custom_color = True
        self.color = (0.5, 0.0, 0.5)
    def execute(self):
        if (not self.inputs[0].is_linked):
            print("Debug: " + self.name + ": Not linked")
            return ""
        self.mesh = self.inputs[0].links[0].from_node.execute()
        if (self.mesh == ""):
            print("Debug: " + self.name + ": Empty object recieved")
            return ""
        self.functionality()
        return self.mesh
    def functionality(self):
        print("Debug: PcgOperationNode: Main functionality of the node")
class PcgSettingNode(PcgNode):
    def init(self, context):
        self.inputs.new("UniversalSocket", "")
        self.outputs.new("UniversalSocket", "")
        self.hide = True
        self.use_custom_color = True
        self.color = (0.5, 0.5, 0.0)
    def execute(self):
        if (not self.inputs[0].is_linked):
            print("Debug: " + self.name + ": Not linked")
            return ""
        self.mesh = self.inputs[0].links[0].from_node.execute()
        if (self.mesh == ""):
            print("Debug: " + self.name + ": Empty object recieved")
            return ""
        self.functionality()
        return self.mesh
    def functionality(self):
        print("Debug: PcgSettingNode: Main functionality of the node")


########################### SOCKETS ##########################
class MeshSocket(NodeSocket):
    bl_idname = "MeshSocket"
    bl_label = "Mesh"

    def draw(self, context, layout, node, text):
        if (node.mesh == ""):
            layout.label(self.name)
        else:
            layout.label(node.mesh)

    def draw_color(self, context, node):
        return 1, 1, 1, 1
class ComponentSocket(NodeSocket):
    bl_idname = "ComponentSocket"
    bl_label = "Component"

    def draw(self, context, layout, node, text):
        layout.label(self.name)

    def draw_color(self, context, node):
        return 0, 0, 0, 1
class UniversalSocket(NodeSocket):
    bl_idname = "UniversalSocket"
    bl_label = "Universal"

    def draw(self, context, layout, node, text):
        layout.label("")

    def draw_color(self, context, node):
        return 1, 0, 0, 1
##############################################################


######################### HELPER OPS #########################
class RealtimeMeshOp(Operator):
    bl_idname = "pcg.realtime_mesh_op"
    bl_label = "Realtime Mesh Update"
    bl_options = {"REGISTER", "UNDO"}

    node = None

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "NODE_EDITOR"

    def execute(self, context):
        bpy.ops.pcg.refresh_mesh_op()
        return {'FINISHED'}

    def modal(self, context, event):
        if (event.type == "ESC"):
            print("Debug: RealtimeMeshOp: STOP")
            return {'FINISHED'}
        elif (event.type == "LEFTMOUSE"):
            node = context.active_node
            if (not node == self.node):
                print("Debug: RealtimeMeshOp: Active node changed")
                self.node = node
                self.execute(context)
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        print("Debug: RealtimeMeshOp: START")
        return {'RUNNING_MODAL'}
class SaveSelectionOp(Operator):
    bl_idname = "pcg.save_selection_op"
    bl_label = "Execute MeshNode"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "NODE_EDITOR"
    
    def execute(self, context):
        node = context.active_node
        if (node == None):
            print("Debug: SaveSelectionOp: No Active Node")
            return {'CANCELLED'}
        node.save_selection()
        return {'FINISHED'}
class RefreshMeshOp(Operator):
    bl_idname = "pcg.refresh_mesh_op"
    bl_label = "Refresh Mesh Update"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "NODE_EDITOR"

    def execute(self, context):
        node = context.active_node
        if (not node == None):
            node.execute()
            return {'FINISHED'}
        print("Debug: RefreshMeshOp: No active node")
        return {'CANCELLED'}
##############################################################


########################### NODES ############################
class PlaneNode(Node, PcgInputNode):
    bl_idname = "PlaneNode"
    bl_label = "Plane"
    
    prop_radius = FloatProperty(name="Radius", default=1.0, min=0, update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.column().prop(self, "prop_radius")
        layout.column().separator()
        layout.row().prop(self, "prop_location")
        layout.row().prop(self, "prop_rotation")
    
    def functionality(self):
        bpy.ops.mesh.primitive_plane_add(radius=self.prop_radius, location=self.prop_location, rotation=self.prop_rotation)
class CubeNode(Node, PcgInputNode):
    bl_idname = "CubeNode"
    bl_label = "Cube"
    
    prop_radius = FloatProperty(name="Radius", default=1.0, min=0.0, update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.column().prop(self, "prop_radius")
        layout.column().separator()
        layout.row().prop(self, "prop_location")
        layout.row().prop(self, "prop_rotation")
    
    def functionality(self):
        bpy.ops.mesh.primitive_cube_add(radius=self.prop_radius, location=self.prop_location, rotation=self.prop_rotation)
class SphereNode(Node, PcgInputNode):
    bl_idname = "SphereNode"
    bl_label = "Sphere"
    
    prop_segments = IntProperty(name="Segments", default=32, min=3, max=10000, update=PcgNode.update_value)
    prop_rings = IntProperty(name="Ring Count", default=16, min=3, max=10000, update=PcgNode.update_value)
    prop_size = FloatProperty(name="Size", default=1.0, min=0.0, update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.column().prop(self, "prop_segments")
        layout.column().prop(self, "prop_rings")
        layout.column().prop(self, "prop_size")
        layout.column().separator()
        layout.row().prop(self, "prop_location")
        layout.row().prop(self, "prop_rotation")
    
    def functionality(self):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=self.prop_segments, ring_count=self.prop_rings, size=self.prop_size, location=self.prop_location, rotation=self.prop_rotation)
class CylinderNode(Node, PcgInputNode):
    bl_idname = "CylinderNode"
    bl_label = "Cylinder"
    
    prop_vertices = IntProperty(name="Vertices", default=32, min=3, max=1000000, update=PcgNode.update_value)
    prop_radius = FloatProperty(name="Radius", default=1.0, min=0, update=PcgNode.update_value)
    prop_depth = FloatProperty(name="Depth", default=2.0, min=0, update=PcgNode.update_value)
    prop_end = EnumProperty(name="End Fill Type", items=[("NOTHING", "Nothing", "Don’t fill at all."), ("NGON", "Ngon", "Use ngons"), ("TRIFAN", "Triangle Fan", "Use triangle fans.")], default="NGON", update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.column().prop(self, "prop_vertices")
        layout.column().prop(self, "prop_radius")
        layout.column().prop(self, "prop_depth")
        layout.column().prop(self, "prop_end")
        layout.column().separator()
        layout.row().prop(self, "prop_location")
        layout.row().prop(self, "prop_rotation")
    
    def functionality(self):
        bpy.ops.mesh.primitive_cylinder_add(vertices=self.prop_vertices, radius=self.prop_radius, depth=self.prop_depth, end_fill_type=self.prop_end, location=self.prop_location, rotation=self.prop_rotation)
class ConeNode(Node, PcgInputNode):
    bl_idname = "ConeNode"
    bl_label = "Cone"
    
    prop_vertices = IntProperty(name="Vertices", default=32, min=3, max=1000000, update=PcgNode.update_value)
    prop_radius1 = FloatProperty(name="Radius 1", default=1.0, min=0.0, update=PcgNode.update_value)
    prop_radius2 = FloatProperty(name="Radius 2", default=0.0, min=0.0, update=PcgNode.update_value)
    prop_depth = FloatProperty(name="Depth", default=2.0, min=0, update=PcgNode.update_value)
    prop_end = EnumProperty(name="End Fill Type", items=[("NOTHING", "Nothing", "Don’t fill at all."), ("NGON", "Ngon", "Use ngons"), ("TRIFAN", "Triangle Fan", "Use triangle fans.")], default="NGON", update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.column().prop(self, "prop_vertices")
        layout.column().prop(self, "prop_radius1")
        layout.column().prop(self, "prop_radius2")
        layout.column().prop(self, "prop_depth")
        layout.column().prop(self, "prop_end")
        layout.column().separator()
        layout.row().prop(self, "prop_location")
        layout.row().prop(self, "prop_rotation")
    
    def functionality(self):
        bpy.ops.mesh.primitive_cone_add(vertices=self.prop_vertices, radius1=self.prop_radius1, radius2=self.prop_radius2, depth=self.prop_depth, end_fill_type=self.prop_end, location=self.prop_location, rotation=self.prop_rotation)
class TorusNode(Node, PcgInputNode):
    bl_idname = "TorusNode"
    bl_label = "Torus"
    
    prop_major_segments = IntProperty(name="Major Segment", default=48, min=3, max=256, update=PcgNode.update_value)
    prop_minor_segments = IntProperty(name="Minor Segment", default=12, min=3, max=256, update=PcgNode.update_value)
    prop_mode = EnumProperty(name="Mode", items=[("MAJOR_MINOR", "Major/Minor", "Use the major/minor radii for torus dimensions."), ("EXT_INT", "Exterior/Interior", "Use the exterior/interior radii for torus dimensions.")], default="MAJOR_MINOR", update=PcgNode.update_value)
    prop_major_radius = FloatProperty(name="Major Radius", default=1.0, min=0.01, max=100, update=PcgNode.update_value)
    prop_minor_radius = FloatProperty(name="Minor Radius", default=0.25, min=0.01, max=100, update=PcgNode.update_value)
    prop_ext_radius = FloatProperty(name="Exterior Radius", default=1.25, min=0.01, max=100, update=PcgNode.update_value)
    prop_int_radius = FloatProperty(name="Interior Radius", default=0.75, min=0.01, max=100, update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.column().prop(self, "prop_major_segments")
        layout.column().prop(self, "prop_minor_segments")
        layout.column().prop(self, "prop_mode")
        if (self.prop_mode == "MAJOR_MINOR"):
            layout.column().prop(self, "prop_major_radius")
            layout.column().prop(self, "prop_minor_radius")
        else:
            layout.column().prop(self, "prop_ext_radius")
            layout.column().prop(self, "prop_int_radius")
        layout.column().separator()
        layout.row().prop(self, "prop_location")
        layout.row().prop(self, "prop_rotation")
    
    def functionality(self):
        bpy.ops.mesh.primitive_torus_add(major_segments=self.prop_major_segments, minor_segments=self.prop_minor_segments, mode=self.prop_mode, major_radius = self.prop_major_radius, minor_radius = self.prop_minor_radius, abso_major_rad = self.prop_ext_radius, abso_minor_rad = self.prop_int_radius, location=self.prop_location, rotation=self.prop_rotation)

class LocationNode(Node, PcgTransformNode):
    bl_idname = "LocationNode"
    bl_label = "Set Location"
    
    prop_location = FloatVectorProperty(name="Location", update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.column().prop(self, "prop_location")
    
    def functionality(self):
        bpy.data.objects[self.mesh].location = self.prop_location
class RotationNode(Node, PcgTransformNode):
    bl_idname = "RotationNode"
    bl_label = "Set Rotation"
    
    prop_rotation = FloatVectorProperty(name="Rotation", subtype="EULER", unit="ROTATION", update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.column().prop(self, "prop_rotation")
    
    def functionality(self):
        bpy.data.objects[self.mesh].rotation_euler = self.prop_rotation
class ScaleNode(Node, PcgTransformNode):
    bl_idname = "ScaleNode"
    bl_label = "Set Scale"
    
    prop_scale = FloatVectorProperty(name="Scale", default=(1.0, 1.0, 1.0), update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.column().prop(self, "prop_scale")
    
    def functionality(self):
        bpy.data.objects[self.mesh].scale = self.prop_scale
class TranslateNode(Node, PcgTransformNode):
    bl_idname = "TranslateNode"
    bl_label = "Translate"

    prop_value = FloatVectorProperty(name="Value", update=PcgNode.update_value)
    prop_constraint_axis = BoolVectorProperty(name="Constraint Axis", update=PcgNode.update_value)
    prop_mirror = BoolProperty(name="Mirror", update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        col = layout.column()
        col.prop(self, "prop_value")
        layout.prop(self, "prop_constraint_axis")
        layout.prop(self, "prop_mirror")
    
    def functionality(self):
        window = bpy.data.window_managers['WinMan'].windows[0]
        screen = window.screen
        area = [i for i in screen.areas if i.type == 'VIEW_3D'][0]
        space = area.spaces[0]
        scene = bpy.data.scenes[0]
        region = [i for i in area.regions if i.type == 'WINDOW'][0]
        override = {'window':window, 'screen':screen, 'area':area, 'space':space, 'scene':scene, 'active_object':bpy.data.objects[self.mesh], 'region':region, 'gpencil_data':bpy.context.gpencil_data}
        bpy.ops.transform.translate(override, value=self.prop_value, constraint_axis=self.prop_constraint_axis, constraint_orientation=space.transform_orientation, mirror=self.prop_mirror, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1.0, snap=False, snap_target='CLOSEST', snap_point=(0.0, 0.0, 0.0), snap_align=False, snap_normal=(0.0, 0.0, 0.0), gpencil_strokes=False, texture_space=False, remove_on_cancel=False, release_confirm=False, use_accurate=False)
class RotateNode(Node, PcgTransformNode):
    bl_idname = "RotateNode"
    bl_label = "Rotate"

    prop_value = FloatProperty(name="Value", subtype="ANGLE", unit="ROTATION", update=PcgNode.update_value)
    prop_axis = FloatVectorProperty(name="Axis", default=(0.0, 0.0, 1.0), update=PcgNode.update_value)
    prop_constraint_axis = BoolVectorProperty(name="Constraint Axis", update=PcgNode.update_value)
    prop_mirror = BoolProperty(name="Mirror", update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_value")
        col = layout.column()
        col.prop(self, "prop_axis")
        layout.prop(self, "prop_constraint_axis")
        layout.prop(self, "prop_mirror")
    
    def functionality(self):
        window = bpy.data.window_managers['WinMan'].windows[0]
        screen = window.screen
        area = [i for i in screen.areas if i.type == 'VIEW_3D'][0]
        space = area.spaces[0]
        scene = bpy.data.scenes[0]
        region = [i for i in area.regions if i.type == 'WINDOW'][0]
        override = {'window':window, 'screen':screen, 'area':area, 'space':space, 'scene':scene, 'active_object':bpy.data.objects[self.mesh], 'region':region, 'gpencil_data':bpy.context.gpencil_data}
        bpy.ops.transform.rotate(override, value=self.prop_value, axis=self.prop_axis, constraint_axis=self.prop_constraint_axis, constraint_orientation=space.transform_orientation, mirror=self.prop_mirror, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1.0, snap=False, snap_target='CLOSEST', snap_point=(0.0, 0.0, 0.0), snap_align=False, snap_normal=(0.0, 0.0, 0.0), gpencil_strokes=False, release_confirm=False, use_accurate=False)
class ResizeNode(Node, PcgTransformNode):
    bl_idname = "ResizeNode"
    bl_label = "Resize"

    prop_value = FloatVectorProperty(name="Value", default=(1.0, 1.0, 1.0), update=PcgNode.update_value)
    prop_constraint_axis = BoolVectorProperty(name="Constraint Axis", update=PcgNode.update_value)
    prop_mirror = BoolProperty(name="Mirror", update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        col = layout.column()
        col.prop(self, "prop_value")
        layout.prop(self, "prop_constraint_axis")
        layout.prop(self, "prop_mirror")
    
    def functionality(self):
        window = bpy.data.window_managers['WinMan'].windows[0]
        screen = window.screen
        area = [i for i in screen.areas if i.type == 'VIEW_3D'][0]
        space = area.spaces[0]
        scene = bpy.data.scenes[0]
        region = [i for i in area.regions if i.type == 'WINDOW'][0]
        override = {'window':window, 'screen':screen, 'area':area, 'space':space, 'scene':scene, 'active_object':bpy.data.objects[self.mesh], 'region':region, 'gpencil_data':bpy.context.gpencil_data}
        bpy.ops.transform.resize(override, value=self.prop_value, constraint_axis=self.prop_constraint_axis, constraint_orientation=space.transform_orientation, mirror=self.prop_mirror, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1.0, snap=False, snap_target='CLOSEST', snap_point=(0.0, 0.0, 0.0), snap_align=False, snap_normal=(0.0, 0.0, 0.0), gpencil_strokes=False, texture_space=False, remove_on_cancel=False, release_confirm=False, use_accurate=False)

class ToComponentNode(Node, PcgNode):
    bl_idname = "ToComponentNode"
    bl_label = "To Component Mode"
    
    prop_selection_type = EnumProperty(name="Component", items=[("FACE", "Faces", ""), ("VERT", "Vertices", ""), ("EDGE", "Edges", "")], default="FACE", update=PcgNode.update_value)
    prop_deselect = BoolProperty(name="Deselect All", default=True, update=PcgNode.update_value)

    def init(self, context):
        self.inputs.new("MeshSocket", "Mesh")
        self.outputs.new("ComponentSocket", "Component")

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_selection_type", expand=True)
        layout.prop(self, "prop_deselect")
    
    def execute(self):
        if (not self.inputs[0].is_linked):
            print("Debug: " + self.name + ": Not linked")
            return ""
        self.mesh = self.inputs[0].links[0].from_node.execute()
        if (self.mesh == ""):
            print("Debug: " + self.name + ": Empty object recieved")
            return ""
        bpy.context.scene.objects.active = bpy.data.objects[self.mesh]
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_mode(type=self.prop_selection_type)
        if (self.prop_deselect):
            bpy.ops.mesh.select_all(action="DESELECT")
        return self.mesh
class ToMeshNode(Node, PcgSelectionNode):
    bl_idname = "ToMeshNode"
    bl_label = "To Mesh Mode"

    def init(self, context):
        self.inputs.new("ComponentSocket", "Component")
        self.outputs.new("MeshSocket", "Mesh")
    
    def execute(self):
        if (not self.inputs[0].is_linked):
            print("Debug: " + self.name + ": Not linked")
            return ""
        self.mesh = self.inputs[0].links[0].from_node.execute()
        if (self.mesh == ""):
            print("Debug: " + self.name + ": Empty object recieved")
            return ""
        bpy.context.scene.objects.active = bpy.data.objects[self.mesh]
        bpy.ops.object.mode_set(mode="OBJECT")
        return self.mesh
class ChangeModeNode(Node, PcgNode):
    bl_idname = "ChangeModeNode"
    bl_label = "Change Mode Mode"
    
    prop_selection_type = EnumProperty(name="Component", items=[("FACE", "Faces", ""), ("VERT", "Vertices", ""), ("EDGE", "Edges", "")], default="FACE", update=PcgNode.update_value)

    def init(self, context):
        self.inputs.new("ComponentSocket", "Component")
        self.outputs.new("ComponentSocket", "Component")

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_selection_type", expand=True)
    
    def execute(self):
        if (not self.inputs[0].is_linked):
            print("Debug: " + self.name + ": Not linked")
            return ""
        self.mesh = self.inputs[0].links[0].from_node.execute()
        if (self.mesh == ""):
            print("Debug: " + self.name + ": Empty object recieved")
            return ""
        bpy.ops.mesh.select_mode(type=self.prop_selection_type)
        return self.mesh

class SelectComponentsManuallyNode(Node, PcgSelectionNode):
    bl_idname = "SelectComponentsManuallyNode"
    bl_label = "Select Mesh Manually Components"
    
    selection_face = StringProperty()
    selection_vert = StringProperty()
    selection_edge = StringProperty()

    def toList(self, string):
        string = string.replace("[", "")
        string = string.replace("]", "")
        list_string = string.rsplit(", ")
        list = []
        for i in list_string:
            if i == "False":
                list.append(False)
            else:
                list.append(True)
        return list

    def save_selection(self):
        if (not self.mesh == ""):
            bpy.ops.object.mode_set(mode="OBJECT")
            self.selection_face = str([i.select for i in bpy.data.objects[self.mesh].data.polygons])
            self.selection_vert = str([i.select for i in bpy.data.objects[self.mesh].data.vertices])
            self.selection_edge = str([i.select for i in bpy.data.objects[self.mesh].data.edges])
            bpy.ops.object.mode_set(mode="EDIT")
            print("Debug: " + self.name + ": Saved components selection")

    def draw_buttons(self, context, layout):
        if (self == self.id_data.nodes.active):
            layout.operator("pcg.save_selection_op", "Save Selection")
        if (not self.mesh == ""):
            layout.label(text="Faces: " + str(len([i for i in bpy.data.objects[self.mesh].data.polygons if i.select == True])) + "/" + str(len(bpy.data.objects[self.mesh].data.polygons)))
            layout.label(text="Vertices: " + str(len([i for i in bpy.data.objects[self.mesh].data.vertices if i.select == True])) + "/" + str(len(bpy.data.objects[self.mesh].data.vertices)))
            layout.label(text="Edges: " + str(len([i for i in bpy.data.objects[self.mesh].data.edges if i.select == True])) + "/" + str(len(bpy.data.objects[self.mesh].data.edges)))
    
    def functionality(self):
        bpy.ops.object.mode_set(mode="OBJECT")
        list_face = self.toList(self.selection_face)
        list_vert = self.toList(self.selection_vert)
        list_edge = self.toList(self.selection_edge)
        if len(list_face) == len(bpy.data.objects[self.mesh].data.polygons):
            for i in range(0, len(bpy.data.objects[self.mesh].data.polygons)):
                bpy.data.objects[self.mesh].data.polygons[i].select = list_face[i]
        if len(list_vert) == len(bpy.data.objects[self.mesh].data.vertices):
            for i in range(0, len(bpy.data.objects[self.mesh].data.vertices)):
                bpy.data.objects[self.mesh].data.vertices[i].select = list_vert[i]
        if len(list_edge) == len(bpy.data.objects[self.mesh].data.edges):
            for i in range(0, len(bpy.data.objects[self.mesh].data.edges)):
                bpy.data.objects[self.mesh].data.edges[i].select = list_edge[i]
        bpy.ops.object.mode_set(mode="EDIT")
class SelectAllNode(Node, PcgSelectionNode):
    bl_idname = "SelectAllNode"
    bl_label = "Select All"

    prop_action = EnumProperty(name="Action", items=[("TOGGLE", "Toggle", ""), ("SELECT", "Select", ""), ("DESELECT", "Deselect", ""), ("INVERT", "Invert", "")], default="TOGGLE", update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_action")
    
    def functionality(self):
        bpy.ops.mesh.select_all(action=self.prop_action)
class SelectAxisNode(Node, PcgSelectionNode):
    bl_idname = "SelectAxisNode"
    bl_label = "Select Axis"

    prop_mode = EnumProperty(name="Mode", items=[("POSITIVE", "Positive", ""), ("NEGATIVE", "Negative", ""), ("ALIGNED", "Aligned", "")], default="POSITIVE", update=PcgNode.update_value)
    prop_axis = EnumProperty(name="Axis", items=[("X_AXIS", "X", ""), ("Y_AXIS", "Y", ""), ("Z_AXIS", "Z", "")], default="X_AXIS", update=PcgNode.update_value)
    prop_threshold = FloatProperty(name="Threshold", default=0.0001, min=0.000001, max=50, update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_mode", expand=True)
        layout.prop(self, "prop_axis")
        layout.prop(self, "prop_threshold")
    
    def functionality(self):
        bpy.ops.mesh.select_axis(mode=self.prop_mode, axis=self.prop_axis, threshold=self.prop_threshold)
class SelectFaceBySidesNode(Node, PcgSelectionNode):
    bl_idname = "SelectFaceBySidesNode"
    bl_label = "Select Face By Sides"

    prop_number = IntProperty(name="Number", default=3, min=3, update=PcgNode.update_value)
    prop_type = EnumProperty(name="Type", items=[("LESS", "Less", ""), ("EQUAL", "Equal", ""), ("GREATER", "Greater", ""), ("NOTEQUAL", "Not Equal", "")], default="EQUAL", update=PcgNode.update_value)
    prop_extend = BoolProperty(name="Extend", default=True, update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_number")
        layout.prop(self, "prop_type")
        layout.prop(self, "prop_extend")
    
    def functionality(self):
        bpy.ops.mesh.select_face_by_sides(number=self.prop_number, type=self.prop_type, extend=self.prop_extend)
class SelectInteriorFaces(Node, PcgSelectionNode):
    bl_idname = "SelectInteriorFaces"
    bl_label = "Select Interior Faces"

    def functionality(self):
        bpy.ops.mesh.select_interior_faces()
class SelectLessNode(Node, PcgSelectionNode):
    bl_idname = "SelectLessNode"
    bl_label = "Select Less"

    prop_face_step = BoolProperty(name="Face Step", default=True, update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_face_step")
    
    def functionality(self):
        bpy.ops.mesh.select_less(use_face_step=self.prop_face_step)
class SelectMoreNode(Node, PcgSelectionNode):
    bl_idname = "SelectMoreNode"
    bl_label = "Select More"

    prop_face_step = BoolProperty(name="Face Step", default=True, update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_face_step")
    
    def functionality(self):
        bpy.ops.mesh.select_more(use_face_step=self.prop_face_step)
class SelectLinkedNode(Node, PcgSelectionNode):
    bl_idname = "SelectLinkedNode"
    bl_label = "Select Linked"

    prop_delimit = EnumProperty(name="Delimit", items=[("NORMAL", "Normal", ""), ("MATERIAL", "Material", ""), ("SEAM", "Seam", ""), ("SHARP", "Sharp", ""), ("UV", "UV", "")], default="SEAM", update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_delimit")
    
    def functionality(self):
        bpy.ops.mesh.select_linked(delimit={self.prop_delimit})
class SelectLooseNode(Node, PcgSelectionNode):
    bl_idname = "SelectLooseNode"
    bl_label = "Select Loose"

    prop_extend = BoolProperty(name="Extend", update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_extend")
    
    def functionality(self):
        bpy.ops.mesh.select_loose(extend=self.prop_extend)
class SelectMirrorNode(Node, PcgSelectionNode):
    bl_idname = "SelectMirrorNode"
    bl_label = "Select Mirror"

    prop_axis = EnumProperty(name="Axis", items=[("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", "")], default="X", update=PcgNode.update_value)
    prop_extend = BoolProperty(name="Extend", update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_axis", expand=True)
        layout.prop(self, "prop_extend")
    
    def functionality(self):
        bpy.ops.mesh.select_mirror(axis={self.prop_axis}, extend=self.prop_extend)
class SelectNextItemNode(Node, PcgSelectionNode):
    bl_idname = "SelectNextItemNode"
    bl_label = "Select Next Item"

    def functionality(self):
        bpy.ops.mesh.select_next_item()
class SelectPrevItemNode(Node, PcgSelectionNode):
    bl_idname = "SelectPrevItemNode"
    bl_label = "Select Previous Item"

    def functionality(self):
        bpy.ops.mesh.select_prev_item()
class SelectNonManifoldNode(Node, PcgSelectionNode):
    bl_idname = "SelectNonManifoldNode"
    bl_label = "Select Non-Manifold"

    prop_extend = BoolProperty(name="Extend", default=True, update=PcgNode.update_value)
    prop_wire = BoolProperty(name="Wire", default=True, update=PcgNode.update_value)
    prop_boundary = BoolProperty(name="Boundary", default=True, update=PcgNode.update_value)
    prop_multi_face = BoolProperty(name="Multiple Faces", default=True, update=PcgNode.update_value)
    prop_non_contiguous = BoolProperty(name="Non Contiguous", default=True, update=PcgNode.update_value)
    prop_verts = BoolProperty(name="Vertices", default=True, update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_extend")
        layout.prop(self, "prop_wire")
        layout.prop(self, "prop_boundary")
        layout.prop(self, "prop_multi_face")
        layout.prop(self, "prop_non_contiguous")
        layout.prop(self, "prop_verts")

    def functionality(self):
        bpy.ops.mesh.select_non_manifold(extend=self.prop_extend, use_wire=self.prop_wire, use_boundary=self.prop_boundary, use_multi_face=self.prop_multi_face, use_non_contiguous=self.prop_non_contiguous, use_verts=self.prop_verts)
class SelectNthNode(Node, PcgSelectionNode):
    bl_idname = "SelectNthNode"
    bl_label = "Select Nth"

    prop_nth = IntProperty(name="Nth", default=2, min=2, update=PcgNode.update_value)
    prop_skip = IntProperty(name="Skip", default=1, min=1, update=PcgNode.update_value)
    prop_offset = IntProperty(name="Offset", default=0, update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_nth")
        layout.prop(self, "prop_skip")
        layout.prop(self, "prop_offset")

    def functionality(self):
        bpy.ops.mesh.select_nth(nth=self.prop_nth, skip=self.prop_skip, offset=self.prop_offset)
class SelectRandomNode(Node, PcgSelectionNode):
    bl_idname = "SelectRandomNode"
    bl_label = "Select Random"

    prop_percent = FloatProperty(name="Percent", default=50.0, min=0.0, max=100.0, update=PcgNode.update_value)
    prop_seed = IntProperty(name="Seed", default=0, min=0, update=PcgNode.update_value)
    prop_action = EnumProperty(name="Action", items=[("SELECT", "Select", ""), ("DESELECT", "Deselect", "")], default="SELECT", update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_percent")
        layout.prop(self, "prop_seed")
        layout.prop(self, "prop_action")

    def functionality(self):
        bpy.ops.mesh.select_random(percent=self.prop_percent, seed=self.prop_seed, action=self.prop_action)
class SelectSimilarNode(Node, PcgSelectionNode):
    bl_idname = "SelectSimilarNode"
    bl_label = "Select Similar"

    prop_type = EnumProperty(name="Type", items=[("MATERIAL", "Material", ""), ("IMAGE", "Image", ""), ("AREA", "Area", ""), ("SIDES", "Sides", ""), ("PERIMETER", "Perimeter", ""), ("NORMAL", "Normal", ""), ("COPLANAR", "Co-Planar", ""), ("SMOOTH", "Smooth", ""), ("FREESTYLE_FACE", "Freestyle Face", "")], default="NORMAL", update=PcgNode.update_value)
    prop_compare = EnumProperty(name="Compare", items=[("EQUAL", "Equal", ""), ("GREATER", "Greater", ""), ("LESS", "Less", "")], default="EQUAL", update=PcgNode.update_value)
    prop_threshold = FloatProperty(name="Threshold", default=0.0, min=0.0, max=1.0, update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_type")
        layout.prop(self, "prop_compare")
        layout.prop(self, "prop_threshold")

    def functionality(self):
        bpy.ops.mesh.select_similar(type=self.prop_type, compare=self.prop_compare, threshold=self.prop_threshold)
class SelectSimilarRegionNode(Node, PcgSelectionNode):
    bl_idname = "SelectSimilarRegionNode"
    bl_label = "Select Similar Region"

    def functionality(self):
        bpy.ops.mesh.select_similar_region()
class SelectUngroupedNode(Node, PcgSelectionNode):
    bl_idname = "SelectUngroupedNode"
    bl_label = "Select Ungrouped"

    prop_extend = BoolProperty(name="Extend", update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_extend")
    
    def functionality(self):
        bpy.ops.mesh.select_ungrouped(extend=self.prop_extend)
class SelectEdgesSharpNode(Node, PcgSelectionNode):
    bl_idname = "SelectEdgesSharpNode"
    bl_label = "Select Sharp-Enough Edges"

    prop_sharpness = FloatProperty(name="Sharpness", default=0.523599, min=0.000174533, max=3.14159, precision=6, update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_sharpness")
    
    def functionality(self):
        bpy.ops.mesh.edges_select_sharp(sharpness=self.prop_sharpness)
class SelectFacesLinkedFlatNode(Node, PcgSelectionNode):
    bl_idname = "SelectFacesLinkedFlatSharpNode"
    bl_label = "Select Linked Faces By Angle"

    prop_sharpness = FloatProperty(name="Sharpness", default=0.523599, min=0.000174533, max=3.14159, precision=6, update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_sharpness")
    
    def functionality(self):
        bpy.ops.mesh.faces_select_linked_flat(sharpness=self.prop_sharpness)

class DeleteNode(Node, PcgOperatorNode):
    bl_idname = "DeleteNode"
    bl_label = "Delete"

    prop_type = EnumProperty(name="Type", items=[("VERT", "Vertices", ""), ("EDGE", "Edges", ""), ("FACE", "Faces", ""), ("EDGE_FACE", "Edges And Faces", ""), ("ONLY_FACE", "Only Faces", "")], default="VERT", update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_type")
    
    def functionality(self):
        bpy.ops.mesh.delete(type=self.prop_type)
class DissolveFacesNode(Node, PcgOperatorNode):
    bl_idname = "DissolveFacesNode"
    bl_label = "Dissolve Faces"

    prop_verts = BoolProperty(name="Use Vertices", update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout(self, "prop_verts")
    
    def functionality(self):
        bpy.ops.mesh.dissolve_faces(use_verts=self.prop_verts)

class BeautifyFillNode(Node, PcgOperatorNode):
    bl_idname = "BeautifyFillNode"
    bl_label = "Beautify Fill"

    prop_angle_limit = FloatProperty(name="Angle Limit", default=3.14159, min=0.0, max=3.14159, subtype="ANGLE", unit="ROTATION", update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_angle_limit")
    
    def functionality(self):
        bpy.ops.mesh.beautify_fill(angle_limit=self.prop_angle_limit)
class BevelNode(Node, PcgOperatorNode):
    bl_idname = "BevelNode"
    bl_label = "Bevel"

    prop_offset_type = EnumProperty(name="Offset Type", items=[("OFFSET", "Offset", ""), ("WIDTH", "Width", ""), ("PERCENT", "Percent", ""), ("DEPTH", "Depth", "")], default="OFFSET", update=PcgNode.update_value)
    prop_offset = FloatProperty(name="Offset", default=0.0, min=-1000000, max=1000000, update=PcgNode.update_value)
    prop_segments = IntProperty(name="Segments", default=1, min=1, max=1000, update=PcgNode.update_value)
    prop_profile = FloatProperty(name="Profile", default=0.5, min=0.15, max=1.0, update=PcgNode.update_value)
    prop_vertex_only = BoolProperty(name="Vertex Only", update=PcgNode.update_value)
    prop_clamp_overlap = BoolProperty(name="Clamp Overlap", update=PcgNode.update_value)
    prop_loop_slide = BoolProperty(name="Loop Slide", default=True, update=PcgNode.update_value)
    prop_material = IntProperty(name="Material", default=-1, min=-1, update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_offset_type")
        layout.prop(self, "prop_offset")
        layout.prop(self, "prop_segments")
        layout.prop(self, "prop_profile")
        layout.prop(self, "prop_vertex_only")
        layout.prop(self, "prop_clamp_overlap")
        layout.prop(self, "prop_loop_slide")
        layout.prop(self, "prop_material")
    
    def functionality(self):
        bpy.ops.mesh.bevel(offset_type=self.prop_offset_type, offset=self.prop_offset, segments=self.prop_segments, profile=self.prop_segments, vertex_only=self.prop_vertex_only, clamp_overlap=self.prop_clamp_overlap, loop_slide=self.prop_loop_slide, material=self.prop_material)
class BridgeEdgeLoopsNode(Node, PcgOperatorNode):
    bl_idname = "BridgeEdgeLoopsNode"
    bl_label = "Bridge Edge Loops"

    prop_type = EnumProperty(name="Connect Loops", items=[("SINGLE", "Single", ""), ("CLOSED", "Closed", ""), ("PAIRS", "Pairs", "")], default="SINGLE", update=PcgNode.update_value)
    prop_use_merge = BoolProperty(name="Merge", update=PcgNode.update_value)
    prop_merge_factor = FloatProperty(name="Merge Factor", default=0.5, min=0.0, max=0.1, update=PcgNode.update_value)
    prop_twist_offset = IntProperty(name="Twist", default=0, min=-1000, max=1000, update=PcgNode.update_value)
    prop_number_cuts = IntProperty(name="Number of Cuts", default=0, min=0, max=1000, update=PcgNode.update_value)
    prop_interpolation = EnumProperty(name="Interpolation", items=[("LINEAR", "Linear", ""), ("PATH", "Path", ""), ("SURFACE", "Surface", "")], default="PATH", update=PcgNode.update_value)
    prop_smoothness = FloatProperty(name="Smoothness", default=1.0, min=0.0, max=1000.0, update=PcgNode.update_value)
    prop_profile_shape_factor = FloatProperty(name="Profile Factor", default=0.0, min=-1000.0, max=1000.0, update=PcgNode.update_value)
    prop_profile_shape = EnumProperty(name="Profile Shape", items=[("SMOOTH", "Smooth", ""), ("SPHERE", "Sphere", ""), ("ROOT", "Root", ""), ("INVERSE_SQUARE", "Inverse Square", ""), ("SHARP", "Sharp", ""), ("LINEAR", "Linear", "")], default="SMOOTH", update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_type")
        layout.prop(self, "prop_use_merge")
        layout.prop(self, "prop_merge_factor")
        layout.prop(self, "prop_twist_offset")
        layout.prop(self, "prop_number_cuts")
        layout.prop(self, "prop_interpolation")
        layout.prop(self, "prop_smoothness")
        layout.prop(self, "prop_profile_shape_factor")
        layout.prop(self, "prop_profile_shape")
    
    def functionality(self):
        bpy.ops.mesh.bridge_edge_loops(type=self.prop_type, use_merge=self.prop_use_merge, merge_factor=self.prop_merge_factor, twist_offset=self.prop_twist_offset, number_cuts=self.prop_number_cuts, interpolation=self.prop_interpolation, smoothness=self.prop_smoothness, profile_shape_factor=self.prop_profile_shape_factor, profile_shape=self.prop_profile_shape)
class DecimateNode(Node, PcgOperatorNode):
    bl_idname = "DecimateNode"
    bl_label = "Decimate"

    prop_ratio = FloatProperty(name="Ratio", default=1.0, min=0.0, max=1.0, update=PcgNode.update_value)
    prop_use_vertex_group = BoolProperty(name="Vertex Group", update=PcgNode.update_value)
    prop_vertex_group_factor = FloatProperty(name="Weight", default=1.0, min=0.0, max=1000.0, update=PcgNode.update_value)
    prop_invert_vertex_group = BoolProperty(name="Invert", update=PcgNode.update_value)
    prop_use_symmetry = BoolProperty(name="Symmetry", update=PcgNode.update_value)
    prop_symmetry_axis = EnumProperty(name="Axis", items=[("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", "")], default="Y", update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_ratio")
        layout.prop(self, "prop_use_vertex_group")
        layout.prop(self, "prop_vertex_group_factor")
        layout.prop(self, "prop_invert_vertex_group")
        layout.prop(self, "prop_use_symmetry")
        layout.prop(self, "prop_symmetry_axis")
    
    def functionality(self):
        bpy.ops.mesh.decimate(ratio=self.prop_ratio, use_vertex_group=self.prop_use_vertex_group, vertex_group_factor=self.prop_vertex_group_factor, invert_vertex_group=self.prop_invert_vertex_group, use_symmetry=self.prop_use_symmetry, symmetry_axis=self.prop_symmetry_axis)
class ExtrudeFacesNode(Node, PcgOperatorNode):
    bl_idname = "ExtrudeFacesNode"
    bl_label = "Extrude Faces"

    prop_amount = FloatProperty(name="Amount", update=PcgNode.update_value)
    prop_mirror = BoolProperty(name="Mirror", update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_amount")
        layout.prop(self, "prop_mirror")
    
    def functionality(self):
        window = bpy.data.window_managers['WinMan'].windows[0]
        screen = window.screen
        area = [i for i in screen.areas if i.type == 'VIEW_3D'][0]
        space = area.spaces[0]
        scene = bpy.data.scenes[0]
        region = [i for i in area.regions if i.type == 'WINDOW'][0]
        override = {'window':window, 'screen':screen, 'area': area, 'space':space, 'scene':scene, 'active_object':bpy.data.objects[self.mesh], 'region':region, 'edit_object':bpy.data.objects[self.mesh], 'gpencil_data':bpy.context.gpencil_data}
        bpy.ops.mesh.extrude_faces_move(override ,MESH_OT_extrude_faces_indiv={"mirror":self.prop_mirror}, TRANSFORM_OT_shrink_fatten={"value":self.prop_amount, "use_even_offset":False, "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "release_confirm":True, "use_accurate":False})
class ExtrudeRegionNode(Node, PcgOperatorNode):
    bl_idname = "ExtrudeRegionNode"
    bl_label = "Extrude Region"

    prop_amount = FloatProperty(name="Amount", update=PcgNode.update_value)
    prop_mirror = BoolProperty(name="Mirror", update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_amount")
        layout.prop(self, "prop_mirror")
    
    def functionality(self):
        window = bpy.data.window_managers['WinMan'].windows[0]
        screen = window.screen
        area = [i for i in screen.areas if i.type == 'VIEW_3D'][0]
        space = area.spaces[0]
        scene = bpy.data.scenes[0]
        region = [i for i in area.regions if i.type == 'WINDOW'][0]
        override = {'window':window, 'screen':screen, 'area': area, 'space':space, 'scene':scene, 'active_object':bpy.data.objects[self.mesh], 'region':region, 'edit_object':bpy.data.objects[self.mesh], 'gpencil_data':bpy.context.gpencil_data}
        bpy.ops.mesh.extrude_region_shrink_fatten(override ,MESH_OT_extrude_region={"mirror":self.prop_mirror}, TRANSFORM_OT_shrink_fatten={"value":self.prop_amount, "use_even_offset":False, "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "release_confirm":True, "use_accurate":False})
class InsetNode(Node, PcgOperatorNode):
    bl_idname = "InsetNode"
    bl_label = "Inset"
    
    prop_thickness = FloatProperty(name="Thickness", default=0.01, min=0.0, update=PcgNode.update_value)
    prop_depth = FloatProperty(name="Depth", update=PcgNode.update_value)
    prop_boundary = BoolProperty(name="Boundary", default=True, update=PcgNode.update_value)
    prop_even_offset = BoolProperty(name="Even Offset", default=True, update=PcgNode.update_value)
    prop_relative_offset = BoolProperty(name="Relative Offset", update=PcgNode.update_value)
    prop_edge_rail = BoolProperty(name="Edge Rail", update=PcgNode.update_value)
    prop_outset = BoolProperty(name="Outset", update=PcgNode.update_value)
    prop_select_inset = BoolProperty(name="Select Inset", update=PcgNode.update_value)
    prop_individual = BoolProperty(name="Individual", update=PcgNode.update_value)
    prop_interpolate = BoolProperty(name="Interpolate", default=True, update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_thickness")
        layout.prop(self, "prop_depth")
        split = layout.split()
        col=split.column()
        col.prop(self, "prop_boundary")
        col.prop(self, "prop_even_offset")
        col.prop(self, "prop_relative_offset")
        col.prop(self, "prop_edge_rail")
        col=split.column()
        col.prop(self, "prop_outset")
        col.prop(self, "prop_select_inset")
        col.prop(self, "prop_individual")
        col.prop(self, "prop_interpolate")

    def functionality(self):
        bpy.ops.mesh.inset(use_boundary=self.prop_boundary, use_even_offset=self.prop_even_offset, use_relative_offset=self.prop_relative_offset, use_edge_rail=self.prop_edge_rail, thickness=self.prop_thickness, depth=self.prop_depth, use_outset=self.prop_outset, use_select_inset=self.prop_select_inset, use_individual=self.prop_individual, use_interpolate=self.prop_interpolate)
class MergeNode(Node, PcgOperatorNode):
    bl_idname = "MergeNode"
    bl_label = "Merge"
    
    prop_type = EnumProperty(name="Type", items=[("CENTER", "Center", ""), ("CURSOR", "Cursor", ""), ("COLLAPSE", "Collapse", "")], default="CENTER", update=PcgNode.update_value)
    prop_uv = BoolProperty(name="UVs", update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_type")
        layout.prop(self, "prop_uv")

    def functionality(self):
        bpy.ops.mesh.merge(type=self.prop_type, uvs=self.prop_uv)
class ScrewNode(Node, PcgOperatorNode):
    bl_idname = "ScrewNode"
    bl_label = "Screw"

    prop_steps = IntProperty(name="Steps",default=9, min=1, max=100000, update=PcgNode.update_value)
    prop_turns = IntProperty(name="Turns",default=1, min=1, max=100000, update=PcgNode.update_value)
    prop_center = FloatVectorProperty(name="Center", update=PcgNode.update_value)
    prop_axis = FloatVectorProperty(name="Axis", default=(1.0, 0.0, 0.0), min=-1.0, max=1.0, update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_steps")
        layout.prop(self, "prop_turns")
        layout.prop(self, "prop_center")
        layout.prop(self, "prop_axis")

    def functionality(self):
        bpy.ops.mesh.screw(steps=self.prop_steps, turns=self.prop_turns, center=self.prop_center, axis=self.prop_axis)
class SolidifyNode(Node, PcgOperatorNode):
    bl_idname = "SolidifyNode"
    bl_label = "Solidify"
    
    prop_thickness = FloatProperty(name="Thickness", default=0.01, min=-10000.0, max=10000.0, update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_thickness")

    def functionality(self):
        bpy.ops.mesh.solidify(thickness=self.prop_thickness)
class SpinNode(Node, PcgOperatorNode):
    bl_idname = "SpinNode"
    bl_label = "Spin"
    
    prop_steps = IntProperty(name="Steps", default=9, min=0, max=1000000, update=PcgNode.update_value)
    prop_dupli = BoolProperty(name="Duplicate", update=PcgNode.update_value)
    prop_angle = FloatProperty(name="Angle", default=1.5708, subtype="ANGLE", unit="ROTATION", update=PcgNode.update_value)
    prop_center = FloatVectorProperty(name="Center", update=PcgNode.update_value)
    prop_axis = FloatVectorProperty(name="Axis", min=-1.0, max=1.0, update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_steps")
        layout.prop(self, "prop_dupli")
        layout.prop(self, "prop_angle")
        layout.prop(self, "prop_center")
        layout.prop(self, "prop_axis")

    def functionality(self):
        bpy.ops.mesh.spin(steps=self.prop_steps, dupli=self.prop_dupli, angle=self.prop_angle, center=self.prop_center, axis=self.prop_axis)
class SubdivideNode(Node, PcgOperatorNode):
    bl_idname = "SubdivideNode"
    bl_label = "Subdivide"

    prop_number_cuts = IntProperty(name="Number of Cuts", default=1, min=1, max=100, update=PcgNode.update_value)
    prop_smoothness = FloatProperty(name="Smoothness", default=0.0, min=0.0, max=1000.0, update=PcgNode.update_value)
    prop_quadtri = BoolProperty(name="Quad/Tri Mode", update=PcgNode.update_value)
    prop_quadcorner = EnumProperty(name="Quad Corner Type", items=[("INNERVERT", "Inner Vertices", ""), ("PATH", "Path", ""), ("STRAIGHT_CUT", "Straight Cut", ""), ("FAN", "Fan", "")], default="STRAIGHT_CUT", update=PcgNode.update_value)
    prop_fractal = FloatProperty(name="Fractal", default=0.0, min=0.0, max=1000000, update=PcgNode.update_value)
    prop_fractal_along_normal = FloatProperty(name="Along Normal", default=0.0, min=0.0, max=1.0, update=PcgNode.update_value)
    prop_seed = IntProperty(name="Random Seed", default=0, min=0, update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_number_cuts")
        layout.prop(self, "prop_smoothness")
        layout.prop(self, "prop_quadtri")
        layout.prop(self, "prop_quadcorner")
        layout.prop(self, "prop_fractal")
        layout.prop(self, "prop_fractal_along_normal")
        layout.prop(self, "prop_seed")
    
    def functionality(self):
        bpy.ops.mesh.subdivide(number_cuts=self.prop_number_cuts, smoothness=self.prop_smoothness, quadtri=self.prop_quadtri, quadcorner=self.prop_quadcorner, fractal=self.prop_fractal, fractal_along_normal=self.prop_fractal_along_normal, seed=self.prop_seed)

class ArrayModNode(Node, PcgModifierNode):
    bl_idname = "ArrayModNode"
    bl_label = "Array"

    fit_type = EnumProperty(name="Fit Type", items=[("FIXED_COUNT", "Fixed Count", ""), ("FIT_LENGTH", "Fit Length", ""), ("FIT_CURVE", "Fit Curve", "")], default="FIXED_COUNT", update=PcgNode.update_value)
    count = IntProperty(name="Count", default=2, min=1, max=1000, update=PcgNode.update_value)
    fit_length = FloatProperty(name="Length", default=0.0, min=0.0, update=PcgNode.update_value)
    curve = PointerProperty(name="Curve", type=bpy.types.Object, update=PcgNode.update_value)
    use_constant_offset = BoolProperty(name="Constant Offset", update=PcgNode.update_value)
    constant_offset_displace = FloatVectorProperty(name="Offset", update=PcgNode.update_value)
    use_merge_vertices = BoolProperty(name="Merge Vertices", update=PcgNode.update_value)
    use_merge_vertices_cap = BoolProperty(name="Cap", update=PcgNode.update_value)
    merge_threshold = FloatProperty(name="Threshold", default=0.01, min=0.0, max=1.0, update=PcgNode.update_value)
    use_relative_offset = BoolProperty(name="Use Relative Offset", default=True, update=PcgNode.update_value)
    relative_offset_displace = FloatVectorProperty(name="Relative Offset", default=(1.0, 0.0, 0.0), update=PcgNode.update_value)
    use_object_offset = BoolProperty(name="Object Offset", update=PcgNode.update_value)
    offset_object = PointerProperty(type=bpy.types.Object, update=PcgNode.update_value)
    start_cap = PointerProperty(name="Start Cap", type=bpy.types.Object, update=PcgNode.update_value)
    end_cap = PointerProperty(name="End Cap", type=bpy.types.Object, update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "fit_type")
        if self.fit_type == 'FIXED_COUNT':
            layout.prop(self, "count")
        elif self.fit_type == 'FIT_LENGTH':
            layout.prop(self, "fit_length")
        elif self.fit_type == 'FIT_CURVE':
            layout.prop(self, "curve")
        layout.separator()
        split = layout.split()
        col = split.column()
        col.prop(self, "use_constant_offset")
        sub = col.column()
        sub.active = self.use_constant_offset
        sub.prop(self, "constant_offset_displace", text="")
        col.separator()
        col.prop(self, "use_merge_vertices", text="Merge")
        sub = col.column()
        sub.active = self.use_merge_vertices
        sub.prop(self, "use_merge_vertices_cap", text="First Last")
        sub.prop(self, "merge_threshold", text="Distance")
        col = split.column()
        col.prop(self, "use_relative_offset")
        sub = col.column()
        sub.active = self.use_relative_offset
        sub.prop(self, "relative_offset_displace", text="")
        col.separator()
        col.prop(self, "use_object_offset")
        sub = col.column()
        sub.active = self.use_object_offset
        sub.prop(self, "offset_object", text="")
        layout.separator()
        layout.prop(self, "start_cap")
        layout.prop(self, "end_cap")
    
    def functionality(self):
        bpy.ops.object.modifier_add(type="ARRAY")
        bpy.data.objects[self.mesh].modifiers[0].fit_type = self.fit_type
        bpy.data.objects[self.mesh].modifiers[0].count = self.count
        bpy.data.objects[self.mesh].modifiers[0].fit_length = self.fit_length
        bpy.data.objects[self.mesh].modifiers[0].curve = self.curve
        bpy.data.objects[self.mesh].modifiers[0].use_constant_offset = self.use_constant_offset
        bpy.data.objects[self.mesh].modifiers[0].constant_offset_displace = self.constant_offset_displace
        bpy.data.objects[self.mesh].modifiers[0].use_merge_vertices = self.use_merge_vertices
        bpy.data.objects[self.mesh].modifiers[0].use_merge_vertices_cap = self.use_merge_vertices_cap
        bpy.data.objects[self.mesh].modifiers[0].merge_threshold = self.merge_threshold
        bpy.data.objects[self.mesh].modifiers[0].use_relative_offset = self.use_relative_offset
        bpy.data.objects[self.mesh].modifiers[0].relative_offset_displace = self.relative_offset_displace
        bpy.data.objects[self.mesh].modifiers[0].use_object_offset = self.use_object_offset
        bpy.data.objects[self.mesh].modifiers[0].offset_object = self.offset_object
        bpy.data.objects[self.mesh].modifiers[0].start_cap = self.start_cap
        bpy.data.objects[self.mesh].modifiers[0].end_cap = self.end_cap
        return True
class BevelModNode(Node, PcgModifierNode):
    bl_idname = "BevelModNode"
    bl_label = "Bevel"
    
    width = FloatProperty(name="Width", default=0.1, min=0.0, update=PcgNode.update_value)
    segments = IntProperty(name="Segments", default=1, min=0, max=100, update=PcgNode.update_value)
    profile = FloatProperty(name="Profile", default=0.5, min=0.0, max=1.0, update=PcgNode.update_value)
    material = IntProperty(name="Material", default=-1, min=0, max=32767, update=PcgNode.update_value)
    use_only_vertices = BoolProperty(name="Only Vertices", update=PcgNode.update_value)
    use_clamp_overlap = BoolProperty(name="Clamp Overlap", default=True, update=PcgNode.update_value)
    loop_slide = BoolProperty(name="Loop Slide", default=True, update=PcgNode.update_value)
    limit_method = EnumProperty(name="Limit Method", items=[("NONE", "None", ""), ("ANGLE", "Angle", ""), ("WEIGHT", "Weight", "")], default="NONE", update=PcgNode.update_value)
    angle_limit = IntProperty(name="Angle", default=30, min=0, max=180, subtype="ANGLE", update=PcgNode.update_value)
    offset_type = EnumProperty(name="Limit Method", items=[("OFFSET", "Offset", ""), ("WIDTH", "Width", ""), ("DEPTH", "Depth", ""), ("PERCENT", "Percent", "")], default="OFFSET", update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        split = layout.split()
        col = split.column()
        col.prop(self, "width")
        col.prop(self, "segments")
        col.prop(self, "profile")
        col.prop(self, "material")
        col = split.column()
        col.prop(self, "use_only_vertices")
        col.prop(self, "use_clamp_overlap")
        col.prop(self, "loop_slide")
        layout.label(text="Limit Method:")
        layout.row().prop(self, "limit_method", expand=True)
        if self.limit_method == 'ANGLE':
            layout.prop(self, "angle_limit")
        layout.label(text="Width Method:")
        layout.row().prop(self, "offset_type", expand=True)
    
    def functionality(self):
        bpy.ops.object.modifier_add(type="BEVEL")
        bpy.data.objects[self.mesh].modifiers[0].width = self.width
        bpy.data.objects[self.mesh].modifiers[0].segments = self.segments
        bpy.data.objects[self.mesh].modifiers[0].profile = self.profile
        bpy.data.objects[self.mesh].modifiers[0].material = self.material
        bpy.data.objects[self.mesh].modifiers[0].use_only_vertices = self.use_only_vertices
        bpy.data.objects[self.mesh].modifiers[0].use_clamp_overlap = self.use_clamp_overlap
        bpy.data.objects[self.mesh].modifiers[0].loop_slide = self.loop_slide
        bpy.data.objects[self.mesh].modifiers[0].limit_method = self.limit_method
        bpy.data.objects[self.mesh].modifiers[0].angle_limit = self.angle_limit
        bpy.data.objects[self.mesh].modifiers[0].offset_type = self.offset_type
        return True
class BooleanModNode(Node, PcgModifierNode):
    bl_idname = "BooleanModNode"
    bl_label = "Boolean"
    
    prop_op = EnumProperty(name="Operation", items=[("DIFFERENCE", "Difference", ""), ("UNION", "Union", ""), ("INTERSECT", "Intersect", "")], default="INTERSECT", update=PcgNode.update_value)
    prop_obj = PointerProperty(name="Object", type=bpy.types.Object, update=PcgNode.update_value)
    prop_overlap = FloatProperty(name="Overlap Threshold", default=0.000001, min=0.0, max=1.0, precision=6, update=PcgNode.update_value)
    prop_draw_mode = EnumProperty(items=[("SOLID", "Solid", ""), ("WIRE", "Wire", ""), ("BOUNDS", "Bounds", "")], default="WIRE", update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.prop(self, "prop_op")
        layout.prop(self, "prop_obj")
        layout.prop(self, "prop_overlap")
        layout.label("Set Secondary Object Display Mode:")
        layout.prop(self, "prop_draw_mode", expand=True)
    
    def functionality(self):
        if (self.prop_obj == None):
            return False
        bpy.ops.object.modifier_add(type="BOOLEAN")
        bpy.data.objects[self.mesh].modifiers[0].operation = self.prop_op
        bpy.data.objects[self.mesh].modifiers[0].object = self.prop_obj
        bpy.data.objects[self.mesh].modifiers[0].double_threshold = self.prop_overlap
        self.prop_obj.draw_type = self.prop_draw_mode
        return True
class CastModNode(Node, PcgModifierNode):
    bl_idname = "CastModNode"
    bl_label = "Cast"

    cast_type = EnumProperty(items=[("SPHERE", "Sphere", ""), ("CYLINDER", "Cylinder", ""), ("CUBOID", "Cuboid", "")], update=PcgNode.update_value)
    use_x = BoolProperty(name="X", default=True, update=PcgNode.update_value)
    use_y = BoolProperty(name="Y", default=True, update=PcgNode.update_value)
    use_z = BoolProperty(name="Z", default=True, update=PcgNode.update_value)
    factor = FloatProperty(name="Factor", default=0.5, update=PcgNode.update_value)
    radius = FloatProperty(name="Radius", default=0.0, min=0.0, update=PcgNode.update_value)
    size = FloatProperty(name="Size", default=0.0, min=0.0, update=PcgNode.update_value)
    use_radius_as_size = BoolProperty(name="From Radius", default=True, update=PcgNode.update_value)
    vertex_group = StringProperty(name="Vertex Group", update=PcgNode.update_value)
    object = PointerProperty(type=bpy.types.Object, update=PcgNode.update_value)
    use_transform = BoolProperty(name="Use transform", update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        split = layout.split(percentage=0.25)
        split.label(text="Cast Type:")
        split.prop(self, "cast_type", text="")
        split = layout.split(percentage=0.25)
        col = split.column()
        col.prop(self, "use_x")
        col.prop(self, "use_y")
        col.prop(self, "use_z")
        col = split.column()
        col.prop(self, "factor")
        col.prop(self, "radius")
        col.prop(self, "size")
        col.prop(self, "use_radius_as_size")
        split = layout.split()
        col = split.column()
        col.label(text="Vertex Group:")
        if (not self.mesh == ""):
            col.prop_search(self, "vertex_group", bpy.data.objects[self.mesh], "vertex_groups", text="")
        col = split.column()
        col.label(text="Control Object:")
        col.prop(self, "object", text="")
        if self.object:
            col.prop(self, "use_transform")
    
    def functionality(self):
        bpy.ops.object.modifier_add(type="CAST")
        bpy.data.objects[self.mesh].modifiers[0].cast_type = self.cast_type
        bpy.data.objects[self.mesh].modifiers[0].use_x = self.use_x
        bpy.data.objects[self.mesh].modifiers[0].use_y = self.use_y
        bpy.data.objects[self.mesh].modifiers[0].use_z = self.use_z
        bpy.data.objects[self.mesh].modifiers[0].factor = self.factor
        bpy.data.objects[self.mesh].modifiers[0].radius = self.radius
        bpy.data.objects[self.mesh].modifiers[0].size = self.size
        bpy.data.objects[self.mesh].modifiers[0].use_radius_as_size = self.use_radius_as_size
        bpy.data.objects[self.mesh].modifiers[0].vertex_group = self.vertex_group
        bpy.data.objects[self.mesh].modifiers[0].object = self.object
        bpy.data.objects[self.mesh].modifiers[0].use_transform = self.use_transform
        return True
class CurveModNode(Node, PcgModifierNode):
    bl_idname = "CurveModNode"
    bl_label = "Curve"
    
    vertex_group = StringProperty(name="Vertex Group", update=PcgNode.update_value)
    object = PointerProperty(type=bpy.types.Object, update=PcgNode.update_value)
    deform_axis = EnumProperty(items=[("POS_X", "X", ""), ("POS_Y", "Y", ""), ("POS_Z", "Z", ""), ("NEG_X", "-X", ""), ("NEG_Y", "-Y", ""), ("NEG_Z", "-Z", "")], default="POS_X", update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        split = layout.split()
        col = split.column()
        col.label(text="Object:")
        col.prop(self, "object", text="")
        col = split.column()
        col.label(text="Vertex Group:")
        if (not self.mesh == ""):
            col.prop_search(self, "vertex_group", bpy.data.objects[self.mesh], "vertex_groups", text="")
        layout.label(text="Deformation Axis:")
        layout.row().prop(self, "deform_axis", expand=True)
    
    def functionality(self):
        if (self.object == None):
            return False
        bpy.ops.object.modifier_add(type="CURVE")
        bpy.data.objects[self.mesh].modifiers[0].vertex_group = self.vertex_group
        bpy.data.objects[self.mesh].modifiers[0].object = self.object
        bpy.data.objects[self.mesh].modifiers[0].deform_axis = self.deform_axis
        return True
class DecimateModNode(Node, PcgModifierNode):
    bl_idname = "DecimateModNode"
    bl_label = "Decimate"

    decimate_type = EnumProperty(items=[("COLLAPSE", "Collapse", ""), ("UNSUBDIV", "Un-Subdivide", ""), ("DISSOLVE", "Planar", "")], default="COLLAPSE", update=PcgNode.update_value)
    vertex_group = StringProperty(update=PcgNode.update_value)
    ratio = FloatProperty(name="Ratio", default=1.0, min=0.0, max=1.0, update=PcgNode.update_value)
    invert_vertex_group = BoolProperty(update=PcgNode.update_value)
    vertex_group_factor = FloatProperty(name="Factor", default=1.0, min=0, max=1000, soft_max=10, update=PcgNode.update_value)
    use_collapse_triangulate = BoolProperty(name="Triangulate", update=PcgNode.update_value)
    use_symmetry = BoolProperty(name="Symmetry", update=PcgNode.update_value)
    symmetry_axis = EnumProperty(items=[("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", "")], default="X", update=PcgNode.update_value)
    iterations = IntProperty(name="Iterations", default=0, min=0, max=32767, soft_max=100, update=PcgNode.update_value)
    angle_limit = FloatProperty(name="Angle Limit", default=0.087266, min=0, max=3.14159, subtype="ANGLE", unit="ROTATION", update=PcgNode.update_value)
    use_dissolve_boundaries = BoolProperty(name="All Boundaries", update=PcgNode.update_value)
    delimit = EnumProperty(items=[("NORMAL", "Normal", "", 2), ("MATERIAL", "Material", "", 4), ("SEAM", "Seam", "", 8), ("SHARP", "Sharp", "", 16), ("UV", "UVs", "", 32)], default={"NORMAL"}, options={'ENUM_FLAG'}, update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        decimate_type = self.decimate_type
        row = layout.row()
        row.prop(self, "decimate_type", expand=True)
        if decimate_type == 'COLLAPSE':
            has_vgroup = bool(self.vertex_group)
            layout.prop(self, "ratio")
            split = layout.split()
            col = split.column()
            row = col.row(align=True)
            if (not self.mesh == ""):
                row.prop_search(self, "vertex_group", bpy.data.objects[self.mesh], "vertex_groups", text="")
            row.prop(self, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
            layout_info = col
            col = split.column()
            row = col.row()
            row.active = has_vgroup
            row.prop(self, "vertex_group_factor")
            col.prop(self, "use_collapse_triangulate")
            row = col.split(percentage=0.75)
            row.prop(self, "use_symmetry")
            row.prop(self, "symmetry_axis", text="")
        elif decimate_type == 'UNSUBDIV':
            layout.prop(self, "iterations")
            layout_info = layout
        else:  # decimate_type == 'DISSOLVE':
            layout.prop(self, "angle_limit")
            layout.prop(self, "use_dissolve_boundaries")
            layout.label("Delimit:")
            row = layout.row()
            row.prop(self, "delimit", expand=True)
            layout_info = layout
        if (not self.mesh == ""):
            layout.label(text="Faces: " + str(len(bpy.data.objects[self.mesh].data.polygons)))
    
    def functionality(self):
        bpy.ops.object.modifier_add(type="DECIMATE")
        bpy.data.objects[self.mesh].modifiers[0].decimate_type = self.decimate_type
        bpy.data.objects[self.mesh].modifiers[0].vertex_group = self.vertex_group
        bpy.data.objects[self.mesh].modifiers[0].ratio = self.ratio
        bpy.data.objects[self.mesh].modifiers[0].invert_vertex_group = self.invert_vertex_group
        bpy.data.objects[self.mesh].modifiers[0].vertex_group_factor = self.vertex_group_factor
        bpy.data.objects[self.mesh].modifiers[0].use_collapse_triangulate = self.use_collapse_triangulate
        bpy.data.objects[self.mesh].modifiers[0].use_symmetry = self.use_symmetry
        bpy.data.objects[self.mesh].modifiers[0].symmetry_axis = self.symmetry_axis
        bpy.data.objects[self.mesh].modifiers[0].iterations = self.iterations
        bpy.data.objects[self.mesh].modifiers[0].angle_limit = self.angle_limit
        bpy.data.objects[self.mesh].modifiers[0].use_dissolve_boundaries = self.use_dissolve_boundaries
        bpy.data.objects[self.mesh].modifiers[0].delimit = self.delimit
        return True
class RemeshModNode(Node, PcgModifierNode):
    bl_idname = "RemeshModNode"
    bl_label = "Remesh"
    
    mode = EnumProperty(name="Mode", items=[("BLOCKS", "Blocks", ""), ("SMOOTH", "Smooth", ""), ("SHARP", "Sharp", "")], default="SHARP", update=PcgNode.update_value)
    octree_depth = IntProperty(name="Octree Depth", default=4, min=1, max=12, update=PcgNode.update_value)
    scale = FloatProperty(name="Scale", default=0.9, min=0.0, max=0.99, update=PcgNode.update_value)
    sharpness = FloatProperty(name="Sharpness", default=1.0, update=PcgNode.update_value)
    use_smooth_shade = BoolProperty(name="Smooth Shading", update=PcgNode.update_value)
    use_remove_disconnected = BoolProperty(name="Remove Disconnected Pieces", default=True, update=PcgNode.update_value)
    threshold = FloatProperty(name="Threshold", default=1.0, min=0.0, max=1.0, update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "mode")
        row = layout.row()
        row.prop(self, "octree_depth")
        row.prop(self, "scale")
        if self.mode == 'SHARP':
            layout.prop(self, "sharpness")
        layout.prop(self, "use_smooth_shade")
        layout.prop(self, "use_remove_disconnected")
        row = layout.row()
        row.active = self.use_remove_disconnected
        row.prop(self, "threshold")
    
    def functionality(self):
        bpy.ops.object.modifier_add(type="REMESH")
        bpy.data.objects[self.mesh].modifiers[0].mode = self.mode
        bpy.data.objects[self.mesh].modifiers[0].octree_depth = self.octree_depth
        bpy.data.objects[self.mesh].modifiers[0].scale = self.scale
        bpy.data.objects[self.mesh].modifiers[0].sharpness = self.sharpness
        bpy.data.objects[self.mesh].modifiers[0].use_smooth_shade = self.use_smooth_shade
        bpy.data.objects[self.mesh].modifiers[0].use_remove_disconnected = self.use_remove_disconnected
        bpy.data.objects[self.mesh].modifiers[0].threshold = self.threshold
        return True
class ScrewModNode(Node, PcgModifierNode):
    bl_idname = "ScrewModNode"
    bl_label = "Screw"

    axis = EnumProperty(name="Axis", items=[("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", "")], default="Z", update=PcgNode.update_value)
    object = PointerProperty(type=bpy.types.Object, update=PcgNode.update_value)
    angle = FloatProperty(name="Angle", default=6.283185, subtype="ANGLE", unit="ROTATION", update=PcgNode.update_value)
    steps = IntProperty(name="Steps", default=16, min=2, max=10000, soft_max=512, update=PcgNode.update_value)
    render_steps = IntProperty(name="Render Steps", default=16, min=2, max=10000, soft_max=512, update=PcgNode.update_value)
    use_smooth_shade = BoolProperty(name="Smooth Shading", default=True, update=PcgNode.update_value)
    use_merge_vertices = BoolProperty(name="Merge Vertices", update=PcgNode.update_value)
    merge_threshold = FloatProperty(name="Merge Distance", default=0.01, min=0, update=PcgNode.update_value)
    screw_offset = FloatProperty(name="Screw", update=PcgNode.update_value)
    use_object_screw_offset = BoolProperty(name="Object Screw", update=PcgNode.update_value)
    use_normal_calculate = BoolProperty(name="Calc Order", update=PcgNode.update_value)
    use_normal_flip = BoolProperty(name="Flip", update=PcgNode.update_value)
    iterations = IntProperty(default=1, min=1, max=10000, name="Iterations", update=PcgNode.update_value)
    use_stretch_u = BoolProperty(name="Stretch U", update=PcgNode.update_value)
    use_stretch_v = BoolProperty(name="Stretch V", update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        split = layout.split()
        col = split.column()
        col.prop(self, "axis")
        col.prop(self, "object", text="AxisOb")
        col.prop(self, "angle")
        col.prop(self, "steps")
        col.prop(self, "render_steps")
        col.prop(self, "use_smooth_shade")
        col.prop(self, "use_merge_vertices")
        sub = col.column()
        sub.active = self.use_merge_vertices
        sub.prop(self, "merge_threshold")
        col = split.column()
        row = col.row()
        row.active = (self.object is None or self.use_object_screw_offset is False)
        row.prop(self, "screw_offset")
        row = col.row()
        row.active = (self.object is not None)
        row.prop(self, "use_object_screw_offset")
        col.prop(self, "use_normal_calculate")
        col.prop(self, "use_normal_flip")
        col.prop(self, "iterations")
        col.prop(self, "use_stretch_u")
        col.prop(self, "use_stretch_v")
    
    def functionality(self):
        bpy.ops.object.modifier_add(type="SCREW")
        bpy.data.objects[self.mesh].modifiers[0].axis = self.axis
        bpy.data.objects[self.mesh].modifiers[0].object = self.object
        bpy.data.objects[self.mesh].modifiers[0].angle = self.angle
        bpy.data.objects[self.mesh].modifiers[0].steps = self.steps
        bpy.data.objects[self.mesh].modifiers[0].render_steps = self.render_steps
        bpy.data.objects[self.mesh].modifiers[0].use_smooth_shade = self.use_smooth_shade
        bpy.data.objects[self.mesh].modifiers[0].use_merge_vertices = self.use_merge_vertices
        bpy.data.objects[self.mesh].modifiers[0].merge_threshold = self.merge_threshold
        bpy.data.objects[self.mesh].modifiers[0].screw_offset = self.screw_offset
        bpy.data.objects[self.mesh].modifiers[0].use_object_screw_offset = self.use_object_screw_offset
        bpy.data.objects[self.mesh].modifiers[0].use_normal_calculate = self.use_normal_calculate
        bpy.data.objects[self.mesh].modifiers[0].use_normal_flip = self.use_normal_flip
        bpy.data.objects[self.mesh].modifiers[0].iterations = self.iterations
        bpy.data.objects[self.mesh].modifiers[0].use_stretch_u = self.use_stretch_u
        bpy.data.objects[self.mesh].modifiers[0].use_stretch_v = self.use_stretch_v
        return True
class SimpleDeformModNode(Node, PcgModifierNode):
    bl_idname = "SimpleDeformModNode"
    bl_label = "Simple Deform"

    vertex_group = StringProperty(name="Vertex Group", update=PcgNode.update_value)
    deform_method = EnumProperty(items=[("TWIST", "Twist", ""), ("BEND", "Bend", ""), ("TAPER", "Taper", ""), ("STRETCH", "Stretch", "")], default="TWIST", update=PcgNode.update_value)
    invert_vertex_group = BoolProperty(update=PcgNode.update_value)
    origin = PointerProperty(type=bpy.types.Object, update=PcgNode.update_value)
    lock_x = BoolProperty(name="Lock X Axis", update=PcgNode.update_value)
    lock_y = BoolProperty(name="Lock Y Axis", update=PcgNode.update_value)
    factor = FloatProperty(name="Factor", default=0.785398, update=PcgNode.update_value)
    angle = FloatProperty(name="Angle", default=0.785398, subtype="ANGLE", unit="ROTATION", update=PcgNode.update_value)
    limits = FloatVectorProperty(size=2, default=(0.0, 1.0), min=0.0, max=1.0, update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.row().prop(self, "deform_method", expand=True)
        split = layout.split()
        col = split.column()
        col.label(text="Vertex Group:")
        row = col.row(align=True)
        if (not self.mesh == ""):
            row.prop_search(self, "vertex_group", bpy.data.objects[self.mesh], "vertex_groups", text="")
        row.prop(self, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
        split = layout.split()
        col = split.column()
        col.label(text="Axis, Origin:")
        col.prop(self, "origin", text="")
        if self.deform_method in {'TAPER', 'STRETCH', 'TWIST'}:
            col.label(text="Lock:")
            col.prop(self, "lock_x")
            col.prop(self, "lock_y")
        col = split.column()
        col.label(text="Deform:")
        if self.deform_method in {'TAPER', 'STRETCH'}:
            col.prop(self, "factor")
        else:
            col.prop(self, "angle")
        col.prop(self, "limits", slider=True)
    
    def functionality(self):
        bpy.ops.object.modifier_add(type="SIMPLE_DEFORM")
        bpy.data.objects[self.mesh].modifiers[0].deform_method = self.deform_method
        bpy.data.objects[self.mesh].modifiers[0].vertex_group = self.vertex_group
        bpy.data.objects[self.mesh].modifiers[0].invert_vertex_group = self.invert_vertex_group
        bpy.data.objects[self.mesh].modifiers[0].origin = self.origin
        bpy.data.objects[self.mesh].modifiers[0].lock_x = self.lock_x
        bpy.data.objects[self.mesh].modifiers[0].lock_y = self.lock_y
        if self.deform_method in {'TAPER', 'STRETCH'}:
            bpy.data.objects[self.mesh].modifiers[0].factor = self.factor
        else:
            bpy.data.objects[self.mesh].modifiers[0].angle = self.angle
        bpy.data.objects[self.mesh].modifiers[0].limits = self.limits
        return True
class SkinModNode(Node, PcgModifierNode):
    bl_idname = "SkinModNode"
    bl_label = "Skin"

    branch_smoothing = FloatProperty(name="Branch Smoothing", default=0.0, min=0.0, max=1.0, update=PcgNode.update_value)
    use_smooth_shade = BoolProperty(name="Smooth Shading", update=PcgNode.update_value)
    use_x_symmetry = BoolProperty(name="X", default=True, update=PcgNode.update_value)
    use_y_symmetry = BoolProperty(name="Y", update=PcgNode.update_value)
    use_z_symmetry = BoolProperty(name="Z", update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        row = layout.row()
        row.operator("object.skin_armature_create", text="Create Armature")
        row.operator("mesh.customdata_skin_add")
        layout.separator()
        row = layout.row(align=True)
        row.prop(self, "branch_smoothing")
        row.prop(self, "use_smooth_shade")
        split = layout.split()
        col = split.column()
        col.label(text="Selected Vertices:")
        sub = col.column(align=True)
        # None of the operators below will work as the mesh will be in object mode
        # Even if it is in the edit mode, the modifier will have already been applied
        sub.operator("object.skin_loose_mark_clear", text="Mark Loose").action = 'MARK'
        sub.operator("object.skin_loose_mark_clear", text="Clear Loose").action = 'CLEAR'
        sub = col.column()
        sub.operator("object.skin_root_mark", text="Mark Root")
        sub.operator("object.skin_radii_equalize", text="Equalize Radii")
        col = split.column()
        col.label(text="Symmetry Axes:")
        col.prop(self, "use_x_symmetry")
        col.prop(self, "use_y_symmetry")
        col.prop(self, "use_z_symmetry")
    
    def functionality(self):
        bpy.ops.object.modifier_add(type="SKIN")
        bpy.data.objects[self.mesh].modifiers[0].branch_smoothing = self.branch_smoothing
        bpy.data.objects[self.mesh].modifiers[0].use_smooth_shade = self.use_smooth_shade
        bpy.data.objects[self.mesh].modifiers[0].use_x_symmetry = self.use_x_symmetry
        bpy.data.objects[self.mesh].modifiers[0].use_y_symmetry = self.use_y_symmetry
        bpy.data.objects[self.mesh].modifiers[0].use_z_symmetry = self.use_z_symmetry
        return True
class SmoothModNode(Node, PcgModifierNode):
    bl_idname = "SmoothModNode"
    bl_label = "Smooth"

    use_x = BoolProperty(name="X", default=True, update=PcgNode.update_value)
    use_y = BoolProperty(name="Y", default=True, update=PcgNode.update_value)
    use_z = BoolProperty(name="Z", default=True, update=PcgNode.update_value)
    factor = FloatProperty(name="Factor", default=0.5, update=PcgNode.update_value)
    iterations = IntProperty(name="Repeat", default=1, min=0, max=32767, soft_max=30, update=PcgNode.update_value)
    vertex_group = StringProperty(name="Vertex Group", update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        split = layout.split(percentage=0.25)
        col = split.column()
        col.label(text="Axis:")
        col.prop(self, "use_x")
        col.prop(self, "use_y")
        col.prop(self, "use_z")
        col = split.column()
        col.prop(self, "factor")
        col.prop(self, "iterations")
        col.label(text="Vertex Group:")
        if (not self.mesh == ""):
            col.prop_search(self, "vertex_group", bpy.data.objects[self.mesh], "vertex_groups", text="")
    
    def functionality(self):
        bpy.ops.object.modifier_add(type="SMOOTH")
        bpy.data.objects[self.mesh].modifiers[0].use_x = self.use_x
        bpy.data.objects[self.mesh].modifiers[0].use_y = self.use_y
        bpy.data.objects[self.mesh].modifiers[0].use_z = self.use_z
        bpy.data.objects[self.mesh].modifiers[0].factor = self.factor
        bpy.data.objects[self.mesh].modifiers[0].iterations = self.iterations
        bpy.data.objects[self.mesh].modifiers[0].vertex_group = self.vertex_group
        return True
class SolidifyModNode(Node, PcgModifierNode):
    bl_idname = "SolidifyModNode"
    bl_label = "Solidify"
    
    thickness = FloatProperty(name="Thickness", default=0.01, update=PcgNode.update_value)
    thickness_clamp = FloatProperty(name="Clamp", default=0.0, min=0.0, max=100.0, update=PcgNode.update_value)
    vertex_group = StringProperty(name="Vertex Group", update=PcgNode.update_value)
    invert_vertex_group = BoolProperty(name="Invert", update=PcgNode.update_value)
    thickness_vertex_group = FloatProperty(default=0.0, min=0.0, max=1.0, update=PcgNode.update_value)
    edge_crease_inner = FloatProperty(default=0.0, min=0.0, max=1.0, update=PcgNode.update_value)
    edge_crease_outer = FloatProperty(default=0.0, min=0.0, max=1.0, update=PcgNode.update_value)
    edge_crease_rim = FloatProperty(default=0.0, min=0.0, max=1.0, update=PcgNode.update_value)
    offset = FloatProperty(name="Offset", default=-1.0, update=PcgNode.update_value)
    use_flip_normals = BoolProperty(name="Flip Normals", update=PcgNode.update_value)
    use_even_offset = BoolProperty(name="Even Thickness", update=PcgNode.update_value)
    use_quality_normals = BoolProperty(name="High Quality Normals", update=PcgNode.update_value)
    use_rim = BoolProperty(name="Fill Rim", default=True, update=PcgNode.update_value)
    use_rim_only = BoolProperty(name="Only Rim", update=PcgNode.update_value)
    material_offset = IntProperty(default=0, min=-32768, max=32767, update=PcgNode.update_value)
    material_offset_rim = IntProperty(default=0, min=-32768, max=32767, update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        split = layout.split()
        col = split.column()
        col.prop(self, "thickness")
        col.prop(self, "thickness_clamp")
        col.separator()
        row = col.row(align=True)
        if (not self.mesh == ""):
            row.prop_search(self, "vertex_group", bpy.data.objects[self.mesh], "vertex_groups", text="")
        sub = row.row(align=True)
        sub.active = bool(self.vertex_group)
        sub.prop(self, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
        sub = col.row()
        sub.active = bool(self.vertex_group)
        sub.prop(self, "thickness_vertex_group", text="Factor")
        col.label(text="Crease:")
        col.prop(self, "edge_crease_inner", text="Inner")
        col.prop(self, "edge_crease_outer", text="Outer")
        col.prop(self, "edge_crease_rim", text="Rim")
        col = split.column()
        col.prop(self, "offset")
        col.prop(self, "use_flip_normals")
        col.prop(self, "use_even_offset")
        col.prop(self, "use_quality_normals")
        col.prop(self, "use_rim")
        col_rim = col.column()
        col_rim.active = self.use_rim
        col_rim.prop(self, "use_rim_only")
        col.separator()
        col.label(text="Material Index Offset:")
        sub = col.column()
        row = sub.split(align=True, percentage=0.4)
        row.prop(self, "material_offset", text="")
        row = row.row(align=True)
        row.active = self.use_rim
        row.prop(self, "material_offset_rim", text="Rim")
    
    def functionality(self):
        bpy.ops.object.modifier_add(type="SOLIDIFY")
        bpy.data.objects[self.mesh].modifiers[0].thickness = self.thickness
        bpy.data.objects[self.mesh].modifiers[0].thickness_clamp = self.thickness_clamp
        bpy.data.objects[self.mesh].modifiers[0].vertex_group = self.vertex_group
        bpy.data.objects[self.mesh].modifiers[0].invert_vertex_group = self.invert_vertex_group
        bpy.data.objects[self.mesh].modifiers[0].thickness_vertex_group = self.thickness_vertex_group
        bpy.data.objects[self.mesh].modifiers[0].edge_crease_inner = self.edge_crease_inner
        bpy.data.objects[self.mesh].modifiers[0].edge_crease_outer = self.edge_crease_outer
        bpy.data.objects[self.mesh].modifiers[0].edge_crease_rim = self.edge_crease_rim
        bpy.data.objects[self.mesh].modifiers[0].offset = self.offset
        bpy.data.objects[self.mesh].modifiers[0].use_flip_normals = self.use_flip_normals
        bpy.data.objects[self.mesh].modifiers[0].use_even_offset = self.use_even_offset
        bpy.data.objects[self.mesh].modifiers[0].use_quality_normals = self.use_quality_normals
        bpy.data.objects[self.mesh].modifiers[0].use_rim = self.use_rim
        bpy.data.objects[self.mesh].modifiers[0].use_rim_only = self.use_rim_only
        bpy.data.objects[self.mesh].modifiers[0].material_offset = self.material_offset
        bpy.data.objects[self.mesh].modifiers[0].material_offset_rim = self.material_offset_rim
        return True
class SubdivideModNode(Node, PcgModifierNode):
    bl_idname = "SubdivideModNode"
    bl_label = "Subdivision Surface"
    
    subdivision_type = EnumProperty(items=[("CATMULL_CLARK", "Catmull-Clark", ""), ("SIMPLE", "Simple", "")], default="CATMULL_CLARK", update=PcgNode.update_value)
    levels = IntProperty(default=1, min=0, max=11, soft_max=6, update=PcgNode.update_value)
    render_levels = IntProperty(default=2, min=0, max=11, soft_max=6, update=PcgNode.update_value)
    use_subsurf_uv = BoolProperty(name="Subdivide UVs", default=True, update=PcgNode.update_value)
    show_only_control_edges = BoolProperty(name="Optimal Display", update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.row().prop(self, "subdivision_type", expand=True)
        split = layout.split()
        col = split.column()
        col.label(text="Subdivisions:")
        col.prop(self, "levels", text="View")
        col.prop(self, "render_levels", text="Render")
        col = split.column()
        col.label(text="Options:")
        sub = col.column()
        sub.prop(self, "use_subsurf_uv")
        col.prop(self, "show_only_control_edges")
    
    def functionality(self):
        if (self.levels == 0):
            return False
        bpy.ops.object.modifier_add(type="SUBSURF")
        bpy.data.objects[self.mesh].modifiers[0].subdivision_type = self.subdivision_type
        bpy.data.objects[self.mesh].modifiers[0].levels = self.levels
        bpy.data.objects[self.mesh].modifiers[0].render_levels = self.render_levels
        bpy.data.objects[self.mesh].modifiers[0].use_subsurf_uv = self.use_subsurf_uv
        bpy.data.objects[self.mesh].modifiers[0].show_only_control_edges = self.show_only_control_edges
        return True
class WireframeModNode(Node, PcgModifierNode):
    bl_idname = "WireframeModNode"
    bl_label = "Wireframe"

    thickness = FloatProperty(update=PcgNode.update_value)
    vertex_group = StringProperty(update=PcgNode.update_value)
    invert_vertex_group = BoolProperty(update=PcgNode.update_value)
    thickness_vertex_group = FloatProperty(default=0.0, min=0.0, max=1.0, update=PcgNode.update_value)
    use_crease = BoolProperty(update=PcgNode.update_value)
    crease_weight = FloatProperty(update=PcgNode.update_value)
    offset = FloatProperty(name="Offset", update=PcgNode.update_value)
    use_even_offset = BoolProperty(update=PcgNode.update_value)
    use_relative_offset = BoolProperty(update=PcgNode.update_value)
    use_boundary = BoolProperty(update=PcgNode.update_value)
    use_replace = BoolProperty(update=PcgNode.update_value)
    material_offset = IntProperty(default=0, min=-32768, max=32767, update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        has_vgroup = bool(self.vertex_group)
        split = layout.split()
        col = split.column()
        col.prop(self, "thickness", text="Thickness")
        row = col.row(align=True)
        if (not self.mesh == ""):
            row.prop_search(self, "vertex_group", bpy.data.objects[self.mesh], "vertex_groups", text="")
        sub = row.row(align=True)
        sub.active = has_vgroup
        sub.prop(self, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
        row = col.row(align=True)
        row.active = has_vgroup
        row.prop(self, "thickness_vertex_group", text="Factor")
        col.prop(self, "use_crease", text="Crease Edges")
        row = col.row()
        row.active = self.use_crease
        row.prop(self, "crease_weight", text="Crease Weight")
        col = split.column()
        col.prop(self, "offset")
        col.prop(self, "use_even_offset", text="Even Thickness")
        col.prop(self, "use_relative_offset", text="Relative Thickness")
        col.prop(self, "use_boundary", text="Boundary")
        col.prop(self, "use_replace", text="Replace Original")
        col.prop(self, "material_offset", text="Material Offset")
    
    def functionality(self):
        bpy.ops.object.modifier_add(type="WIREFRAME")
        bpy.data.objects[self.mesh].modifiers[0].thickness = self.thickness
        bpy.data.objects[self.mesh].modifiers[0].vertex_group = self.vertex_group
        bpy.data.objects[self.mesh].modifiers[0].invert_vertex_group = self.invert_vertex_group
        bpy.data.objects[self.mesh].modifiers[0].thickness_vertex_group = self.thickness_vertex_group
        bpy.data.objects[self.mesh].modifiers[0].use_crease = self.use_crease
        bpy.data.objects[self.mesh].modifiers[0].crease_weight = self.crease_weight
        bpy.data.objects[self.mesh].modifiers[0].offset = self.offset
        bpy.data.objects[self.mesh].modifiers[0].use_even_offset = self.use_even_offset
        bpy.data.objects[self.mesh].modifiers[0].use_relative_offset = self.use_relative_offset
        bpy.data.objects[self.mesh].modifiers[0].use_boundary = self.use_boundary
        bpy.data.objects[self.mesh].modifiers[0].use_replace = self.use_replace
        bpy.data.objects[self.mesh].modifiers[0].material_offset = self.material_offset
        return True

class PivotNode(Node, PcgSettingNode):
    bl_idname = "PivotNode"
    bl_label = "Pivot Center"

    prop_pivot = EnumProperty(name="Pivot Point", items=[("BOUNDING_BOX_CENTER", "Bound Box Center", ""), ("CURSOR", "Cursor", ""), ("INDIVIDUAL_ORIGINS", "Individual Origins", ""), ("MEDIAN_POINT", "Median Point", ""), ("ACTIVE_ELEMENT", "Active Element", "")], default="MEDIAN_POINT", update=PcgNode.update_value)

    def draw_buttons(self, context, layout):
        layout.column().prop(self, "prop_pivot", expand=True)
    
    def functionality(self):
        window = bpy.data.window_managers['WinMan'].windows[0]
        screen = window.screen
        area = [i for i in screen.areas if i.type == 'VIEW_3D'][0]
        space = area.spaces[0]
        space.pivot_point = self.prop_pivot
class OrientationNode(Node, PcgSettingNode):
    bl_idname = "OrientationNode"
    bl_label = "Transform Orientation"

    prop_orientation = EnumProperty(name="Pivot Point", items=[("GLOBAL", "Global", ""), ("LOCAL", "Local", ""), ("NORMAL", "Normal", ""), ("GIMBAL", "Gimbal", ""), ("VIEW", "View", "")], default="GLOBAL", update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        layout.column().prop(self, "prop_orientation", expand=True)
    
    def functionality(self):
        window = bpy.data.window_managers['WinMan'].windows[0]
        screen = window.screen
        area = [i for i in screen.areas if i.type == 'VIEW_3D'][0]
        space = area.spaces[0]
        space.transform_orientation = self.prop_orientation

class MeshNode(Node, PcgSettingNode):
    bl_idname = "MeshNode"
    bl_label = "Mesh Output"
    
    print_output = BoolProperty(name="Print Output (Debug)", default=False, update=PcgNode.update_value)
    
    def init(self, context):
        self.inputs.new("UniversalSocket", "Mesh")
    
    def draw_buttons(self, context, layout):
        if (self == self.id_data.nodes.active):
            layout.operator("pcg.refresh_mesh_op", "Refresh Mesh")
        layout.column().prop(self, "print_output")
    
    def functionality(self):
        if (self.print_output):
            print(self.name + ": " + self.mesh)
class DrawModeNode(Node, PcgSettingNode):
    bl_idname = "DrawModeNode"
    bl_label = "Mesh Draw Mode (Viewport)"

    prop_name = BoolProperty(name="Name", update=PcgNode.update_value)
    prop_wire = BoolProperty(name="Wire", update=PcgNode.update_value)
    prop_xray = BoolProperty(name="X-Ray", update=PcgNode.update_value)
    prop_transparency = BoolProperty(name="Transparency", update=PcgNode.update_value)
    prop_max_draw_type = EnumProperty(name="Maximum Draw Type", items=[("SOLID", "Solid", ""), ("WIRE", "Wire", ""), ("BOUNDS", "Bounds", "")], default="SOLID", update=PcgNode.update_value)
    
    def draw_buttons(self, context, layout):
        split = layout.split()
        col = split.column()
        col.prop(self, "prop_name")
        col.prop(self, "prop_wire")
        col = split.column()
        col.prop(self, "prop_xray")
        col.prop(self, "prop_transparency")
        layout.label("Maximum Draw Type:")
        layout.prop(self, "prop_max_draw_type", expand=True)
    
    def functionality(self):
        bpy.data.objects[self.mesh].show_name = self.prop_name
        bpy.data.objects[self.mesh].show_wire = self.prop_wire
        bpy.data.objects[self.mesh].show_x_ray = self.prop_xray
        bpy.data.objects[self.mesh].show_transparent = self.prop_transparency
        bpy.data.objects[self.mesh].draw_type = self.prop_max_draw_type
##############################################################                                                            ##############################################


inputs = [PlaneNode, CubeNode, SphereNode, CylinderNode, ConeNode] #TorusNode
transform = [LocationNode, RotationNode, ScaleNode, TranslateNode, RotateNode, ResizeNode]
modifiers = [ArrayModNode, BevelModNode, BooleanModNode, CastModNode, CurveModNode, DecimateModNode, RemeshModNode, ScrewModNode, SimpleDeformModNode, SkinModNode, SmoothModNode, SolidifyModNode, SubdivideModNode, WireframeModNode]
conversion = [ToComponentNode, ToMeshNode, ChangeModeNode]
selection = [SelectComponentsManuallyNode, SelectAllNode, SelectAxisNode, SelectFaceBySidesNode, SelectInteriorFaces, SelectLessNode, SelectMoreNode, SelectLinkedNode, SelectLooseNode, SelectMirrorNode, SelectNextItemNode, SelectPrevItemNode, SelectNonManifoldNode, SelectNthNode, SelectRandomNode, SelectSimilarNode, SelectSimilarRegionNode, SelectUngroupedNode, SelectEdgesSharpNode, SelectFacesLinkedFlatNode]
deletion = [DeleteNode, DissolveFacesNode]
operators = [BeautifyFillNode, BevelNode, BridgeEdgeLoopsNode, DecimateNode, ExtrudeFacesNode, ExtrudeRegionNode, InsetNode, MergeNode, ScrewNode, SolidifyNode, SpinNode, SubdivideNode] #Overrides
settings = [PivotNode, OrientationNode]
outputs = [MeshNode, DrawModeNode]

node_categories = [PcgNodeCategory("inputs", "Inputs", items=[NodeItem(i.bl_idname) for i in inputs]),
                   PcgNodeCategory("transform", "Transform", items=[NodeItem(i.bl_idname) for i in transform]),
                   PcgNodeCategory("modifiers", "Modifiers", items=[NodeItem(i.bl_idname) for i in modifiers]),
                   PcgNodeCategory("conversion", "Conversion", items=[NodeItem(i.bl_idname) for i in conversion]),
                   PcgNodeCategory("selection", "Selection", items=[NodeItem(i.bl_idname) for i in selection]),
                   PcgNodeCategory("deletion", "Deletion", items=[NodeItem(i.bl_idname) for i in deletion]),
                   PcgNodeCategory("operators", "Operators", items=[NodeItem(i.bl_idname) for i in operators]),
                   PcgNodeCategory("settings", "Settings", items=[NodeItem(i.bl_idname) for i in settings]),
                   PcgNodeCategory("outputs", "Outputs", items=[NodeItem(i.bl_idname) for i in outputs])]

def register():
    nodeitems_utils.register_node_categories("PcgNodeCategories", node_categories)
    bpy.utils.register_module(__name__)
def unregister():
    nodeitems_utils.unregister_node_categories("PcgNodeCategories")
    bpy.utils.unregister_module(__name__)