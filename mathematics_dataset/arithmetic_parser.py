""" Adapted from Georg Nebehay's arithmetic parser at https://github.com/gnebehay/parser
Extended to include:
- multi-digit numbers
- decimals/floating point numbers
- explicit negative numbers
- string output, including parentheses (which aren't strictly necessary in the AST)
- single step reduction
"""

import sys
import enum
import re
import operator
import random
from scipy.stats import skewnorm

START_MARKER = '\u59cb'
END_MARKER = '\u7d42'

class TokenType(enum.Enum):
  T_NUM = 0
  T_PLUS = 1
  T_MINUS = 2
  T_MULT = 3
  T_DIV = 4
  T_LPAR = 5
  T_RPAR = 6
  T_END = 7

operations = {
    TokenType.T_PLUS: operator.add,
    TokenType.T_MINUS: operator.sub,
    TokenType.T_MULT: operator.mul,
    TokenType.T_DIV: operator.truediv
}

class Node:
  def __init__(self, token_type: TokenType, value=None):
    self.token_type = token_type
    self.value = value
    self.children = []
    self.paren = False
    self.staged = False

  def to_string(self, debug=False) -> str:
    """ Converts the AST to a string representation. Enable debug for readability (spaces).
    """
    if self.token_type == TokenType.T_NUM:
      # Deal with annoying floating point precision stuff
      val = round(self.value, 12)
      if val == int(val):
        val = int(val)
      s = str(val)

    else:
      sep = ' ' if debug else ''
      left_str = self.children[0].to_string(debug)
      right_str = self.children[1].to_string(debug)
      s = left_str + sep + str(self.value) + sep + right_str

    if self.paren:
      s = '(' + s + ')'
    if self.staged:
      s = START_MARKER + s + END_MARKER

    return s

  def is_reducable(self) -> bool:
    """ Convenience function to determine whether this Node is reducable.
    """
    return self.token_type != TokenType.T_NUM

  def step(self):
    """ Reduces the expression represented by this Node by randomly selecting one of its children
    to reduce if they are reducable. Otherwise, if both children are fully reduced, computes the 
    numerical value of this Node.
    """
    if self.token_type == TokenType.T_NUM:
      return
    
    # If both children are numeric, reduce this node
    left_reducable = self.children[0].is_reducable()
    right_reducable = self.children[1].is_reducable()
    if not (left_reducable or right_reducable):
      if self.staged:
        assert(self.children[0].token_type == TokenType.T_NUM)
        assert(self.children[1].token_type == TokenType.T_NUM)

        left_val = self.children[0].value
        right_val = self.children[1].value
        operation = operations[self.token_type]

        self.token_type = TokenType.T_NUM
        self.paren = False
        self.value = operation(left_val, right_val)
        if int(self.value) == self.value:
          self.value = int(self.value)
        self.children = []
        self.staged = False
        return
      else:
        self.staged = True

    # Otherwise, pick one of the children to reduce
    child_ind = 0 if left_reducable else 1
    self.children[child_ind].step()


def lexical_analysis(s: str) -> [Node]:
  """ Converts an arithmetic string into a series of tokens, represented by AST nodes directly.
  """
  mappings = {
    '+': TokenType.T_PLUS,
    '-': TokenType.T_MINUS,
    '*': TokenType.T_MULT,
    '/': TokenType.T_DIV,
    '(': TokenType.T_LPAR,
    ')': TokenType.T_RPAR}

  tokens = []
  idx = 0
  is_prev_value = False
  while idx < len(s):
    c = s[idx]
    if (not is_prev_value and (c == '+' or c == '-')) or re.match(r'\d', c): # handle numeric
      start = idx
      if c == '+' or c == '-': # account for explicit positive/negative number
        idx += 1

      while idx < len(s) and re.fullmatch(r'(\+|-)?(\d+(\.\d*)?|\.\d+)', s[start:idx + 1]):
        idx += 1
      
      num = float(s[start:idx])
      if int(num) == float(num):
        num = int(num)
      token = Node(TokenType.T_NUM, value=num)
      is_prev_value = True

    elif c in mappings:
      token_type = mappings[c]
      token = Node(token_type, value=c)
      idx += 1
      is_prev_value = (c == ')')
    else:
      raise Exception('Invalid token: {}'.format(c))
    tokens.append(token)
  tokens.append(Node(TokenType.T_END))
  return tokens


