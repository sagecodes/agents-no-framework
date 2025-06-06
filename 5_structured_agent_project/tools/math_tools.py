from utils.decorators import tool

@tool(agent="math")
def add(a, b): """Adds two numbers."""; return a + b

@tool(agent="math")
def multiply(a, b): """Multiplies two numbers."""; return a * b

@tool(agent="math")
def power(a, b): """Raises a to the power of b."""; return a ** b
