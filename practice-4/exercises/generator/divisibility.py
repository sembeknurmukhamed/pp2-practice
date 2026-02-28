def divisibility(x):
   for i in range(x + 1):
      if i % 3 == 0 and i % 4 == 0:
         yield i

n = divisibility(int(input()))
for i in n: print(i, end=" ")