def main():   
   while True:      
      text = None
      key = None
      file_name = input("Enter file name: ")
      with open(file_name, 'r') as file:
         text = file.read()
      print(f"File content:\n{text}")
      key = input("Enter key: ")
      
      while True:
         operation = input("1. Decode\n2. Encode\n")
         if operation == "1" or operation == "2":
            break
      if operation == "1":
         result = decode(text, key)
         print(f"Decoded text:\n{result}")
      elif operation == "2":
         result = encode(text, key)
         print(f"Encoded text:\n{result}")

def encode(text, key):
   result = ""
   key_values = [ord(char.lower()) - ord('a') for char in key]
   key_length = len(key)
   for index, character in enumerate(text.lower()):
      if not character.isalpha():
         result += character
         continue
      shift = key_values[index % key_length]
      new_character = ord(character) + shift
      if new_character > ord('z'):
         new_character = ord('a') + (new_character - ord('z') - 1)
      result += chr(new_character)
   return result

def decode(text, key):
   result = ""
   key_values = [ord(char.lower()) - ord('a') for char in key]
   key_length = len(key)
   for index, character in enumerate(text.lower()):
      if not character.isalpha():
         result += character
         continue
      shift = key_values[index % key_length]
      new_character = ord(character) - shift
      if new_character < ord('a'):
         new_character = ord('z') - (ord('a') - new_character - 1)
      result += chr(new_character)
   return result

if __name__ == "__main__":
   main()