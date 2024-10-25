# the purpose of this file is just to highlight how the code can be used.
from FPV import Validator


def main():
    example_path = " /path /to./file*.txt"
    
    # Create a validator object
    validator = Validator(example_path)

    # Access the original path
    print("Original Path:", validator.original_path)

    # Get a cleaned version of your path
    cleaned_path = validator.get_cleaned_path()
    print("Cleaned Path:", cleaned_path)  # Output should be "/path/to/file.txt"

    # Check if the original path is valid
    try:
        validator.check_if_valid()
        print("Path is valid!")
    except ValueError as e:
        print(f"Validation Error: {e}")

    # Auto-clean the path upon creating the validator object
    validator_auto_clean = Validator(example_path, auto_clean=True)
    print("Automatically Cleaned Path:", validator_auto_clean.path)


if __name__ == "__main__":
    main()
