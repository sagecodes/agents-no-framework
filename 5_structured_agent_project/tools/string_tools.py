from utils.decorators import tool

@tool(agent="string")
def word_count(s):
    """Calculates the number of words in the given string.

    Args:
        s (str): The input string to analyze.

    Returns:
        int: The total count of words in the string.
    """
    return len(s.split())

@tool(agent="string")
def letter_count(s):
    """Calculates the number of alphabetic characters in the given string.

    Args:
        s (str): The input string to analyze.

    Returns:
        int: The total count of alphabetic characters in the string.
    """
    return sum(c.isalpha() for c in s)
