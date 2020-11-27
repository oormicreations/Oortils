# Oortils utilities by Oormi Creations
#http://oormi.in


bl_info = {
    "name": "Oortils",
    "description": "Blender utilities",
    "author": "Oormi Creations",
    "version": (0, 2, 0),
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
from mathutils import *
from bpy import context
import codecs
import platform
from datetime import datetime


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
            #print(cam)
            cam.location = [0,0,0]
            cam.rotation_euler = [0,0,0]
            
            bpy.ops.object.constraint_add(type='FOLLOW_PATH')
            fp = bpy.context.object.constraints["Follow Path"]
            fp.use_curve_follow = True
            fp.forward_axis = 'TRACK_NEGATIVE_X'
            fp.up_axis = 'UP_Y'
            
            bpy.ops.curve.primitive_bezier_circle_add(radius = rtool.r_ttradius, enter_editmode=False, location=(0, 0, 0))
            fp.target = bpy.context.selected_objects[0]
            
            bpy.ops.object.select_all(action = "DESELECT")
            cam.select_set(True)
            bpy.context.view_layer.objects.active = cam
            override={'constraint':cam.constraints["Follow Path"]}
            bpy.ops.constraint.followpath_path_animate(override, constraint="Follow Path", owner='OBJECT')

        else:
            ShowMessageBox("Please select a camera")
    else:
        ShowMessageBox("Please select a camera")

    rtool.r_status = "Turntable created!"

def Nodetoscript(rtool):
    if len(bpy.path.abspath("//"))<1:
        ShowMessageBox("Please save your file first, script will be saved in the same folder as your file")
        return 0
        
    
    objs = bpy.context.selected_objects
    if len(objs)>1:
        ShowMessageBox("Please select only one object")
        return 0
    
    if len(bpy.context.object.data.materials) > 1:
        ShowMessageBox("First material will be used")
        
    mat = bpy.context.object.data.materials[0]
    if mat == None:
        ShowMessageBox("Object has no material")
        return 0
        
    matnodes = mat.node_tree.nodes
    if len(matnodes) < 1:
        ShowMessageBox("There are no nodes in the material")
        return 0
        
    matlinks = mat.node_tree.links


    s = "### Node-to-Script Start - Generated using Oortils\n### " + mat.name + "\nimport bpy\nfrom mathutils import *\nfrom bpy import context\n\n"
    s = s + "mat = bpy.data.materials.new(name=\"NodeToScriptMat\")\nmat.use_nodes = True\nmatnodes = mat.node_tree.nodes\nmatlinks = mat.node_tree.links\n\n"
    s = s + "for n in matnodes:\n\tmatnodes.remove(n)\n\n"

    count = 1
    nodevars = []

    for m in matnodes:
        nodename = m.name
        nodename = nodename.replace(" ", "")
        nodename = nodename.replace(".", "")
        nodevars.append(nodename)
        s = s + nodename + " = matnodes.new('" + m.bl_idname + "')\n"
        count += 1

    s = s + "\n\n"
    count = 0
    for n in nodevars:
        locstr = str(matnodes[count].location)
        locstr = locstr.replace("<", "")
        locstr = locstr.replace(">", "")
        locstr = locstr.replace("(", "((")
        locstr = locstr.replace(")", "))")
        s = s + n + ".location = " + locstr + "\n"
        count += 1
        
    s = s + "\n\n"
    for ml in matlinks:
        node1 = ml.from_node.name
        node1 = node1.replace(" ", "")
        node1 = node1.replace(".", "")
        node1out = ml.from_socket.name

        node2 = ml.to_node.name
        node2 = node2.replace(" ", "")
        node2 = node2.replace(".", "")
        node2in = ml.to_socket.name

        s = s + "matlinks.new(" + node1 + ".outputs['" + node1out + "'], " + node2 + ".inputs['" + node2in + "'])\n"


    count = 0
    sp = ""

    for m in matnodes:
        if len(m.inputs)>0 and m.bl_idname != "ShaderNodeOutputMaterial":
            #print(m)
            for i in m.inputs:
                try:
                    #print(count, m.name, i.name, i.default_value)
                    valstr = str(i.default_value)
                    if valstr.find("NodeSocketVector") >= 0:
                        valstr = "[" + str(i.default_value[0]) + "," + str(i.default_value[1]) + "," + str(i.default_value[2]) + "]"
                    if valstr.find("NodeSocketColor") >= 0:
                        valstr = "[" + str(i.default_value[0]) + "," + str(i.default_value[1]) + "," + str(i.default_value[2]) + "," + str(i.default_value[3])+ "]"
                    if valstr.find("<Vector") >= 0:
                        valstr = valstr.replace("<Vector ", "Vector(")
                        valstr = valstr.replace(")>", "))")
                    if valstr.find("<Euler") >= 0:
                        valstr = "[" + str(i.default_value[0]) + "," + str(i.default_value[1]) + "," + str(i.default_value[2]) + "]"
                                            
                    sp = sp + nodevars[count] + ".inputs['" + i.name + "'].default_value = " + valstr + "\n"
                except:
                    print(count, m.name, i.name, "Error")
                    sp = sp + "\n#Error: " + m.name + " > " + i.name + " \n"
        count += 1
        sp = sp + "\n"


    s = s + sp + "\n### Node-to-Script End\n"
    print(s)

    dir = bpy.path.abspath("//")
    today = datetime.now()
    outfilename = dir +  mat.name.replace(".","") + "_NodeToScript_" + today.strftime("%Y%m%d") + ".py"

    print (outfilename)

    outfile = codecs.open(outfilename, "w", "utf-8")
    outfile.write(s)
    outfile.close()
    rtool.r_status = outfilename + " written."

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
    
class CNS_OT_CNodeToScript(bpy.types.Operator):
    bl_idname = "node.script"
    bl_label = "Nodes to Script"
    bl_description = "Convert shader nodes to a python script."

    def execute(self, context):
        scene = context.scene
        rtool = scene.r_tool
        Nodetoscript(rtool)
        
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
        layout.prop(rtool, "r_ttradius")
        layout.operator("turn.table", text = "Turntable", icon='OUTLINER_OB_CAMERA')
        layout.operator("node.script", text = "Nodes to Script", icon='NETWORK_DRIVE')
        layout.label(text = "Status : " + rtool.r_status)


class CCProperties(PropertyGroup):
    
    r_outfilename: StringProperty(
        name = "Out File Name",
        description = "Name of the joined movie",
        default = "joinedoutput"
      )

    r_status: StringProperty(
        name = "Status",
        description = "Status of commands",
        default = "Ready"
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
    
    r_ttradius: FloatProperty(
        name = "Turntable Radius",
        description = "Turntable radius",
        default = 2.0,
        min = 0
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
    CTA_OT_CTurntable,
    CNS_OT_CNodeToScript
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