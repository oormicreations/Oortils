# Oortils utilities by Oormi Creations
#http://oormi.in


bl_info = {
    "name": "Oortils",
    "description": "Blender utilities",
    "author": "Oormi Creations",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "3D Viewport > N Menu > Oortils",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "https://github.com/oormicreations/Oortils",
    "tracker_url": "https://github.com/oormicreations/Oortils",
    "category": "Development"
}

import bpy
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       IntVectorProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )

import os
import random

def ShowMessageBox(message = "", title = "Oortils Says...", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


def RunInTerminal(openfile):
    blendexe = bpy.app.binary_path
    blendfilepath = bpy.context.blend_data.filepath
    shstr = "gnome-terminal -- " + blendexe
    
    if openfile:
        if len(blendfilepath)>0:
            shstr = "gnome-terminal -- " + blendexe + " '" + blendfilepath + "'"
    
    #print(shstr)
    #TODO : check for save required
    
    os.system(shstr)
    bpy.ops.wm.quit_blender()

def TrueColors(rtool):
    bpy.context.space_data.shading.type = 'SOLID'
    bpy.context.space_data.shading.color_type  = 'OBJECT'
    bpy.context.space_data.shading.wireframe_color_type  = 'OBJECT'
    res = 10000
    for obj in bpy.data.objects:
        r = float(random.randrange(0, res))/res
        g = float(random.randrange(0, res))/res
        b = float(random.randrange(0, res))/res
        a = 1#float(random.randrange(0, res))/res
        if rtool.r_setalpha:
            a = float(random.randrange(500, res))/res
        obj.color = (r,g,b,a)

def ReloadTex(rtool):
    bpy.context.space_data.shading.type = 'SOLID'
    bpy.context.space_data.shading.color_type = 'TEXTURE'

    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            if len(obj.data.materials)>0:
                mat = obj.data.materials[0]
                #print(mat)
                matnodes = mat.node_tree.nodes
                #print(matnodes)
                for node in matnodes:
                    if node.type == 'TEX_IMAGE':
                        #print(node.image.filepath)
                        node.image.filepath = node.image.filepath
        
def Turntable(rtool):
    objs = bpy.context.selected_objects
    if len(objs)>0:
        cam = objs[0]
        if cam.type == 'CAMERA':
            print(cam)
            loc = cam.location
            #bpy.ops.object.add(type='EMPTY', location=loc)
            #cam.parent = bpy.context.object
            bpy.ops.object.constraint_add(type='LOCKED_TRACK')
            bpy.context.object.constraints["Locked Track"].target = bpy.data.objects["Cube"]
            bpy.context.object.constraints["Locked Track"].track_axis = 'TRACK_NEGATIVE_Z'
            bpy.context.object.constraints["Locked Track"].lock_axis = 'LOCK_Y'
            

        else:
            ShowMessageBox("Please select a camera")
    else:
        ShowMessageBox("Please select a camera")

### Operators ###

class COT_OT_COpenTerm(bpy.types.Operator):
    bl_idname = "open.term"
    bl_label = "Open Term"
    bl_description = "Open Terminal."

    def execute(self, context):
        scene = context.scene
        rtool = scene.r_tool
        RunInTerminal(rtool.r_openfile)
        
        return{'FINISHED'} 
    
class CTC_OT_CTrueColors(bpy.types.Operator):
    bl_idname = "true.colors"
    bl_label = "True Colors"
    bl_description = "Assign random colors."

    def execute(self, context):
        scene = context.scene
        rtool = scene.r_tool
        TrueColors(rtool)
        
        return{'FINISHED'} 

class CRT_OT_CReloadTexture(bpy.types.Operator):
    bl_idname = "reload.tex"
    bl_label = "Reload Texture"
    bl_description = "Reload the changed texture image."

    def execute(self, context):
        scene = context.scene
        rtool = scene.r_tool
        ReloadTex(rtool)
        
        return{'FINISHED'} 

class CTA_OT_CTurntable(bpy.types.Operator):
    bl_idname = "turn.table"
    bl_label = "Turn Table"
    bl_description = "Create Turntable Animation."

    def execute(self, context):
        scene = context.scene
        rtool = scene.r_tool
        Turntable(rtool)
        
        return{'FINISHED'} 

### Panels ###

class OBJECT_PT_OoPanel(bpy.types.Panel):

    bl_label = "Oortils"
    bl_idname = "OBJECT_PT_OO_Panel"
    bl_category = "Oortils"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
#    bl_context = "objectmode"


    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rtool = scene.r_tool
        
        layout.prop(rtool, "r_openfile")
        layout.operator("open.term", text = "Open in terminal", icon='BLENDER')
        layout.prop(rtool, "r_setalpha")
        layout.operator("true.colors", text = "True Colors", icon='COLORSET_02_VEC')
        layout.operator("reload.tex", text = "Reload Textures", icon='FILE_IMAGE')
        layout.operator("turn.table", text = "Turntable", icon='FILE_IMAGE')
        #layout.label(text = "Part Frame Count : " + str(vsrtool.vsr_partframes))


class CCProperties(PropertyGroup):
    
    r_outfilename: StringProperty(
        name = "Out File Name",
        description = "Name of the joined movie",
        default = "joinedoutput"
      )
      
    r_openfile: BoolProperty(
        name = "Open File",
        description = "Loads Blender in terminal with the currently open file",
        default = True
    )

    r_setalpha: BoolProperty(
        name = "Affect Transparancy",
        description = "Changes transparancy of objects.",
        default = False
    )



# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    OBJECT_PT_OoPanel,
    CCProperties,
    CTC_OT_CTrueColors,
    COT_OT_COpenTerm,
    CRT_OT_CReloadTexture,
    CTA_OT_CTurntable
)

def register():
    bl_info['blender'] = getattr(bpy.app, "version")
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.r_tool = PointerProperty(type=CCProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.r_tool



if __name__ == "__main__":
    register()