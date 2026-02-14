# Python Inheritance
''' Inheritance allows us to define a class that inherits all the methods and properties from another class.
    Parent class is the class being inherited from, also called base class.
    Child class is the class that inherits from another class, also called derived class. '''

class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname

  def printname(self):
    print(self.firstname, self.lastname)

# Use the Person class to create an object, and then execute the printname method:

x = Person("John", "Doe")
x.printname() 

class Student(Person):
  pass

y = Student("Mike", "Olsen")
y.printname()

# Add the __init__() function to the Student class
class Student(Person):
  def __init__(self, fname, lname):
    #add properties etc.
    pass

# When you add the __init__() function, the child class will no longer inherit the parent's __init__() function

# To keep the inheritance of the parent's __init__() function, add a call to the parent's __init__() function
class Student(Person):
  def __init__(self, fname, lname):
    Person.__init__(self, fname, lname)

# Python also has a super() function that will make the child class inherit all the methods and properties from its parent
class Student(Person):
  def __init__(self, fname, lname):
    super().__init__(fname, lname) 

# Add a property called graduationyear to the Student class
class Student(Person):
  def __init__(self, fname, lname):
    super().__init__(fname, lname)
    self.graduationyear = 2019

# In the example below, the year 2019 should be a variable, and passed into the Student class when creating student objects. To do so, add another parameter in the __init__() function
# Add a year parameter, and pass the correct year when creating objects
class Student(Person):
  def __init__(self, fname, lname, year):
    super().__init__(fname, lname)
    self.graduationyear = year

x = Student("Mike", "Olsen", 2019)

# Add a method called welcome to the Student class
class Student(Person):
  def __init__(self, fname, lname, year):
    super().__init__(fname, lname)
    self.graduationyear = year

  def welcome(self):
    print("Welcome", self.firstname, self.lastname, "to the class of", self.graduationyear) 

