def main():   
   while True:      
      text = None
      shift = None
      file_name = input("Enter file name: ")
      with open(file_name, 'r') as file:
         text = file.read()
      print(f"File content:\n{text}")
      while True:
         try:
            shift = int(input("Enter shift: ")) % 26
         except Exception:
            print("Wrong input")
         else:
            break

      while True:
         operation = input("1. Decode\n2. Encode\n")
         if operation == "1" or operation == "2":
            break
      if operation == "1":
         result = decode(text, shift)
         print(f"Decoded text:\n{result}")
      elif operation == "2":
         result = encode(text, shift)
         print(f"Encoded text:\n{result}")

def encode(text, shift):
   result = ""
   for character in text.lower():
      if not character.isalpha():
         result += character
         continue
      new_character = ord(character) + shift
      if new_character > ord('z'):
         new_character = ord('a') + (new_character - ord('z') - 1)
      result += chr(new_character)
   return result

def decode(text, shift):
   result = ""
   for character in text:
      if not character.isalpha():
         result += character
         continue
      new_character = ord(character) - shift
      if new_character < ord('a'):
         new_character = ord('z') - (ord('a') - new_character - 1)
      result += chr(new_character)
   return result

if __name__ == "__main__":
   main()