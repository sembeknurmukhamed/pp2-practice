def squares(x, y):
   for i in range(x, y + 1):
      yield i ** 2

n1, n2 = map(int, input().split())
n = squares(n1, n2)
for i in n: print(i, end=" ")
