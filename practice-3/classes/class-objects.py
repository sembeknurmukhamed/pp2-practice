# Create a class
class MyClass:
  x = 5

# Create object
p1 = MyClass()
print(p1.x) 

# Delete Objects
del p1

# Multiple objects
p1 = MyClass()
p2 = MyClass()
p3 = MyClass()

print(p1.x)
print(p2.x)
print(p3.x) 

'''class definitions cannot be empty
   but if you for some reason have a class definition with no content
   put in the pass statement to avoid getting an error'''
