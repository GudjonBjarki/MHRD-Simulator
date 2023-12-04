from mhrd_parser import *
from schematic_library import SchematicLibrary

if __name__ == "__main__":
    import glob

    schematic_library = SchematicLibrary()

    for file in glob.glob("../schematics/**/*.mhrd", recursive=True):
        with open(file, "r") as f:
            print(f"Compiling {file}...")
            try:
                schematic = parse_mhrd_schematic(f.read())
                schematic_library.add_schematic(schematic)
                print(f"Success! {schematic.schematic_id} parsed from {file}")

            except Exception as e:
                print(f"Failed to parse {file}: {e}")

            print()

    for schematic in schematic_library.schematics:
        print(f"Obtaining truth table of {schematic.schematic_id}...")
        truth_table = schematic_library.get_scehematic_truth_table(schematic)

        for inputs, outputs in truth_table:
            print(f"{inputs} -> {outputs}")

        print()
