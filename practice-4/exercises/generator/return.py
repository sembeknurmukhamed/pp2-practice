def returning(x):
   for i in range(x, -1, -1):
      yield i

n = returning(int(input()))
for i in n: print(i, end=" ")