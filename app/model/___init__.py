import os
import importlib

def import_all_modules():
    # Get the list of all Python files in the model folder
    model_folder = os.path.dirname(__file__)
    module_files = [file[:-3] for file in os.listdir(model_folder) if file.endswith('.py') and file != '__init__.py']

    # Dynamically import all modules
    for module_name in module_files:
        module = importlib.import_module(f'.{module_name}', package='app.model')
        globals()[module_name] = module