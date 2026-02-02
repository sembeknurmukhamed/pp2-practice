# Global variables can be used by everyone, both inside of functions and outside
x = "awesome"
def myfunc():
  print("Python is " + x)
myfunc() 

# To create a global variable inside a function, you can use the 'global' keyword.
def myfunc():
  global x
  x = "fantastic"
myfunc()
print("Python is " + x) 