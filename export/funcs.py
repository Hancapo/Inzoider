from bpy.types import Object, Image
import hashlib
import bpy
from math import radians
import os
import time
import struct
from .meta import Meta
import shutil

def get_obj_extents(obj: Object) -> tuple:
    """Gets proper extents of object to match inZOI scale."""
    return list(obj.dimensions * 50)
        
def generate_md5_from_str(_str: str) -> str:
    """Generates an MD5 hash from a string."""
    text_bytes = _str.encode('utf-8')
    hash_md5 = hashlib.md5(text_bytes)
    return hash_md5.hexdigest()

def current_time_str() -> str:
    """Returns the current time in a string format."""
    return time.strftime("%Y%m%d-%H%M%S")

def convert_image_to_format(path: str, img: Image, format: str, name: str, quality: int = 95) -> str:
    """Converts the selected thumbnail to another supported format."""
    scene = bpy.context.scene
    config = scene.render.image_settings
    config.file_format = format
    config.quality = quality
    
    extension = 'jpg' if format == 'JPEG' else 'bmp'
    
    try:
        img.save_render(f"{path}/{name}.{extension}", scene=scene)
    except Exception as e:
        print(f"Error converting image: {str(e)}")
    
def create_folder(name: str) -> str:
    """Creates a folder using the hashed name from the object and current time in the export directory."""
    path = bpy.path.abspath(f"//{name}")
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def export_obj_as_glb(obj: Object, filepath: str, name: str) -> None:
    """Exports an object as a GLB file."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=filepath + f"/{name}.glb", use_selection=True, export_animations=False, export_draco_mesh_compression_enable=False, export_format='GLB')
    obj.select_set(False)

def change_visual_rotation_to_obj(obj: Object, apply: bool) -> None:
    """Applies or unapplies a 90-degree rotation to the Z axis visually and resets the rotation data."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.rotation_mode = 'XYZ'
    if apply:
        obj.rotation_euler.z = radians(90)
    else:
        obj.rotation_euler.z = radians(-90)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    obj.select_set(False)

def change_selection(self, context):
    if len(context.scene.obj_craft_list) == 0:
        return
    selected_item = context.scene.obj_craft_list[context.scene.obj_craft_index]
    if selected_item:
        bpy.ops.object.select_all(action='DESELECT')
        selected_item.mesh.select_set(True)
        
def get_author_from_printed_file(filepath: str) -> str:
    """Returns the author from the printed.dat file."""
    with open(filepath, 'rb') as file:
        file.seek(4)
        data2 = struct.unpack('<i', file.read(4))[0]
        author_str = file.read(data2-28).decode('utf-8')
        return author_str
    
def file_exists(filepath: str) -> bool:
    """Checks if a file exists."""
    return os.path.isfile(filepath)

def folder_exists(filepath: str) -> bool:
    """Checks if a folder exists."""
    return os.path.isdir(filepath)

def process_item(self, scene, item):
        from ..preferences import get_addon_prefs
        prefs = get_addon_prefs()

        hash_name = generate_md5_from_str(f"{item.title}{current_time_str()}")
        new_folder = create_folder(prefs.my3dprinter_path + f"/{hash_name.upper()}")
        if item.type == 'Character':
            change_visual_rotation_to_obj(item.mesh, True)
            export_obj_as_glb(item.mesh, new_folder, hash_name.upper())
            change_visual_rotation_to_obj(item.mesh, False)
        else:
            export_obj_as_glb(item.mesh, new_folder, hash_name.upper())
        if item.thumbnail:
            convert_image_to_format(new_folder, item.thumbnail, "JPEG", "thumbnail1")
            convert_image_to_format(new_folder, item.thumbnail, "BMP", "original")
                
        meta = Meta(
                    [0, 0, 0],
                    [0, 0, 0] if item.type == 'Character' else [0, -90, 0],
                    get_obj_extents(item.mesh),
                    item.title,
                    item.description,
                )
        meta.export_to_file(f"{new_folder}/meta.json")
        copy_printed_file(f"{new_folder}/printed.dat")
        self.report({'INFO'}, f"Craft '{item.title}' exported successfully!")

        
def copy_printed_file(filepath: str) -> None:
    """Copies the printed.dat file to the 3D prints directory."""
    from ..preferences import get_addon_prefs
    prefs = get_addon_prefs()
    if not prefs.is_printed_file_loaded:
        return
    else:
        printed_file = prefs.example_printed_file_path
        shutil.copyfile(printed_file, filepath)
