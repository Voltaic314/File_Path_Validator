# example usage of the FPV module :) 
from FPV import Validator


def main():
    path = " leading_space/file.txt"
    validator = Validator(path, service_name="box")
    
    try:
        if validator.check_if_valid():
            print("Path is valid.")
        
        cleaned_path = validator.get_cleaned_path()
        print(f"Cleaned path: {cleaned_path}")

    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
