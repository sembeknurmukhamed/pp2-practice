def square(x): 
   for i in range(1, x + 1): 
      yield i ** 2

n = square(int(input()))
for i in n: print(i, end=" ")
