from os import listdir, remove, mkdir
from os.path import isfile, join
import csv
import difflib

"""
Simple file I/O library 
"""

def get_files(dirname, **kw):
  def filtering(filename):
    if 'type' in kw:
      filetype = kw['type']
      if filetype[0] != '.':
        filetype = '.' + filetype
      if filename[-len(filetype):] != filetype:
        return False
    if 'phrase' in kw:
      if kw['phrase'] not in filename:
        return False
    if filename[:2] == '~$': # Microsoft Office temporary file
      return False
    return True
  files = [file for file in listdir(dirname) if isfile(join(dirname, file))]
  return list(filter(lambda x: filtering(x), files))
def get_folders(dirname, **kw):
  def filtering(filename):
    if 'type' in kw:
      filetype = kw['type']
      if filetype[0] != '.':
        filetype = '.' + filetype
      if filename[-len(filetype):] != filetype:
        return False
    if 'phrase' in kw:
      if kw['phrase'] not in filename:
        return False
    if filename[:2] == '~$': # Microsoft Office temporary file
      return False
    return True
  files = [file for file in listdir(dirname) if not isfile(join(dirname, file))]
  return list(filter(lambda x: filtering(x), files))

def read_file(filename):
  with open(filename) as file:
    return file.read()
  return ""
def write_file(filename, data):
  with open(filename, 'w', encoding='utf-8') as file:
    file.write(data)

def read_csv(csvfilename):
  rows = []
  with open(csvfilename) as csvfile:
    file_reader = csv.reader(csvfile)
    for row in file_reader:
      rows.append(row)
  return rows
def write_csv(filename, output, header=''):
  with open(filename, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    if header != '':
      header = list(header.split(','))
      csvwriter.writerow(header)
    for row in output:
      csvwriter.writerow(row)

def make_folder(path):
  try:
    mkdir(path)
  except:
    pass

def get_stuid(filename):
  return filename[:filename.index('-')].upper()

def remove_files(files):
  for file in files:
    try:
      remove('{0}'.format(file))
    except:
      pass

def str_diff(str1, str2):
  return difflib.unified_diff(str1,str2)
