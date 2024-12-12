Glaze: AI Image Protection Addon

Glaze is a Blender addon designed to protect the unique style of artists' images from AI-based algorithms, such as those used in LoRA (Low-Rank Adaptation) and other style-transfer technologies. The addon provides a set of tools for embedding subtle modifications into images to make them resistant to style cloning and analysis, helping safeguard the integrity of artistic works in the age of AI.
Features:

    Steganographic Watermarking: Embeds a hidden watermark in the luminance channel of the image, ensuring that it is not visible to the human eye but can be detected by the artist or through custom algorithms. This helps protect the image from unauthorized reproduction or analysis.

    Adaptive Noise Application: Adds noise to the image based on the detected edges, making it more difficult for AI models to extract clean, usable data for style cloning. The noise adapts to the image structure, blending seamlessly while adding protective elements.

    Multifrequency Noise with DCT: Applies noise in the frequency domain using Discrete Cosine Transform (DCT). This method targets the frequency components of the image, adding subtle variations that are harder to detect or undo by AI algorithms. It works in parallel, enhancing performance with multi-threading.

    Multithreading Support: To handle large images more efficiently, the addon splits the image into blocks and processes them concurrently, speeding up the operation and making it suitable for high-resolution images.

How It Works:

    Embed a Steganographic Watermark: The image is converted to the YCbCr color space, and the watermark is embedded in the Y (luminance) channel. The watermark is applied through bitwise operations, ensuring it's undetectable by human eye.

    Adaptive Noise: A noise layer is added to the image, with intensity based on edge detection. The noise helps obscure fine details, making it harder for AI models to replicate the image's features accurately.

    Multifrequency Noise: The image is divided into blocks, and noise is applied in the frequency domain using DCT. This operation is parallelized for better performance, allowing for faster processing times.

    Saving the Protected Image: The modified image is saved with a .protected.png extension, ensuring the protection process is non-destructive and easy to distinguish.

Use Case:

This addon is particularly useful for artists, photographers, and content creators who wish to protect their work from being cloned or analyzed by AI algorithms. It provides an additional layer of security, helping to maintain the uniqueness of artistic styles in an increasingly automated world.
Installation:

    Download the addon from the repository.
    In Blender, go to Edit > Preferences > Add-ons > Install.
    Select the .zip file of the addon.
    Enable the addon from the list of installed addons.

License:

This addon is open-source and available under the MIT License. Feel free to contribute and modify the code as needed.
