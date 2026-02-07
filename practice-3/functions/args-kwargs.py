# By default, a function must be called with the correct number of arguments
# However, sometimes you may not know how many arguments that will be passed into your function
# *args and **kwargs allow functions to accept a unknown number of arguments

# If you do not know how many arguments will be passed into your function, add a * before the parameter name.
# This way, the function will receive a tuple of arguments and can access the items accordingly
def my_function(*kids):
  print("The youngest child is " + kids[2])

my_function("Emil", "Tobias", "Linus") 

def my_function(*args):
  print("Type:", type(args)) # Tuple
  print("First argument:", args[0]) # Emil
  print("Second argument:", args[1]) # Tobias
  print("All arguments:", args) # ('Emil', 'Tobias', 'Linus')

my_function("Emil", "Tobias", "Linus")

# You can combine regular parameters with *args.
# Regular parameters must come before *args
def my_function(greeting, *names):
  for name in names:
    print(greeting, name)

my_function("Hello", "Emil", "Tobias", "Linus")

# The **kwargs parameter allows a function to accept any number of keyword arguments
# Inside the function, kwargs becomes a dictionary containing all the keyword arguments
def my_function(**myvar):
  print("Type:", type(myvar)) # Dictionary
  print("Name:", myvar["name"]) # Tobias
  print("Age:", myvar["age"]) # 30
  print("All data:", myvar) # 

my_function(name = "Tobias", age = 30, city = "Bergen")

def my_function(username, **details):
  print("Username:", username)
  print("Additional details:")
  for key, value in details.items():
    print(" ", key + ":", value)

my_function("emil123", age = 25, city = "Oslo", hobby = "coding")

''' You can use both *args and **kwargs in the same function.
The order must be:

   1. regular parameters
   2. *args
   3. **kwargs '''

def my_function(title, *args, **kwargs):
  print("Title:", title)
  print("Positional arguments:", args)
  print("Keyword arguments:", kwargs)

my_function("User Info", "Emil", "Tobias", age = 25, city = "Oslo")

# The * and ** operators can also be used when calling functions to unpack (expand) a list or dictionary into separate arguments
def my_function(a, b, c):
  return a + b + c

numbers = [1, 2, 3]
result = my_function(*numbers) # Same as: my_function(1, 2, 3)
print(result) 

def my_function(fname, lname):
  print("Hello", fname, lname)

person = {"fname": "Emil", "lname": "Refsnes"}
my_function(**person) # Same as: my_function(fname="Emil", lname="Refsnes")
