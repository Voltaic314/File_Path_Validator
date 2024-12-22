from FPV import FPV_Windows


def main():
    # Define an example path
    example_path = "C:\\ Broken\\ **path\\to\\||file . txt"

    # Instantiate the FPV_Windows object without auto-validation
    validator = FPV_Windows(example_path, relative=False, auto_validate=False, file_added=True)

    print(f"Original Path: {example_path}\n")

    # Step 1: Validate the original path
    try:
        print("Validating the original path...")
        issues = validator.validate(raise_error=True)  # This will raise a ValueError if issues exist
        if not issues:
            print("Original path is valid!")
    except ValueError as e:
        print(f"Validation Error:\n{e}")

    # Step 2: Clean the original path
    print("\nCleaning the path...")
    cleaned_path = validator.clean()
    print(f"Cleaned Path: {cleaned_path}")

    # Step 3: Validate the cleaned path
    try:
        print("\nValidating the cleaned path...")
        issues = validator.validate(raise_error=True)
        if not issues:
            print("Cleaned path is valid!")
    except ValueError as e:
        print(f"Validation Error (Cleaned Path):\n{e}")

    # Step 4: Dynamic path building
    print("\n--- Dynamic Path Building ---")
    print("Starting with root path: C:\\")
    dynamic_validator = FPV_Windows("C:\\", relative=False)
    print(f"Initial Path: {dynamic_validator.get_full_path()}")

    print("\nAdding parts dynamically...")
    dynamic_validator.add_part("NewFolder")
    print(f"After adding 'NewFolder': {dynamic_validator.get_full_path()}")
    dynamic_validator.add_part("AnotherFolder")
    print(f"After adding 'AnotherFolder': {dynamic_validator.get_full_path()}")
    dynamic_validator.add_part("file.txt", is_file=True)
    print(f"After adding 'file.txt': {dynamic_validator.get_full_path()}")

    # Validate the dynamically built path
    print("\nValidating the dynamically built path...")
    try:
        dynamic_validator.validate(raise_error=True)
        print("Dynamically built path is valid!")
    except ValueError as e:
        print(f"Validation Error (Dynamic Path):\n{e}")

    # Step 5: Modify the path
    print("\nModifying the path...")
    dynamic_validator._path_helper.parts[1]["part"] = "RenamedFolder"
    print(f"After renaming 'NewFolder' to 'RenamedFolder': {dynamic_validator.get_full_path()}")

    # Step 6: Remove a part
    print("\nRemoving a part...")
    dynamic_validator.remove_part(2)  # Remove 'AnotherFolder'
    print(f"After removing 'AnotherFolder': {dynamic_validator.get_full_path()}")

    # Step 7: Validate the modified path
    print("\nValidating the modified path...")
    try:
        dynamic_validator.validate(raise_error=True)
        print("Modified path is valid!")
    except ValueError as e:
        print(f"Validation Error (Modified Path):\n{e}")


if __name__ == "__main__":
    main()
