from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.types import Operator, Panel
from bpy.props import StringProperty, FloatProperty, IntProperty
import bpy
from . import install_libraries

try:
    import cv2
    from concurrent.futures import ThreadPoolExecutor
    from PIL import Image
    from scipy.fftpack import dct, idct
    import numpy as np
except ImportError:
    print("Some required libraries are not installed. Functionality will be limited.")

# Вспомогательные функции для работы с цветовыми пространствами
def rgb_to_ycbcr(rgb):
    y = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    cb = -0.1687 * rgb[:, :, 0] - 0.3313 * rgb[:, :, 1] + 0.5 * rgb[:, :, 2] + 128
    cr = 0.5 * rgb[:, :, 0] - 0.4187 * rgb[:, :, 1] - 0.0813 * rgb[:, :, 2] + 128
    return np.dstack((y, cb, cr))

def ycbcr_to_rgb(ycbcr):
    y, cb, cr = cv2.split(ycbcr)
    r = y + 1.402 * (cr - 128)
    g = y - 0.34414 * (cb - 128) - 0.71414 * (cr - 128)
    b = y + 1.772 * (cb - 128)
    return np.dstack((r, g, b)).clip(0, 255).astype(np.uint8)

# Встраивание стеганографического водяного знака
def embed_steganographic_watermark(img_array, watermark):
    ycbcr = rgb_to_ycbcr(img_array)
    y = ycbcr[:, :, 0]
    y = np.uint8(y)  # Преобразуем в uint8 перед операцией
    watermark = np.uint8(watermark)  # Убедимся, что watermark тоже uint8
    y = (y & ~1) | watermark  # Побитовая операция
    ycbcr[:, :, 0] = y
    return ycbcr_to_rgb(ycbcr)

# Адаптивный шум
def apply_adaptive_noise(img_array, intensity=0.01):
    edges = cv2.Canny(img_array,25,255,L2gradient=False)
    mask = np.where(edges > 0, 0, 1)
    noise = np.random.normal(0, intensity, img_array.shape)
    return np.clip(img_array + (noise * mask[:, :, np.newaxis]), 0, 255).astype(np.uint8)

# Применение многочастотного шума
def apply_multifrequency_noise_block(block, intensity=0.1):
    height, width, _ = block.shape
    dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')

    mask = np.ones_like(dct_block, dtype=np.float64)  # Убедимся, что mask имеет правильный тип
    mask[height//4:, width//4:] += np.random.normal(0, intensity, mask[height//4:, width//4:].shape)

    dct_block = dct_block * mask
    return idct(idct(dct_block.T, norm='ortho').T, norm='ortho')

def apply_multifrequency_noise_multithreaded(img_array, intensity=0.1, num_workers=4):
    height = img_array.shape[0]
    block_size = height // num_workers
    blocks = [img_array[i:i + block_size, :]
              for i in range(0, height, block_size)]

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(
            apply_multifrequency_noise_block,
            blocks,
            [intensity] * len(blocks)
        ))

    return np.clip(np.vstack(results), 0, 255).astype(np.uint8)

# Комплексная функция защиты изображения
def modify_image(image_path, output_path, intensity=0.1, num_workers=4):
    try:
        img = Image.open(image_path)
        img_array = np.array(img, dtype=np.uint8)  # Преобразуем в uint8

        watermark = np.random.randint(0, 2, size=img_array.shape[:2], dtype=np.uint8)

        img_array = embed_steganographic_watermark(img_array, watermark)

        img_array = apply_adaptive_noise(img_array, intensity)
        img_array_noisy = apply_multifrequency_noise_multithreaded(
            img_array, intensity, num_workers)

        modified_img = Image.fromarray(img_array_noisy)
        modified_img.save(output_path)
    except ImportError:
        raise RuntimeError("Required libraries are not installed. Please install them to use this feature.")
    except Exception as e:
        raise RuntimeError(f"Error in image processing: {str(e)}")

# Оператор для защиты изображения
class GLAZE_OT_ProtectOperator(Operator, ImportHelper, ExportHelper):
    bl_idname = "glaze.protect_operator"
    bl_label = "Protect Image"
    filename_ext = ".png"
    filter_glob: StringProperty(
        default="*.png;*.jpg;*.jpeg;*.bmp", options={'HIDDEN'})

    intensity: FloatProperty(name="Noise Intensity", default=0.1, min=0.01, max=0.2)
    num_workers: IntProperty(name="Number of Threads", default=4, min=1, max=16)  # Изменено на IntProperty

    def execute(self, context):
        try:
            input_path = self.filepath
            output_path = bpy.path.ensure_ext(self.filepath, ".protected.png")
            modify_image(input_path, output_path,
                         self.intensity, int(self.num_workers))
            self.report(
                {'INFO'}, f"Image protected and saved as: {output_path}")
            return {'FINISHED'}
        except RuntimeError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"An error occurred: {str(e)}")
            return {'CANCELLED'}

# Панель для интерфейса
class GLAZE_PT_ProtectPanel(Panel):
    bl_label = "Glaze: Protect Image"
    bl_idname = "GLAZE_PT_protect_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Glaze"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Protect image from AI")
        if install_libraries.are_dependencies_installed():
            layout.operator("glaze.protect_operator", text="Select image")
        else:
            layout.label(
                text="Functionality not available. Install libraries.")

def register():
    bpy.utils.register_class(GLAZE_OT_ProtectOperator)
    bpy.utils.register_class(GLAZE_PT_ProtectPanel)

def unregister():
    bpy.utils.unregister_class(GLAZE_OT_ProtectOperator)
    bpy.utils.unregister_class(GLAZE_PT_ProtectPanel)
