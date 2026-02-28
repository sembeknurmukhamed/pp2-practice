from math import tan, degrees, pi

n = int(input("Input number of sides: "))
length = int(input("Input the length of a side: "))
print("The area of the polygon is:", int((n * pow(length, 2)) / 4 * int(tan(degrees(pi) / n)))) 
