def even(x):
   for i in range(x + 1):
      if i % 2 == 0:
         if i == x or i == x - 1:
            yield i
            break 
         yield f"{i}, "

n = even(int(input()))
for i in n: print(i, end="")