def match(tokens: [Node], token: TokenType) -> Node:
  """ Pops the next token off the stack if it matches the given Token.
  Used primarily to match parse parentheses.
  """
  if tokens[0].token_type == token:
    return tokens.pop(0)
  else:
    raise Exception('Invalid syntax on token {}: {}, expected {}'.format(tokens[0].token_type, tokens[0].value, token))

def parse_e(tokens: [Node]) -> Node:
  """ Parses lowest priority expressions: addition, subtraction.
  """
  left_node = parse_e2(tokens)

  while tokens[0].token_type in [TokenType.T_PLUS, TokenType.T_MINUS]:
    node = tokens.pop(0)
    node.children.append(left_node)
    node.children.append(parse_e2(tokens))
    left_node = node

  return left_node


def parse_e2(tokens: [Node]) -> Node:
  """ Parses second-priority expressions: multiplication, division
  """
  left_node = parse_e3(tokens)

  while tokens[0].token_type in [TokenType.T_MULT, TokenType.T_DIV]:
    node = tokens.pop(0)
    node.children.append(left_node)
    node.children.append(parse_e3(tokens))
    left_node = node

  return left_node


def parse_e3(tokens: [Node]) -> Node:
  """ Parses highest-priority expressions: parentheses and numeric values.
  """
  if tokens[0].token_type == TokenType.T_NUM:
    return tokens.pop(0)

  match(tokens, TokenType.T_LPAR)
  expression = parse_e(tokens)
  match(tokens, TokenType.T_RPAR)

  expression.paren = True 
  return expression


def parse(inputstring: str) -> Node:
  """ Parses an arithmetic string into an abstract syntax tree.
  """
  inputstring = ''.join(inputstring.split())
  tokens = lexical_analysis(inputstring)
  ast = parse_e(tokens)
  match(tokens, TokenType.T_END)
  return ast


def sample_indices(n, size):
  while True:
    indices = skewnorm.rvs(-0.1, size=n)
    indices = set(map(lambda i: min(max(int(i * (size - 1)), 0), size - 1), indices))
    if len(indices) == n:
      return indices


# enable step corruption by setting num_intermediates to a non-negative integer
def generate_datapoints(inputstring: str, num_intermediates = -1, debug=False,
                        with_markers = False) -> [(str, str, int)]:
  """ Generates a list of (expr, next_expr, finished) tuples for a given arithmetic expression.
  """
  datapoints = []
  ast = parse(inputstring)

  while ast.is_reducable():
    curr = ast.to_string(debug)
    ast.step()
    if not with_markers:
      ast.step() # skip the staging step
    reduced = ast.to_string(debug)
    finished = not ast.is_reducable()

    datapoints.append((curr, reduced, int(finished)))

  # step corruption
  if (num_intermediates >= 0):
    num_intermediates = min(num_intermediates, len(datapoints) - 1)

    indices =  sample_indices(num_intermediates, len(datapoints[:-1]))
    # print(indices)
    intermediates = list(map(lambda i: datapoints[:-1][i], indices))
    datapoints = [datapoints[-1]] + intermediates
    # datapoints = intermediates
    # datapoints = [datapoints[-1]] + random.sample(datapoints[:-1], num_intermediates)
  
  return datapoints

if __name__ == '__main__':
  # ast = parse(inp)
  for datapoint in generate_datapoints(sys.argv[1], num_intermediates = 2, debug=True, with_markers=True):
    print(datapoint)