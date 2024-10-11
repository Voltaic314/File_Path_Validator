# example usage of the FPV module :) 
from FPV import Validator


def main():
    path = "example/path/with/invalid<>characters"
    validator = Validator(path, service_name="windows")
    
    try:
        if validator.check_if_valid():
            print("Path is valid.")
        
        cleaned_path = validator.get_cleaned_path()
        print(f"Cleaned path: {cleaned_path}")

    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
