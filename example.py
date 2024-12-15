# the purpose of this file is just to highlight how the code can be used.

# showing off the available OS classes
from FPV import FPV_Windows, FPV_MacOS, FPV_Linux

# showing off the available cloud storage classes
from FPV import FPV_Dropbox, FPV_Box, FPV_Egnyte, FPV_OneDrive, FPV_SharePoint, FPV_ShareFile


def main():
    example_path = "C:\\ Broken\\ **path\\to\\||file . txt"

    # Create a validator object
    FPVW = FPV_Windows(example_path, relative=False)
    # if the path did not have a drive letter in it for windows paths, you can say relative=True or omit the relative argument.

    # Access the original path
    print("Original Path:", FPVW.original_path)

    # Get a cleaned version of your path
    cleaned_path = FPVW.clean(path=example_path)
    print("Cleaned Path:", cleaned_path)  # Output should be "C:/Broken/path/to/file.txt"

    # Check if the original path is valid
    try:
        FPVW.validate()
        print("Path is valid!")
    except ValueError as e:
        print(f"Validation Error: {e}")

    # Auto-clean the path upon creating the validator object
    # the purpose of auto clean is to set the .path attribute to the cleaned path
    # in the init before any other checks are done.
    # this ensures that when you do any checks, it does it on the cleaned path first.
    # sort of like an auto-correct feature. 
    FPVW_Auto_Clean = FPV_Windows(example_path, auto_clean=True, relative=True)
    print("Automatically Cleaned Path:", FPVW_Auto_Clean.path)


if __name__ == "__main__":
    main()
