# The bool() function allows you to evaluate any value, and give you True or False in return
print(bool("smtn...")) # True
print(bool(2145)) # True if every number except 0
print(bool(0)) # False
print(bool("")) # False

# Evaluate two variables
x = "Hello"
y = 15

print(bool(x))
print(bool(y))

# In fact, there are not many values that evaluate to False, 
# except empty values, such as (), [], {}, "", the number 0, and the value None. 
# And of course the value False evaluates to False.
bool(False)
bool(None)
bool(0)
bool("")
bool(())
bool([])
bool({})

# Python also has many built-in functions that return a boolean value, 
# like the isinstance() function, which can be used to determine if an object is of a certain data type
x = 200
print(isinstance(x, int))