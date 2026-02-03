# The 'if' statement evaluates a condition (an expression that results in True or False).
# If the condition is true, the code block inside the if statement is executed. 
# If the condition is false, the code block is skipped

# When you use 'elif', Python evaluates the conditions from top to bottom. 
# As soon as it finds a condition that is true, it executes that block and skips all remaining conditions

# The 'else' statement provides a default action when none of the previous conditions are true.
# Think of it as a "catch-all" for any scenario not covered by your if and elif statements

temperature = int(input())
if temperature > 30:
  print("It's hot outside!")
elif temperature > 20:
  print("It's warm outside")
elif temperature > 10:
  print("It's cool outside")
else:
  print("It's cold outside!")