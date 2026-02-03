# Arithmetic operators
x = 15
y = 4
print(x + y)
print(x - y)
print(x * y)
print(x / y)
print(x % y)
print(x ** y)
print(x // y)

# Walrus operator
numbers = [1, 2, 3, 4, 5]
if (count := len(numbers)) > 3:
   print(f"List has {count} elements")
                   
# They are same 
numbers = [1, 2, 3, 4, 5]
count = len(numbers)
if count > 3:
   print(f"List has {count} elements")

# Logical operators
x = 5
print(x > 0 and x < 10)
print(x > 0 or x > 10)
print(not(x > 0 and x < 10))

# Identity operators
x = ["apple", "banana"]
y = ["apple", "banana"]
z = x
print(x is not y)
print(x is y)
print(x is z)
print(x == y)

# Membership operators
text = "Hello World"
print("H" in text)
print("hello" in text)
print("z" not in text)

# Bitwise operators
print(5 & 3)   # 0101 & 0011 = 0001 → 1
print(5 | 3)   # 0101 | 0011 = 0111 → 7
print(5 ^ 3)   # 0101 ^ 0011 = 0110 → 6
print(5 << 1)  # 0101 → 1010 = 10
print(5 << 2)  # 0101 → 10100 = 20
print(20 >> 1) # 10100 → 01010 = 10
print(20 >> 2) # 10100 → 00101 = 5

# Precedence order
'''


() 	                                                Parentheses 	
**  	                                                Exponentiation 	
+x  -x  ~x 	                                          Unary plus, unary minus, and bitwise NOT 	
*  /  //  % 	                                       Multiplication, division, floor division, and modulus 	
+  - 	                                                Addition and subtraction 	
<<  >> 	                                             Bitwise left and right shifts 	
& 	                                                   Bitwise AND 	
^ 	                                                   Bitwise XOR 	
| 	                                                   Bitwise OR 	
==  !=  >  >=  <  <= 'is'  'is not'  'in'  'not in'  Comparisons, identity, and membership operators 	
not 	                                                Logical NOT 	
and 	                                                AND 	
or 	                                                OR 


'''