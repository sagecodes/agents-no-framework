from utils.decorators import tool

@tool(agent="string")
def word_count(s): """Counts number of words in a string."""; return len(s.split())

@tool(agent="string")
def letter_count(s): """Counts number of letters in a string."""; return sum(c.isalpha() for c in s)
