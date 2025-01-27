import importlib
import os

MODULES_DIR = 'modules'

def load_module(module_name):
    try:
        module = importlib.import_module(module_name)
        return module
    except ImportError as e:
        print(f"Error loading module {module_name}: {e}")
        return None

def discover_modules():
    return [d for d in os.listdir(MODULES_DIR) if os.path.isdir(os.path.join(MODULES_DIR, d))]

def main():
    print("Discovering modules...")
    modules = discover_modules()
    for module in modules:
        print(f"Loading module: {module}")
        load_module(f"modules.{module}")

if __name__ == "__main__":
    main()
