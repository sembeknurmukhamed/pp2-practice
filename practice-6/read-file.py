f = open(r"C:\Users\tacoc\OneDrive\Рабочий стол\pp_2\practice-6\python-handling\demofile.txt")
print(f.read())

# You can also use the with statement when opening a file:
with open(r"C:\Users\tacoc\OneDrive\Рабочий стол\pp_2\practice-6\python-handling\demofile.txt") as f:
   # print(f.read())
   # By looping through the lines of the file, you can read the whole file, line by line
   for x in f:
      print(x) 
   # By default the read() method returns the whole text, but you can also specify how many characters you want to return:
   print(f.read(5))
   # By calling readline() two times, you can read the two first lines:
   print(f.readline()) 
   print(f.readline()) 

# If you are not using the with statement, you must write a close statement in order to close the file:
f.close()