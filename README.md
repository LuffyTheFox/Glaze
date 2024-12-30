Glaze. Cryptographic image protection addon which helps protecting images from being copied by AI.
This addon breaks CLIP Vision and CLIP image classification system.

This addon performs main protection operation, it converts an image to a cryptographic noise based on SHA256 image hash, and restores it making for AI very hard to replicate it, because noise is not random anymore and completely unique and depends from input image.

This addon aims to provide protection for 2D artists works, helping prevent unauthorized AI copying.

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
