from decimal import Decimal

"""
Print Utilities
"""
def table(head, body):
  ncol, nrow = len(head), len(body)
  
  # Find Maximum Length
  length = [0] * len(head)
  for i in range(len(head)):
    length[i] = len(head[i])
    for row in body:
      length[i] = max(length[i], len(str(row[i])))

  res = ''
  # Construct Head
  res += ' ' + ' | '.join([rpad(head[i], length[i]) for i in range(ncol)]) + ' \n'
  res += '-' + '-+-'.join(['-' * length[i] for i in range(ncol)]) + '-\n'

  # Construct Body
  for row in body:
    res += ' ' + ' | '.join([pad(row[i], length[i]) for i in range(ncol)]) + ' \n'

  # Count
  res += f'''
{nrow} row{"s" if nrow > 1 else ""}
'''
  return res

def pad(val, length):
  chk = str(val)
  if chk in '✓✗':
    return mpad(val, length)
  if chk == None:
    return rpad('NULL', length)
  if type(val) == str:
    return rpad(val, length)
  if type(val) == int:
    return lpad(val, length)
  if type(val) == Decimal:
    return lpad(val, length)
  return lpad('--', length)
def lpad(val, length):
  val = str(val)
  return (' ' * (length - len(val))) + val
def rpad(val, length):
  val = str(val)
  return val + (' ' * (length - len(val)))
def mpad(val, length):
  val = str(val)
  dif = length - len(val)
  mid = dif//2
  tmp = (' ' * mid) + val + (' ' * mid)
  if dif % 2 == 0:
    return tmp
  else:
    return tmp + ' '
