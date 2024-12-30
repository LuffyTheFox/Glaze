from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.types import Operator, Panel
from bpy.props import StringProperty, FloatProperty
import bpy

try:
    from PIL import Image
    import numpy as np
    from hashlib import sha256
    import secrets
    import traceback
except ImportError:
    print("Some required libraries are not installed. Functionality will be limited.")

# Применение минимального adversarial шума
def apply_minimal_adversarial_noise(img_array, epsilon=1.0):
    img_array_float = img_array.astype(np.float32)

    # Вычисляем градиенты изображения
    gradients = np.gradient(img_array_float)
    
    # Меньшая амплитуда для шума, чтобы он был едва заметен
    gradient_magnitude = np.sqrt(np.square(gradients[0]) + np.square(gradients[1]))
    gradient_sign = np.sign(gradient_magnitude)
    
    # Генерация минимального шума с малой амплитудой
    adversarial_noise = epsilon * gradient_sign
    return np.clip(img_array_float + adversarial_noise, 0, 255).astype(np.uint8)

# Встраивание скрытых данных с минимальными изменениями
def embed_hidden_data_in_subtle_areas(img_array, hidden_data, epsilon=1.0):
    img_array_float = img_array.astype(np.float32)
    
    # Генерация и добавление малозаметного adversarial noise
    img_array_float = apply_minimal_adversarial_noise(img_array_float, epsilon)

    # Встраиваем скрытые данные с минимальными изменениями
    hidden_data_bytes = hidden_data.encode('utf-8')
    pattern_index = 0
    height, width, channels = img_array_float.shape
    for x in range(height):
        for y in range(width):
            if (x + y) % 50 == 0:  # Редкие изменения в изображении
                for channel in range(channels):
                    if pattern_index < len(hidden_data_bytes):
                        img_array_float[x, y, channel] ^= hidden_data_bytes[pattern_index]  # Применяем XOR
                        pattern_index += 1
    return np.clip(img_array_float, 0, 255).astype(np.uint8)

# Генерация и применение криптографического шума на основе хеша изображения
def generate_cryptographic_noise(img_array, intensity=1.0):
    height, width, channels = img_array.shape
    img_hash = sha256(img_array.tobytes()).digest()  # Хэш изображения для защиты
    noise = np.frombuffer(img_hash * ((height * width * channels) // len(img_hash) + 1), dtype=np.uint8)
    noise = noise[:height * width * channels].reshape((height, width, channels))
    noise = (noise / 255.0 - 0.5) * 2 * intensity
    return noise.astype(np.float32)

def apply_cryptographic_noise(img_array, intensity=1.0):
    noise = generate_cryptographic_noise(img_array, intensity)
    return np.clip(img_array + noise, 0, 255).astype(np.uint8)

# Встраивание уникального идентификатора в изображение
def embed_unique_identifier(img_array_noisy):
    height, width, channels = img_array_noisy.shape
    # Генерация уникального идентификатора на основе хеша изображения
    unique_id = sha256(img_array_noisy.tobytes()).hexdigest()[:16]  # Короткий хеш
    unique_id_bytes = unique_id.encode('utf-8')

    # Встраиваем идентификатор в пиксели
    pattern_index = 0
    for x in range(height):
        for y in range(width):
            if (x + y) % 10 == 0:  # Каждые 10 пикселей модифицируем
                for channel in range(channels):
                    if pattern_index < len(unique_id_bytes):
                        img_array_noisy[x, y, channel] ^= unique_id_bytes[pattern_index]  # Применяем XOR с байтом из уникального идентификатора
                        pattern_index += 1
    return img_array_noisy

# Основная функция для защиты изображения
def protect_image(image_path, output_path, intensity=1.0):
    try:
        img = Image.open(image_path)
        img_array = np.array(img, dtype=np.uint8)

        # Генерация скрытых данных с использованием secrets
        hidden_data = secrets.token_urlsafe(32)  # Генерация случайных секретных данных
        img_array_adv = embed_hidden_data_in_subtle_areas(img_array, hidden_data)

        # Применение криптографического шума
        img_array_noisy = apply_cryptographic_noise(img_array_adv, intensity)

        # Встраивание уникального идентификатора и скрытых данных
        img_array_noisy = embed_unique_identifier(img_array_noisy)

        # Сохранение изображения в формате PNG или JPEG
        modified_img = Image.fromarray(img_array_noisy)
        modified_img.save(output_path, format="PNG" if output_path.endswith(".png") else "JPEG", quality=95)
        print(f"Image successfully protected and saved to {output_path}")

    except Exception as e:
        print(f"Error processing the image: {e}")

# Blender оператор для защиты изображения
class GLAZE_OT_ProtectOperator(Operator, ImportHelper, ExportHelper):
    bl_idname = "glaze.protect_operator"
    bl_label = "Protect Image"
    filename_ext = ".png"
    filter_glob: StringProperty(default="*.png;*.jpg;*.jpeg;*.bmp", options={'HIDDEN'})

    intensity: FloatProperty(name="Noise Intensity", default=1.0, min=0.01, max=1.0)

    def execute(self, context):
        try:
            input_path = self.filepath
            output_path = bpy.path.ensure_ext(self.filepath, ".protected.png")
            protect_image(input_path, output_path, self.intensity)  # Модификация изображения с защитой
            self.report({'INFO'}, f"Image protected and saved as: {output_path}")
            return {'FINISHED'}
        except RuntimeError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        except Exception:
            error_traceback = traceback.format_exc()
            self.report({'ERROR'}, f"An unexpected error occurred:\n{error_traceback}")
            return {'CANCELLED'}

# Blender панель для UI
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

# Регистрация классов
def register():
    bpy.utils.register_class(GLAZE_OT_ProtectOperator)
    bpy.utils.register_class(GLAZE_PT_ProtectPanel)

def unregister():
    bpy.utils.unregister_class(GLAZE_OT_ProtectOperator)
    bpy.utils.unregister_class(GLAZE_PT_ProtectPanel)
