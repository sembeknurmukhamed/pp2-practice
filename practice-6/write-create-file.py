# Open the file "demofile.txt" and append content to the file:
with open(r"C:\Users\tacoc\OneDrive\Рабочий стол\pp_2\practice-6\python-handling\demofile.txt", "a") as f:
   f.write("Now the file has more content!")

with open(r"C:\Users\tacoc\OneDrive\Рабочий стол\pp_2\practice-6\python-handling\demofile.txt") as f:
   print(f.read())

# Open the file "demofile.txt" and overwrite the content:
with open(r"C:\Users\tacoc\OneDrive\Рабочий стол\pp_2\practice-6\python-handling\demofile.txt", "w") as f:
  f.write("Woops! I have deleted the content!")

#open and read the file after the overwriting:
with open(r"C:\Users\tacoc\OneDrive\Рабочий стол\pp_2\practice-6\python-handling\demofile.txt") as f:
  print(f.read()) 

f = open("myfile.txt", "x")