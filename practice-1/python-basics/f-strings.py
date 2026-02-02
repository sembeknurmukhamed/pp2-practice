# Create an f-string
age = 36
txt = f"My name is John, I am {age}"
print(txt)

# A placeholder can contain variables, operations, functions, and modifiers to format the value
# A placeholder can include a modifier to format the value.
# A modifier is included by adding a colon : followed by a legal formatting type, like .2f which means fixed point number with 2 decimals
price = 59
txt = f"The price is {price:.2f} dollars"
print(txt)