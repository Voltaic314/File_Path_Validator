from FPV import FPV_Dropbox


def main():
    example_path = "folder**/file.txt"

    validator = FPV_Dropbox(example_path, file_added=True, auto_validate=False, relative=True)

    print(f"Original Path: {example_path}\n")

    # validate the path to show the issues
    try:
        issues = validator.validate()
        if not issues:
            print("Cleaned path is valid!")
    except ValueError as e:
        print(f"Validation Error:\n{e}")

    cleaned_path = validator.clean()
    print(f"Cleaned Path: {cleaned_path}\n")


if __name__ == "__main__":
    main()
