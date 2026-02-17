# Now we can use the module we just created, by using the import statement
import mymodule

mymodule.greeting("Jonathan")
a = mymodule.person1["age"]
print(a)

# What module contain
print(dir(mymodule))

# You can name the module file whatever you like, but it must have the file extension .py
# You can create an alias when you import a module, by using the as keyword
# Create an alias for mymodule called mx
import mymodule as mx

a = mx.person1["age"]
print(a) 

# Built-in modules
import platform

x = platform.system()
print(x)
x = dir(platform)
print(x)

# You can choose to import only parts from a module, by using the from keyword
from mymodule import person1

print (person1["age"])
