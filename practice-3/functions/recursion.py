'''Recursion is a common mathematical and programming concept. 
   It means that a function calls itself. 
   This has the benefit of meaning that you can loop through data to reach a result'''

def countdown(n):
  if n <= 0:
    print("Done!")
  else:
    print(n)
    countdown(n - 1)

countdown(5) 

# A base case - A condition that stops the recursion
# A recursive case - The function calling itself with a modified argument
def fibonacci(n):
  if n <= 1:
    return n
  else:
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(7))



def sum_list(numbers):
  if len(numbers) == 0:
    return 0
  else:
    return numbers[0] + sum_list(numbers[1:])

my_list = [1, 2, 3, 4, 5]
print(sum_list(my_list))



def find_max(numbers):
  if len(numbers) == 1:
    return numbers[0]
  else:
    max_of_rest = find_max(numbers[1:])
    return numbers[0] if numbers[0] > max_of_rest else max_of_rest

my_list = [3, 7, 2, 9, 1]
print(find_max(my_list))

# Python has a limit on how deep recursion can go. The default limit is usually around 1000 recursive calls.
# Check the recursion limit:
import sys
print(sys.getrecursionlimit()) 

# If you need deeper recursion, you can increase the limit, but be careful as this can cause crashes
import sys
sys.setrecursionlimit(2000)
print(sys.getrecursionlimit())

# Generators are functions that can pause and resume their execution
# When a generator function is called, it returns a generator object, which is an iterator
# The code inside the function is not executed yet, it is only compiled. The function only executes when you iterate over the generator
def my_generator():
  yield 1
  yield 2
  yield 3

for value in my_generator():
  print(value) 

# When yield is encountered, the function's state is saved, and the value is returned. The next time the generator is called, it continues from where it left off
# Generator that yields numbers
def count_up_to(n):
  count = 1
  while count <= n:
    yield count
    count += 1

for num in count_up_to(5):
  print(num) 

# You can manually iterate through a generator using the next() function
# When there are no more values to yield, the generator raises a StopIteration exception
def simple_gen():
  yield "Emil"
  yield "Tobias"

gen = simple_gen()
print(next(gen))
print(next(gen))
'print(next(gen))' # This will raise StopIteration 



# Generators are memory-efficient because they generate values on-the-fly instead of storing everything in memory
# For large datasets, generators save memory
# Generator for large sequences
def large_sequence(n):
  for i in range(n):
    yield i

# This doesn't create a million numbers in memory
gen = large_sequence(1000000)
print(next(gen))
print(next(gen))
print(next(gen)) 

# Similar to list comprehensions, you can create generators using generator expressions with parentheses instead of square brackets
# List comprehension vs generator expression

# List comprehension - creates a list
list_comp = [x * x for x in range(5)]
print(list_comp)

# Generator expression - creates a generator
gen_exp = (x * x for x in range(5))
print(gen_exp)
print(list(gen_exp)) 

# Calculate sum of squares without creating a list
total = sum(x * x for x in range(10))
print(total)

# Get first 100 Fibonacci numbers
def fibonacci():
  a, b = 0, 1
  while True:
    yield a
    a, b = b, a + b

gen = fibonacci()
for _ in range(100):
  print(next(gen))

# The send() method allows you to send a value to the generator
def echo_generator():
  while True:
    received = yield
    print("Received:", received)

gen = echo_generator()
next(gen) # Prime the generator
gen.send("Hello")
gen.send("World")

# The close() method stops the generator
def my_gen():
  try:
    yield 1
    yield 2
    yield 3
  finally:
    print("Generator closed")

gen = my_gen()
print(next(gen))
gen.close() 
