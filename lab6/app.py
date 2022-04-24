import os

def main():
    script_name = "app.py"
    command = f"pyarmor obfuscate {script_name}"
    os.system(f'cmd /c "{command}"')

if __name__ == "__main__":
    main()