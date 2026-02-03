# One-line 'if' statement
a, b = 5, 2
if a > b: print("a is greater than b")

# One-line if/else that prints a value
a, b = 2, 330
print("A") if a > b else print("B")

# You can also use a one-line if/else to choose a value and assign it to a variable 
a, b = 10, 20
bigger = a if a > b else b # variable = value_if_true if condition else value_if_false
print("Bigger is", bigger)

a, b = 330, 330
print("A") if a > b else print("=") if a == b else print("B")
