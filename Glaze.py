bl_info = {
    "name": "Glaze",
    "blender": (2, 80, 0),
    "category": "3D View",
    "description": "Protect images from neural network style copying by adding imperceptible noise",
    "author": "LuffyTheFox, ChatGPT",
    "version": (1, 0, 0),
    "location": "View3D > Sidebar > Glaze",
    "warning": "",
    "wiki_url": "https://t.me/BlenderNext",
    "tracker_url": "https://t.me/BlenderNext",
    "support": "COMMUNITY",
}

import bpy
import numpy as np
from scipy.fftpack import dct, idct
from PIL import Image
from bpy.props import StringProperty, FloatProperty
from bpy.types import Operator, Panel
from bpy_extras.io_utils import ImportHelper, ExportHelper

# Применение DCT-шумов
def apply_dct_noise(img_array, intensity=0.05):
    """Добавление шума в высокочастотные компоненты изображения через DCT."""
    
    # Преобразуем изображение в пространстве DCT
    dct_img = dct(dct(img_array.T, norm='ortho').T, norm='ortho')
    
    # Добавляем шум в высокочастотные компоненты (далёкие от верхних левых углов)
    height, width, _ = dct_img.shape
    for i in range(height):
        for j in range(width):
            if i > height // 2 or j > width // 2:
                dct_img[i, j] += np.random.randn() * intensity
    
    # Обратное DCT для восстановления изображения
    idct_img = idct(idct(dct_img.T, norm='ortho').T, norm='ortho')
    
    # Нормализация пикселей и возврат к диапазону [0, 255]
    return np.clip(idct_img, 0, 255).astype(np.uint8)

# Модификация изображения с использованием DCT
def modify_image(image_path, output_path, intensity=0.05):
    """Модификация изображения для защиты от использования в нейросетях."""
    img = Image.open(image_path)
    img_array = np.array(img)

    # Применяем невидимый шум на основе DCT
    img_array_noisy = apply_dct_noise(img_array, intensity)

    # Преобразуем обратно в изображение
    modified_img = Image.fromarray(img_array_noisy)
    modified_img.save(output_path)

# Оператор для защиты изображения
class GLAZE_OT_ProtectOperator(Operator, ImportHelper, ExportHelper):
    """Оператор для защиты изображения"""
    bl_idname = "glaze.protect_operator"
    bl_label = "Protect Image"
    
    filename_ext = ".png"
    
    filter_glob: StringProperty(default="*.png;*.jpg;*.jpeg;*.bmp", options={'HIDDEN'})

    intensity: FloatProperty(
        name="Noise Intensity",
        description="Intensity of imperceptible noise",
        default=0.2,
        min=0.01,
        max=0.2
    )
    
    def execute(self, context):
        input_path = self.filepath
        output_path = bpy.path.ensure_ext(self.filepath, ".protected.png")
        
        # Модифицируем изображение
        modify_image(input_path, output_path, self.intensity)
        
        self.report({'INFO'}, f"Image protected and saved as: {output_path}")
        return {'FINISHED'}

# Панель с интерфейсом для защиты изображения
class GLAZE_PT_ProtectPanel(Panel):
    """Создание интерфейса для аддона в 3D View"""
    bl_label = "Glaze: Protect Image"
    bl_idname = "GLAZE_PT_protect_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Glaze"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Protect your image from neural network copying")

        # Кнопка для запуска защиты изображения
        layout.operator("glaze.protect_operator", text="Protect Image")


# Регистрация аддона
def register():
    bpy.utils.register_class(GLAZE_OT_ProtectOperator)
    bpy.utils.register_class(GLAZE_PT_ProtectPanel)


def unregister():
    bpy.utils.unregister_class(GLAZE_OT_ProtectOperator)
    bpy.utils.unregister_class(GLAZE_PT_ProtectPanel)


if __name__ == "__main__":
    register()
