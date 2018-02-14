def ErrOrZero(cond):
  try:
    return cond()
  except:
    return 0
