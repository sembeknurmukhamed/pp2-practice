# A for loop is used for iterating over a sequence (that is either a list, a tuple, a dictionary, a set, or a string)
fruits = ["apple", "banana", "cherry"]
for x in fruits:
  print(x)

# Even strings are iterable objects, they contain a sequence of characters
for x in "banana":
  print(x)

# With the break statement we can stop the loop before it has looped through all the items
fruits = ["apple", "banana", "cherry"]
for x in fruits:
  print(x)
  if x == "banana":
    break

# With the continue statement we can stop the current iteration of the loop, and continue with the next
fruits = ["apple", "banana", "cherry"]
for x in fruits:
  if x == "banana":
    continue
  print(x)

# The range() function returns a sequence of numbers, starting from 0 by default, and increments by 1 (by default), and ends at a specified number
# Syntax 
  'range(start, stop, step)'

# The else keyword in a for loop specifies a block of code to be executed when the loop is finished
for x in range(6):
  print(x)
else:
  print("Finally finished!")

# for loops cannot be empty, but if you for some reason have a for loop with no content, put in the pass statement to avoid getting an error
for x in [0, 1, 2]:
  pass

