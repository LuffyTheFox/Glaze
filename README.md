Glaze. Cryptographic image protection addon which helps protecting images from being copied by AI. 
The addon performs two main operations:

    Apply Cryptographic Noise and Watermark: It modifies an image by embedding a cryptographic noise, making it harder for AI systems to replicate or copy the image accurately. The noise is generated based on the hash of the image, and the watermark is embedded in the YCbCr color space to avoid noticeable changes in the image.

    Blender Integration: The addon provides a Blender panel and operator that allows users to select an image and apply the protection process directly from the Blender interface. The image is saved with a modified file name (e.g., .protected.png) and can be adjusted with a noise intensity parameter.

Key Features:

    Cryptographic Noise: Adds unique noise to the image based on its hash, making it difficult for AI to recreate.
    User-Friendly Interface: Integrated into Blender with a custom panel and operator for easy image protection.
    Supports Multiple Image Formats: Can process common image formats like PNG, JPEG, BMP, and others.

Libraries Used:

    cv2, PIL, numpy, scipy, and hashlib are used to manipulate and process the images.

Workflow:

    The user selects an image through the Blender file picker.
    The addon converts image to cryptographic noise and restores it.
    The modified image is saved with a .protected.png extension.

This addon aims to provide protection for 2D artists' works, helping prevent unauthorized AI copying.

How to install addon?

    Download the Addon
        Download the addon .zip file.

    Open Blender
        Launch Blender.

    Install the Addon
        Go to Edit > Preferences.
        Click on Add-ons tab, then click Install.
        Select the downloaded .zip file and click Install Add-on.

    Enable the Addon
        Find "Glaze: Protect Image" in the list and check the box to enable it.
        Use Install Libraries button to install python libraries for addon in your Blender.

    Access the Addon
        In the 3D View, go to the Glaze tab in the right panel.

    Use the Addon
        Click Select Image to choose an image.
        The addon will process and save the protected image as .protected.png.

You’re done! The addon will now protect your images from AI copying.
