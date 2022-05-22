def trash_commit_judge(message):
  if message.isdigit():
    return True
  elif message is None:
    return True
  elif len(message) <= 1:
    return True

  return False

def auto_commit_judge(message):
  if message.find('Merge pull request #') != -1:
    return True
  elif message.find("Merge branch '") != -1:
    return True
  
  return False

