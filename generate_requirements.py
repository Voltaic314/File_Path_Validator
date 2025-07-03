#!/usr/bin/env python3
"""
Script to generate a proper UTF-8 requirements.txt file
"""
import subprocess
import sys
import os

def generate_requirements(output_file='FPV/requirements.txt', encoding='utf-8'):
    """Generate requirements.txt with proper UTF-8 encoding"""
    try:
        # Run pip freeze
        result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], 
                              capture_output=True, text=True, encoding=encoding)
        
        if result.returncode == 0:
            # Write to file with UTF-8 encoding
            with open(output_file, 'w', encoding=encoding) as f:
                f.write(result.stdout)
            print(f"✅ Successfully generated {output_file} with {encoding} encoding")
            return True
        else:
            print(f"❌ Error running pip freeze: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error generating requirements: {e}")
        return False

def generate_minimal_requirements(output_file='FPV/requirements.txt'):
    """Generate minimal requirements for FPV library"""
    minimal_requirements = [
        "colorama==0.4.6",
        "exceptiongroup==1.2.2", 
        "iniconfig==2.0.0",
        "packaging==24.1",
        "pluggy==1.5.0",
        "pytest==8.3.3",
        "tomli==2.0.2",
        "typing_extensions==4.14.0"
    ]
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for req in minimal_requirements:
                f.write(req + '\n')
        print(f"✅ Successfully generated minimal {output_file} with UTF-8 encoding")
        return True
    except Exception as e:
        print(f"❌ Error generating minimal requirements: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate requirements.txt with proper encoding')
    parser.add_argument('--full', action='store_true', help='Generate full requirements from pip freeze')
    parser.add_argument('--minimal', action='store_true', help='Generate minimal requirements for FPV')
    parser.add_argument('--output', default='FPV/requirements.txt', help='Output file path')
    
    args = parser.parse_args()
    
    if args.full:
        generate_requirements(args.output)
    elif args.minimal:
        generate_minimal_requirements(args.output)
    else:
        # Default to minimal requirements
        generate_minimal_requirements(args.output) 