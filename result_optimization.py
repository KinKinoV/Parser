import hashlib

def optimization(output_file_path=input('File to save info to: '), input_file_path=input('File to get info from: ')):
  completed_lines_hash = set()

  output_file = open(output_file_path, "w")
  for line in open('results\\already_checked.txt', 'r'):
    completed_lines_hash.add(hashlib.md5(line.rstrip().encode('utf-8')).hexdigest())

  for line in open(input_file_path, "r"):
    hashValue = hashlib.md5(line.rstrip().encode('utf-8')).hexdigest()
    if hashValue not in completed_lines_hash:
      output_file.write(line)
      completed_lines_hash.add(hashValue)
  output_file.close()

optimization()