import os

def main():
    folder = input("Enter project folder name: ")
    command = f"pyarmor obfuscate {folder}/"
    os.system(f'cmd /c "{command}"')

if __name__ == "__main__":
    main()