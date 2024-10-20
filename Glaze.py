bl_info = {
    "name": "Glaze",
    "blender": (2, 80, 0),
    "category": "3D View",
    "description": "Protect images from neural network artstyle copying and LoRA by adding irreversible multi-frequency DCT noise",
    "author": "ChatGPT, LuffyTheFox",
    "version": (1, 2, 0),
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
from concurrent.futures import ThreadPoolExecutor
from bpy.props import StringProperty, FloatProperty
from bpy.types import Operator, Panel
from bpy_extras.io_utils import ImportHelper, ExportHelper

# Применение многочастотного шума с использованием мультипоточности
def apply_multifrequency_noise_block(block, intensity_low=0.05, intensity_mid=0.1, intensity_high=0.2):
    """Добавление шума в блок изображения через DCT (многопоточно)."""
    height, width, _ = block.shape

    # Преобразуем блок изображения в частотное пространство DCT
    dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')

    # Проход по каждому элементу блока
    for i in range(height):
        for j in range(width):
            # Низкочастотный шум
            if i < height // 4 and j < width // 4:
                dct_block[i, j] += np.random.randn() * intensity_low
            # Среднечастотный шум
            elif i < height // 2 and j < width // 2:
                dct_block[i, j] += np.random.randn() * intensity_mid
            # Высокочастотный шум
            else:
                dct_block[i, j] += np.random.randn() * intensity_high

    # Обратное преобразование DCT для восстановления блока
    return idct(idct(dct_block.T, norm='ortho').T, norm='ortho')

# Функция для разделения изображения на блоки и обработки их в потоках
def apply_multifrequency_noise_multithreaded(img_array, intensity_low=0.05, intensity_mid=0.1, intensity_high=0.2, num_workers=4):
    """Разделение изображения на блоки и обработка с использованием мультипоточности."""
    height, width, channels = img_array.shape
    block_size = height // num_workers  # Разделяем по вертикали на блоки
    blocks = [img_array[i:i + block_size, :] for i in range(0, height, block_size)]
    
    # Используем пул потоков для параллельной обработки блоков
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = executor.map(
            apply_multifrequency_noise_block, 
            blocks, 
            [intensity_low] * len(blocks), 
            [intensity_mid] * len(blocks), 
            [intensity_high] * len(blocks)
        )
    
    # Собираем результат обратно в одно изображение
    img_array_noisy = np.vstack(list(results))
    return np.clip(img_array_noisy, 0, 255).astype(np.uint8)

# Модификация изображения с добавлением многочастотного шума (многопоточно)
def modify_image(image_path, output_path, intensity_low=0.05, intensity_mid=0.1, intensity_high=0.2, num_workers=4):
    """Модификация изображения для защиты от нейросетей, с использованием мультипоточности."""
    img = Image.open(image_path)
    img_array = np.array(img)

    # Применяем многочастотный шум с использованием многопоточной обработки
    img_array_noisy = apply_multifrequency_noise_multithreaded(
        img_array, intensity_low, intensity_mid, intensity_high, num_workers
    )

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

    intensity_low: FloatProperty(
        name="Low Frequency Noise",
        description="Intensity of noise for low frequencies",
        default=0.05,
        min=0.01,
        max=0.2
    )

    intensity_mid: FloatProperty(
        name="Mid Frequency Noise",
        description="Intensity of noise for mid frequencies",
        default=0.1,
        min=0.01,
        max=0.2
    )

    intensity_high: FloatProperty(
        name="High Frequency Noise",
        description="Intensity of noise for high frequencies",
        default=0.2,
        min=0.01,
        max=0.2
    )

    num_workers: FloatProperty(
        name="Number of Threads",
        description="Number of threads to use for processing",
        default=4,
        min=1,
        max=16
    )
    
    def execute(self, context):
        input_path = self.filepath
        output_path = bpy.path.ensure_ext(self.filepath, ".protected.png")
        
        # Модифицируем изображение с использованием мультипоточности
        modify_image(input_path, output_path, self.intensity_low, self.intensity_mid, self.intensity_high, int(self.num_workers))
        
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
        layout.label(text="Protect image from AI")

        # Кнопка для запуска защиты изображения
        layout.operator("glaze.protect_operator", text="Select image")


# Регистрация аддона
def register():
    bpy.utils.register_class(GLAZE_OT_ProtectOperator)
    bpy.utils.register_class(GLAZE_PT_ProtectPanel)

def unregister():
    bpy.utils.unregister_class(GLAZE_OT_ProtectOperator)
    bpy.utils.unregister_class(GLAZE_PT_ProtectPanel)

if __name__ == "__main__":
    register()
