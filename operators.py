from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.types import Operator, Panel
from bpy.props import StringProperty, FloatProperty, IntProperty
import bpy

try:
    import cv2
    from concurrent.futures import ThreadPoolExecutor
    from PIL import Image
    from scipy.fftpack import dct, idct
    import numpy as np
    from hashlib import sha256
except ImportError:
    print("Some required libraries are not installed. Functionality will be limited.")

import traceback

# Generate cryptographic noise based on image hash
def generate_cryptographic_noise(img_array, intensity=1.0):
    height, width, _ = img_array.shape
    img_hash = sha256(img_array.tobytes()).digest()
    noise = np.frombuffer(img_hash * ((height * width * 3) // len(img_hash) + 1), dtype=np.uint8)
    noise = noise[:height * width * 3].reshape((height, width, 3))
    noise = (noise / 255.0 - 0.5) * 2 * intensity
    return noise.astype(np.float32)

# Apply cryptographic noise
def apply_cryptographic_noise(img_array, intensity=1.0):
    noise = generate_cryptographic_noise(img_array, intensity)
    return np.clip(img_array + noise, 0, 255).astype(np.uint8)

# Convert RGB to YCbCr
def rgb_to_ycbcr(rgb):
    y = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    cb = -0.1687 * rgb[:, :, 0] - 0.3313 * rgb[:, :, 1] + 0.5 * rgb[:, :, 2] + 128
    cr = 0.5 * rgb[:, :, 0] - 0.4187 * rgb[:, :, 1] - 0.0813 * rgb[:, :, 2] + 128
    return np.dstack((y, cb, cr))

# Convert YCbCr to RGB
def ycbcr_to_rgb(ycbcr):
    y, cb, cr = cv2.split(ycbcr)
    r = y + 1.402 * (cr - 128)
    g = y - 0.34414 * (cb - 128) - 0.71414 * (cr - 128)
    b = y + 1.772 * (cb - 128)
    return np.dstack((r, g, b)).clip(0, 255).astype(np.uint8)

# Modify image for protection
def modify_image(image_path, output_path, intensity=1.0):
    try:
        img = Image.open(image_path)
        img_array = np.array(img, dtype=np.uint8)

        img_array_noisy = apply_cryptographic_noise(img_array, intensity)

        modified_img = Image.fromarray(img_array_noisy)
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

    intensity: FloatProperty(name="Noise Intensity", default=1.0, min=0.01, max=1.0)

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
