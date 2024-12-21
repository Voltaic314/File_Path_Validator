from FPV import FPV_Windows


def main():
    # Define an example path
    example_path = "C:\\ Broken\\ **path\\to\\||file . txt"

    # Instantiate the FPV_Windows object without auto-validation
    validator = FPV_Windows(example_path, relative=False, auto_validate=False, file_added=True)

    print(f"Original Path: {example_path}\n")

    try:
        # Validate the original path
        print("Validating the original path...")
        issues = validator.validate(raise_error=True)  # This will raise a ValueError if issues exist
        if not issues:
            print("Original path is valid!")

    except ValueError as e:
        print(f"Validation Error:\n{e}")

    print("\nCleaning the path...")
    # Clean the path
    cleaned_path = validator.clean()
    print(f"Cleaned Path: {cleaned_path}")

    print("\nValidating the cleaned path...")

    try:
        # Validate the cleaned path
        issues = validator.validate(raise_error=True)
        if not issues:
            print("Cleaned path is valid!")

    except ValueError as e:
        print(f"Validation Error (Cleaned Path):\n{e}")

if __name__ == "__main__":
    main()
