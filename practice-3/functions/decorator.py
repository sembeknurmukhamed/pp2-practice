# By placing @changecase directly above the function definition, the function myfunction is being "decorated" with the changecase function
# The function changecase is the decorator
# The function myfunction is the function that gets decorated
# A decorator can be called multiple times. Just place the decorator above the function you want to decorate
def changecase(func):
  def myinner():
    return func().upper()
  return myinner

@changecase
def myfunction():
  return "Hello Sally"

@changecase
def otherfunction():
  return "I am speed!"

print(myfunction())
print(otherfunction())

# Functions with arguments can also be decorated:
def changecase(func):
  def myinner(x):
    return func(x).upper()
  return myinner

@changecase
def myfunction(nam):
  return "Hello " + nam

print(myfunction("John"))

# A decorator factory that takes an argument and transforms the casing based on the argument value
def changecase(n):
  def changecase(func):
    def myinner():
      if n == 1:
        a = func().lower()
      else:
        a = func().upper()
      return a
    return myinner
  return changecase

@changecase(1)
def myfunction():
  return "Hello Linus"

print(myfunction())

# You can use multiple decorators on one function
# This is done by placing the decorator calls on top of each other
# Decorators are called in the reverse order, starting with the one closest to the function
def changecase(func):
  def myinner():
    return func().upper()
  return myinner

def addgreeting(func):
  def myinner():
    return "Hello " + func() + " Have a good day!"
  return myinner

@changecase
@addgreeting
def myfunction():
  return "Tobias"

print(myfunction())

# Functions in Python has metadata that can be accessed using the __name__ and __doc__ attributes
def myfunction():
  return "Have a great day!"

print(myfunction.__name__) 

# But, when a function is decorated, the metadata of the original function is lost
# Try returning the name from a decorated function and you will not get the same result
def changecase(func):
  def myinner():
    return func().upper()
  return myinner

@changecase
def myfunction():
  return "Have a great day!"

print(myfunction.__name__)

# To fix this, Python has a built-in function called functools.wraps that can be used to preserve the original function's name and docstring
import functools

def changecase(func):
  @functools.wraps(func)
  def myinner():
    return func().upper()
  return myinner

@changecase
def myfunction():
  return "Have a great day!"

print(myfunction.__name__)
print(myfunction.__doc__)