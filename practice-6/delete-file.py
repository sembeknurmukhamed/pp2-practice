# Remove the file "demofile.txt":
import os
os.remove(r"C:\Users\tacoc\OneDrive\Рабочий стол\pp_2\practice-6\demofile.txt") 

# Check if file exists, then delete it:
if os.path.exists(r"C:\Users\tacoc\OneDrive\Рабочий стол\pp_2\practice-6\demofile.txt"):
  os.remove(r"C:\Users\tacoc\OneDrive\Рабочий стол\pp_2\practice-6\demofile.txt")
else:
  print("The file does not exist") 

# Delete a folder
# os.rmdir("myfolder") 