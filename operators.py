from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.types import Operator, Panel
from bpy.props import StringProperty, FloatProperty, IntProperty
import bpy

try:
    import cv2
    from PIL import Image
    import numpy as np
    import secrets
except ImportError:
    print("Some required libraries are not installed. Functionality will be limited.")

import traceback

# Усложнённое добавление адаптивного шума
def apply_robust_noise(img_array, intensity=0.05):
    # Используем криптографически стойкий генератор случайных чисел
    rng = np.random.default_rng(secrets.randbelow(1 << 32))
    noise = rng.normal(0, intensity, img_array.shape)

    # Генерация случайной маски с нелинейным распределением
    gradient_x = cv2.Sobel(img_array, cv2.CV_64F, 1, 0, ksize=3)
    gradient_y = cv2.Sobel(img_array, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = np.sqrt(np.sum(gradient_x**2 + gradient_y**2, axis=-1))
    mask = np.tanh(gradient_magnitude / (gradient_magnitude.max() + 1e-5))
    mask = mask[:, :, np.newaxis]  # Добавляем размер канала

    # Применяем шум с дополнительным преобразованием
    robust_noise = np.sin(noise + np.pi * mask)
    return np.clip(img_array + robust_noise * 255, 0, 255).astype(np.uint8)

# Изменённый процесс модификации изображения
def modify_image(image_path, output_path, intensity=0.1):
    try:
        img = Image.open(image_path)
        img_array = np.array(img, dtype=np.uint8)

        # Встроим шум и защиту
        img_array = apply_robust_noise(img_array, intensity)

        modified_img = Image.fromarray(img_array)
        modified_img.save(output_path)
    except Exception as e:
        error_traceback = traceback.format_exc()
        raise RuntimeError(f"Error in image processing: {str(e)}\nTraceback:\n{error_traceback}")

# Blender operator for image protection
class GLAZE_OT_ProtectOperator(Operator, ImportHelper, ExportHelper):
    bl_idname = "glaze.protect_operator"
    bl_label = "Protect Image"
    filename_ext = ".png"
    filter_glob: StringProperty(default="*.png;*.jpg;*.jpeg;*.bmp", options={'HIDDEN'})

    intensity: FloatProperty(name="Noise Intensity", default=0.1, min=0.01, max=0.2)

    def execute(self, context):
        try:
            input_path = self.filepath
            output_path = bpy.path.ensure_ext(self.filepath, ".protected.png")
            modify_image(input_path, output_path, self.intensity)
            self.report({'INFO'}, f"Image protected and saved as: {output_path}")
            return {'FINISHED'}
        except RuntimeError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        except Exception:
            error_traceback = traceback.format_exc()
            self.report({'ERROR'}, f"An unexpected error occurred:\n{error_traceback}")
            return {'CANCELLED'}

# Blender panel for the UI
class GLAZE_PT_ProtectPanel(Panel):
    bl_label = "Glaze: Protect Image"
    bl_idname = "GLAZE_PT_protect_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Glaze"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Protect image from AI")
        layout.operator("glaze.protect_operator", text="Select image")

# Register classes
def register():
    bpy.utils.register_class(GLAZE_OT_ProtectOperator)
    bpy.utils.register_class(GLAZE_PT_ProtectPanel)

def unregister():
    bpy.utils.unregister_class(GLAZE_OT_ProtectOperator)
    bpy.utils.unregister_class(GLAZE_PT_ProtectPanel)

if __name__ == "__main__":
    register()
