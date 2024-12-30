English:
Glaze. This is a cryptographic image protection addon that helps protect images from being copied by AI. This addon disrupts the CLIP Vision and CLIP image classification system.

This addon performs the main protection operation: it converts an image into cryptographic noise based on the SHA256 image hash and restores it, making it very difficult for AI to replicate, as the noise is no longer random but completely unique and depends on the input image.

This addon aims to provide protection for 2D artists' works, helping to prevent unauthorized AI copying.

Russian:
Glaze. Это дополнение для криптографической защиты изображений, которое помогает защитить изображения от копирования с помощью ИИ. Это дополнение нарушает работу системы CLIP Vision и классификации изображений CLIP.

Это дополнение выполняет основную операцию защиты: оно преобразует изображение в криптографический шум на основе хеша изображения SHA256 и восстанавливает его, что делает для ИИ очень сложным его воспроизведение, поскольку шум больше не является случайным, а полностью уникален и зависит от входного изображения.

Это дополнение направлено на защиту работ 2D-художников, помогая предотвратить несанкционированное копирование ИИ.

How to install the addon?

    Download the Addon
        Download the addon .zip file. Use green button on GitHub page: Code -> Download ZIP
        Or use following link: https://github.com/LuffyTheFox/Glaze/archive/refs/heads/main.zip

    Open Blender
        Launch Blender.

    Install the Addon
        Go to Edit > Preferences.
        Click on Add-ons tab, then click Install.
        Select the downloaded .zip file and click Install Add-on.

    Enable the Addon
        Find "Glaze: Protect Image" in the list and check the box to enable it.
        Use Install Libraries button to install python libraries for addon in your Blender.
        Disable and Enable addon in blender preferences.

    Access the Addon
        In the 3D View, go to the Glaze tab (N button) in the right panel.

    Use the Addon
        Click Select Image to choose an image.
        The addon will process and save the protected image as .protected.png.
