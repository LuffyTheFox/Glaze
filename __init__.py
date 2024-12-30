#!/usr/bin/python3
# copyright (c) 2023-2024 LuffyTheFox

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

from bpy.types import AddonPreferences
import ctypes
import os
from . import install_libraries
from . import operators
import bpy
bl_info = {
    "name": "Glaze",
    "author": "ChatGPT, LuffyTheFox",
    "description": "Protect images from neural network",
    "blender": (4, 2, 3),
    "version": (2, 0, 0),
    "location": "View3D > Sidebar > Glaze",
    "warning": "",
    "wiki_url": "https://t.me/BlenderNext",
    "tracker_url": "https://t.me/BlenderNext",
    "category": "3D View"
}

passed = False


class GLAZE_AddonPreferences(AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout

        if not install_libraries.are_dependencies_installed():
            row = layout.row()
            # Кнопка для установки библиотек
            row.operator("glaze.install_libraries")
            row = layout.row()
            row.label(
                text="After you have Installed Libraries, please re-boot Blender")
        else:
            layout.label(text="Libraries are installed")
            if ctypes.windll.shell32.IsUserAnAdmin() == 1:
                layout.label(text="Admin mode, you can start using addon now")


class GLAZE_OT_InstallLibraries(bpy.types.Operator):
    bl_idname = "glaze.install_libraries"
    bl_label = "Install Libraries"
    bl_description = "Install the required libraries for the Glaze addon"

    def execute(self, context):
        try:
            install_libraries.setup_dependencies()
            install_libraries.set_dependencies_installed(
                True)  # Устанавливаем флаг успешной установки
            self.report({'INFO'}, "Libraries installed successfully")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to install libraries: {str(e)}")
            return {'CANCELLED'}


def register():
    try:
        install_libraries.checkDeps()
        install_libraries.set_dependencies_installed(True)
        bpy.utils.register_class(GLAZE_AddonPreferences)
        bpy.utils.register_class(GLAZE_OT_InstallLibraries)
        operators.register()
    except ModuleNotFoundError:
        install_libraries.set_dependencies_installed(False)
        bpy.utils.register_class(GLAZE_AddonPreferences)
        bpy.utils.register_class(GLAZE_OT_InstallLibraries)


def unregister():
    try:
        operators.unregister()
    except Exception:
        pass  # Игнорируем, если operators не был зарегистрирован
    if hasattr(GLAZE_OT_InstallLibraries, 'bl_rna'):
        bpy.utils.unregister_class(GLAZE_OT_InstallLibraries)
    if hasattr(GLAZE_AddonPreferences, 'bl_rna'):
        bpy.utils.unregister_class(GLAZE_AddonPreferences)


if __name__ == "__main__":
    register()
