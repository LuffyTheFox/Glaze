import os
import sys
import importlib
import subprocess

dependencies_installed = False


def checkDeps():
    import numpy
    import scipy
    import PIL
    import cv2
    import secrets
    set_dependencies_installed(True)


def are_dependencies_installed():
    global dependencies_installed
    return dependencies_installed


def set_dependencies_installed(are_installed):
    global dependencies_installed
    dependencies_installed = are_installed


def import_module(module_name, global_name=None, reload=True):
    """
    Import a module.
    :param module_name: Module to import.
    :param global_name: (Optional) Name under which the module is imported. If None the module_name will be used.
    :param reload: Whether to reload the module if it's already imported.
    :raises: ImportError and ModuleNotFoundError
    """
    if global_name is None:
        global_name = module_name

    if global_name in globals():
        if reload:
            importlib.reload(globals()[global_name])
    else:
        globals()[global_name] = importlib.import_module(module_name)


def install_pip():
    """
    Installs pip if not already present. Removes PIP_REQ_TRACKER to avoid path errors.
    """
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True)
    except subprocess.CalledProcessError:
        import ensurepip
        ensurepip.bootstrap()
        os.environ.pop("PIP_REQ_TRACKER", None)


def install_module(module_name, package_name=None, global_name=None):
    """
    Installs the package through pip and attempts to import the installed module.
    :param module_name: Module to import.
    :param package_name: (Optional) Name of the package that needs to be installed.
    :param global_name: (Optional) Name under which the module is imported.
    :raises: subprocess.CalledProcessError and ImportError
    """
    if package_name is None:
        package_name = module_name

    if global_name is None:
        global_name = module_name

    environ_copy = dict(os.environ)
    environ_copy["PYTHONNOUSERSITE"] = "1"

    try:
        subprocess.run([sys.executable, "-m", "pip", "install",
                       package_name], check=True, env=environ_copy)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package_name}: {e}")
        raise


def install_and_import_requirements():
    try:
        install_module('numpy')
        install_module('scipy')
        install_module('pillow')
        install_module('opencv-python')
        install_module('secrets')
        checkDeps()  # Check if all modules are now installed
    except Exception as e:
        print(f"Installation of dependencies failed: {e}")
        set_dependencies_installed(False)

# Call this function when you initialize your addon


def setup_dependencies():
    try:
        install_pip()
        install_and_import_requirements()
    except Exception as e:
        print(f"Could not set up dependencies: {e}")
        # Here you might want to alert the user through Blender's UI or log it
