# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

'''
Rotate function:
Toggle between the rotated and original versions of the images
Duplicate and rotate the images from selected image texture nodes
Save the duplicate to disk adding "_rotated" before file extension.

Toggle function:
Toggle box and flat project for all selected image texture nodes
Set the blend value to a hardcoded 0.2
'''

import bpy
from pathlib import Path
from PIL import Image





bl_info = {
    "name": "BoxProject Tools",
    "author": "Erik Selin",
    "version": (1, 1),
    "blender": (4, 0, 2),
    "location": "Search, 'RotateImage' mapped to ALT+W, 'BoxToggle' mapped to ALT+Q",
    "description": "Rotates texture image maps and toggle Box project, note that this addon save imagefiles to disk.",
    "warning": "",
    "wiki_url": "https://www.artisticrender.com",
    "category": "Shader Editor",
}

def rotate_func(context):



    for node in bpy.context.active_object.active_material.node_tree.nodes:
        if node.select == True:
            if node.type == "TEX_IMAGE":
                if  node.image:
                    
                    #define parameters
                    numberFile = False
                    tempName = node.image.name

                    imageformat = tempName[tempName.rfind("."):]
                    abs_filepath = bpy.path.abspath(node.image.filepath)
                    image_set = False

                    #test to see if filename ends with a file extension or texture.jpg.001 or any other number.
                    #really just test if the last character is a number.
                    try:
                        int(tempName[-1])
                    except: pass
                    else:
                        numberExt = tempName[-4:]
                        tempName = tempName[:-4]
                        numberFile = True

                    #check if image is the rotated version or not by looking at the filename
                    if tempName[-(len(imageformat)+len("_rotated".lower())):-len(imageformat)] == "_rotated":
                        rotated = True
                        filename = ''.join(tempName.rsplit("_rotated".lower(), 1))
                    else:
                        rotated = False
                        name, ext = tempName.rsplit('.', maxsplit = 1)
                        filename = "{name}_rotated.{ext}".format(name=name, ext=ext)

                    #set the path after finding out if the current image is rotated or not.
                    filepath = bpy.path.abspath(node.image.filepath)[:abs_filepath.rfind("\\")+1] + filename

                    #if the extension is a number, reset the filename once the filepath is set to once again contain the number ending.
                    if numberFile == True:
                            filename = filename + numberExt

                    for i in bpy.data.images:
                        if i.name == filename:
                            node.image = bpy.data.images[filename]
                            image_set = True
                            break

                    #load the right image
                    if Path(filepath).is_file() and image_set == False:
                        node.image = bpy.data.images.load(filepath = filepath)
                    #or rotate and load if the rotated image doesn't exist.
                    elif image_set == False:
                        colorImage  = Image.open(bpy.path.abspath(node.image.filepath))
                        if rotated:
                            transposed  = colorImage.transpose(Image.ROTATE_270)
                        else:
                            transposed  = colorImage.transpose(Image.ROTATE_90)
                        transposed.save(fp=filepath)
                        node.image = bpy.data.images.load(filepath = filepath)

def toggle_func(context):
    for node in bpy.context.active_object.active_material.node_tree.nodes:
        if node.select == True:
            if node.type == "TEX_IMAGE":
                if node.inputs.data.projection != 'BOX':
                    node.inputs.data.projection = 'BOX'
                    node.inputs.data.projection_blend = 0.2
                else:
                    node.inputs.data.projection = 'FLAT'

class BoxToggle(bpy.types.Operator):
    bl_idname = "node.batchbox"
    bl_label = "BoxToggle"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        #take a look at this line, is it right?
        return context.active_object is not None

    def execute(self, context):
        toggle_func(context)
        return {'FINISHED'}

class RotateImage(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "node.rotateimage"
    bl_label = "RotateImage"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        #take a look at this line, is it right?
        return context.active_object is not None

    def execute(self, context):
        rotate_func(context)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(BoxToggle)
    bpy.utils.register_class(RotateImage)

    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Node Editor", space_type="NODE_EDITOR")
        kmi = km.keymap_items.new('node.batchbox', 'Q', 'PRESS', alt=True)

        km = kc.keymaps.new(name="Node Editor", space_type="NODE_EDITOR")
        kmi = km.keymap_items.new('node.rotateimage', 'W', 'PRESS', alt=True)

def unregister():
    bpy.utils.unregister_class(BoxToggle)
    bpy.utils.unregister_class(RotateImage)

    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps["Node Editor"]
        for kmi in km.keymap_items:
            if kmi.idname == 'node.batchbox':
                km.keymap_items.remove(kmi)
                break
        for kmi in km.keymap_items:
            if kmi.idname == 'node.rotateimage':
                km.keymap_items.remove(kmi)
                break


if __name__ == "__main__":
    register()
