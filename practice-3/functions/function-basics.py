# Creating a function
def my_function():
  print("Hello from a function")

# Calling a Function
my_function()

''' A function name must start with a letter or underscore
    A function name can only contain letters, numbers, and underscores
    Function names are case-sensitive (myFunction and myfunction are different) '''

# Return values
def get_greeting():
  return "Hello from a function"
message = get_greeting()
print(message) 

def get_greeting():
  return "Hello from a function"
print(get_greeting()) 

# Function definitions cannot be empty. If you need to create a function placeholder without any code, use the 'pass' statement

# A parameter is the variable listed inside the parentheses in the function definition.
# An argument is the actual value that is sent to the function when it is called.

def my_function(name): # name is a parameter
  print("Hello", name)
my_function("Emil") # "Emil" is an argument 

# You can assign default values to parameters. If the function is called without an argument, it uses the default value
def my_function(name = "friend"):
  print("Hello", name)

my_function("Emil")
my_function("Tobias")
my_function()
my_function("Linus")

# You can send arguments with the key = value syntax
def my_function(animal, name):
  print("I have a", animal)
  print("My", animal + "'s name is", name)

my_function(animal = "dog", name = "Buddy")

# You can send any data type as an argument to a function
def my_function(fruits):
  for fruit in fruits:
    print(fruit)

my_fruits = ["apple", "banana", "cherry"]
my_function(my_fruits)

def my_function(person):
  print("Name:", person["name"])
  print("Age:", person["age"])

my_person = {"name": "Emil", "age": 25}
my_function(my_person) 

# Functions can return values using the return statement
def my_function(x, y):
  return x + y

result = my_function(5, 3)
print(result) 

# Functions can return any data type, including lists, tuples, dictionaries, and more
def my_function():
  return ["apple", "banana", "cherry"]

fruits = my_function()
print(fruits[0])
print(fruits[1])
print(fruits[2]) 

def my_function():
  return (10, 20)

x, y = my_function()
print("x:", x)
print("y:", y) 

# To specify positional-only arguments, add , / after the arguments
# To specify that a function can have only keyword arguments, add *, before the arguments
# You can combine both argument types in the same function
# Arguments before / are positional-only, and arguments after * are keyword-only
def my_function(a, b, /, *, c, d):
  return a + b + c + d

result = my_function(5, 10, c = 15, d = 20)
print(result)
