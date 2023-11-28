from components import *
from mhrd import *

if __name__ == "__main__":
    import glob

    component_library = ComponentLibrary()

    for file in glob.glob("../schematics/**/*.mhrd", recursive=True):

        with open(file, "r") as f:

            print(f"Compiling {file}...")
            try:
                component = parse_script(f.read())
                component_library.add_component(component)
                print(f"Success! {component.id} parsed from {file}")

            except Exception as e:
                print(f"Failed to parse {file}: {e}")
            
            print()

    for component in component_library.components:
        print(f"Obtaining truth table of {component.id}...")
        truth_table = component_library.get_component_truth_table(component)

        for inputs, outputs in truth_table:
            print(f"{inputs} -> {outputs}")

        print()