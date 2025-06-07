from utils.decorators import tool

@tool(agent="math")
def add(a, b):
    """
    Adds two numbers together.

    Args:
        a (int or float): The first number.
        b (int or float): The second number.

    Returns:
        int or float: The sum of the two numbers.
    """
    return a + b

@tool(agent="math")
def multiply(a, b):
    """
    Multiplies two numbers.

    Args:
        a (int or float): The first number.
        b (int or float): The second number.

    Returns:
        int or float: The product of the two numbers.
    """
    return a * b

@tool(agent="math")
def power(a, b):
    """
    Raises a number to the power of another number.

    Args:
        a (int or float): The base number.
        b (int or float): The exponent.

    Returns:
        int or float: The result of raising the base to the given exponent.
    """
    return a ** b
