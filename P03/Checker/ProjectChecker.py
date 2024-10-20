from DB import *
from Config import config
from Utilities import *
from file_io import *
from decimal import Decimal
import psycopg


'''
USER CONFIG
'''
SOLUTION = 'P03.sql'
triggers = read_file(SOLUTION)


'''
Helper to check unordered result
  - Change to set first
  - Also check length
Format:
  act = ([header], [body])
  exp = ([header], [body])
'''
def unordered(act, exp):
  if type(act) != tuple:
    return 'Error'
  if len(act[1]) != len(exp[1]):
    return 'Mismatch length'
  if set(act[1]) != set(exp[1]):
    return 'Mismatch body'
  return 'Correct'

'''
Helper to check ordered result
  - Also check length
Format:
  act = ([header], [body])
  exp = ([header], [body])
'''
def ordered(act, exp):
  if type(act) != tuple:
    return 'Error'
  if len(act[1]) != len(exp[1]):
    return 'Mismatch length'
  if act[1] != exp[1]:
    return 'Mismatch body'
  return 'Correct'

'''
Helper to check if INSERT pass/fail
'''
def insert(res, exp, cmt, tbl):
  if exp == True:
    if res == 'INSERT 0 1':
      tbl.append(('PASS', cmt))
      return 1
    else:
      tbl.append(('FAIL', cmt))
      return 0
  else:
    if res == 'INSERT 0 0' or type(res) == psycopg.errors.RaiseException:
      tbl.append(('PASS', cmt))
      return 1
    else:
      tbl.append(('FAIL', cmt))
      return 0

'''
Helper to check db_state is PASS/FAIL
'''
def check_db_state(res, cmt, tbl):
  if res == 'Correct':
    tbl.append(('PASS', cmt))
    return 1
  else:
    tbl.append(('FAIL', cmt))
    return 0


'''
Trigger #1
'''
def trigger1(sql):
  print('Trigger #1:', end=' ', flush=True)

  # Connect and reset
  db = DB(**config).reset()
  print(' ', end='', flush=True)

  # Setup the database
  db.exec("INSERT INTO Customers VALUES ('email', DATE('1970-01-01'), 'address', 80000000, 'fsname', 'lsname')")
  db.exec("INSERT INTO Locations VALUES (123456, 'lname', 'laddr')")
  db.exec("INSERT INTO Employees VALUES (100, 'ename', 90000000, 123456)")
  db.exec("INSERT INTO Drivers VALUES (100, 'pdvl')")
  db.exec("INSERT INTO CarModels VALUES ('brand', 'model', 4, 1000, 200)")
  db.exec("INSERT INTO CarDetails VALUES ('plate1', 'color', 2000, 'brand', 'model', 123456)")
  db.exec("INSERT INTO CarDetails VALUES ('plate2', 'color', 2000, 'brand', 'model', 123456)")
  db.exec("INSERT INTO Bookings VALUES (1000, DATE('2023-01-01'), 6, 'email', 'ccnum', DATE('2022-12-01'), 'brand', 'model', 123456)")
  db.exec("INSERT INTO Bookings VALUES (1001, DATE('2023-01-01'), 6, 'email', 'ccnum', DATE('2022-12-01'), 'brand', 'model', 123456)")
  db.exec("INSERT INTO Assigns VALUES (1000, 'plate1')")
  db.exec("INSERT INTO Assigns VALUES (1001, 'plate2')")
  print('░', end='', flush=True)

  # Check DB
  db_check = unordered(db.fetch("SELECT bid FROM Bookings;").res[-1], ([], [(1000,),(1001,)]))
  if db_check != 'Correct':
    print(db_check)
    return

  # Initialize Answer
  db.exec(sql)
  print('▒', end='', flush=True)

  count = 0
  tbl = []
  if db.err != 0:
    count -= 1000
  
    
  # Should pass
  db.exec("INSERT INTO Hires VALUES (1000, 100, DATE('2023-01-02'), DATE('2023-01-05'), 'ccnum')")
  count += insert(db.res[-1], True, 'Initial Hire', tbl)
  print('▓', end='', flush=True)
  
  # Should fail
  db.exec("INSERT INTO Hires VALUES (1001, 100, DATE('2023-01-01'), DATE('2023-01-02'), 'ccnum')")
  count += insert(db.res[-1], False, 'Overlap NEW.todate', tbl)
  print('▓', end='', flush=True)
  
  # Should fail
  db.exec("INSERT INTO Hires VALUES (1001, 100, DATE('2023-01-05'), DATE('2023-01-06'), 'ccnum')")
  count += insert(db.res[-1], False, 'Overlap NEW.fromdate', tbl)
  print('▓', end='', flush=True)
  
  # Should fail
  db.exec("INSERT INTO Hires VALUES (1001, 100, DATE('2023-01-01'), DATE('2023-01-06'), 'ccnum')")
  count += insert(db.res[-1], False, 'NEW Covers OLD', tbl)
  print('▓', end='', flush=True)
  
  # Should fail
  db.exec("INSERT INTO Hires VALUES (1001, 100, DATE('2023-01-03'), DATE('2023-01-04'), 'ccnum')")
  count += insert(db.res[-1], False, 'OLD Covers NEW', tbl)
  print('▓', end='', flush=True)
  
  # Should fail
  db.exec("INSERT INTO Hires VALUES (1001, 100, DATE('2023-01-02'), DATE('2023-01-03'), 'ccnum')")
  count += insert(db.res[-1], False, 'Overlap Exact', tbl)
  print('▓', end='', flush=True)
  
  # Should pass
  db.exec("INSERT INTO Hires VALUES (1001, 100, DATE('2023-01-01'), DATE('2023-01-01'), 'ccnum')")
  count += insert(db.res[-1], True, 'No Overlap', tbl)
  print('▓', end='', flush=True)

  db.close()
  print('█')
  print(table(['Check', 'Comment'], tbl))


'''
Trigger #2
'''
def trigger2(sql):
  print('Trigger #2:', end=' ', flush=True)

  # Connect and reset
  db = DB(**config).reset()
  print(' ', end='', flush=True)

  # Setup the database
  db.exec("INSERT INTO Customers VALUES ('email', DATE('1970-01-01'), 'address', 80000000, 'fsname', 'lsname')")
  db.exec("INSERT INTO Locations VALUES (123456, 'lname', 'laddr')")
  db.exec("INSERT INTO Employees VALUES (100, 'ename', 90000000, 123456)")
  db.exec("INSERT INTO Drivers VALUES (100, 'pdvl')")
  
  db.exec("INSERT INTO CarModels VALUES ('brand', 'model', 4, 1000, 200)")
  
  db.exec("INSERT INTO CarDetails VALUES ('plate1', 'color', 2000, 'brand', 'model', 123456)")
  db.exec("INSERT INTO CarDetails VALUES ('plate2', 'color', 2000, 'brand', 'model', 123456)")

  db.exec("INSERT INTO Bookings VALUES (1000, DATE('2023-01-01'), 6, 'email', 'ccnum', DATE('2022-12-01'), 'brand', 'model', 123456)")
  db.exec("INSERT INTO Bookings VALUES (1001, DATE('2023-01-01'), 6, 'email', 'ccnum', DATE('2022-12-01'), 'brand', 'model', 123456)")
  db.exec("INSERT INTO Bookings VALUES (1002, DATE('2023-01-07'), 6, 'email', 'ccnum', DATE('2022-12-01'), 'brand', 'model', 123456)")
  print('░', end='', flush=True)

  # Check DB
  db_check = unordered(db.fetch("SELECT bid FROM Bookings;").res[-1], ([], [(1000,),(1001,),(1002,)]))
  if db_check != 'Correct':
    print(db_check)
    return
  
  # Initialize Answer
  db.exec(sql)
  print('▒', end='', flush=True)

  count = 0
  tbl = []
  if db.err != 0:
    count -= 1000
  
  # Should pass
  db.exec("INSERT INTO Assigns VALUES (1000, 'plate1')")
  count += insert(db.res[-1], True, 'Initial assign', tbl)
  print('▓', end='', flush=True)
  
  # Should fail
  db.exec("INSERT INTO Assigns VALUES (1001, 'plate1')")
  count += insert(db.res[-1], False, 'Plate already assigned to another booking during the same time', tbl)
  print('▓', end='', flush=True)
  
  # Should fail
  db.exec("INSERT INTO Assigns VALUES (1000, 'plate1')")
  count += insert(db.res[-1], False, 'Plate already assigned to the same booking', tbl)  
  print('▓', end='', flush=True)
  
  # Should pass
  db.exec("INSERT INTO Assigns VALUES (1001, 'plate2')")
  count += insert(db.res[-1], True, 'Unused plate', tbl)
  print('▓', end='', flush=True)
  
  # Should pass
  db.exec("INSERT INTO Assigns VALUES (1002, 'plate1')")
  count += insert(db.res[-1], True, 'Plate assigned to another booking but with start date just after the end date', tbl)
  print('▓', end='', flush=True)

  db.close()
  print('█')
  print(table(['Check', 'Comment'], tbl))


'''
Trigger #3
'''
def trigger3(sql):
  print('Trigger #3:', end=' ', flush=True)

  # Connect and reset
  db = DB(**config).reset()
  print(' ', end='', flush=True)

  # Setup the database
  db.exec("INSERT INTO Customers VALUES ('email', DATE('1970-01-01'), 'address', 80000000, 'fsname', 'lsname')")
  db.exec("INSERT INTO Customers VALUES ('email2', DATE('1980-01-02'), 'address2', 80000001, 'fsname1', 'lsname1')")
  db.exec("INSERT INTO Customers VALUES ('email3', DATE('1980-01-02'), 'address3', 80000101, 'fsname1', 'lsname1')")

  db.exec("INSERT INTO Locations VALUES (123456, 'lname', 'laddr')")
  db.exec("INSERT INTO Locations VALUES (118203, 'lname2', 'laddr2')")
  db.exec("INSERT INTO Locations VALUES (119200, 'lname3', 'laddr3')")
    
  db.exec("INSERT INTO Employees VALUES (100, 'name1', 90000000, 123456)")
  db.exec("INSERT INTO Employees VALUES (101, 'name2', 90100000, 118203)")
  db.exec("INSERT INTO Employees VALUES (102, 'name3', 90000020, 119200)")
    
  db.exec("INSERT INTO CarModels VALUES ('brand', 'model', 4, 1000, 200)")
  
  db.exec("INSERT INTO CarDetails VALUES ('plate1', 'color', 2000, 'brand', 'model', 123456)")
  db.exec("INSERT INTO CarDetails VALUES ('plate2', 'color', 2000, 'brand', 'model', 118203)")
  db.exec("INSERT INTO CarDetails VALUES ('plate3', 'color', 2000, 'brand', 'model', 119200)")
  
  db.exec("INSERT INTO Bookings VALUES (1000, DATE('2023-01-01'), 6, 'email', 'ccnum', DATE('2022-12-01'), 'brand', 'model', 123456)")
  db.exec("INSERT INTO Bookings VALUES (1001, DATE('2023-01-01'), 6, 'email2', 'ccnum', DATE('2022-12-01'), 'brand', 'model', 118203)")
  db.exec("INSERT INTO Bookings VALUES (1002, DATE('2023-01-01'), 6, 'email3', 'ccnum',  DATE('2022-12-01'), 'brand', 'model', 119200)")

  db.exec("INSERT INTO Assigns VALUES (1000, 'plate1')")
  db.exec("INSERT INTO Assigns VALUES (1001, 'plate2')")
  db.exec("INSERT INTO Assigns VALUES (1002, 'plate3')")
  print('░', end='', flush=True)

  # Check DB
  db_check = unordered(db.fetch("SELECT bid FROM Bookings;").res[-1], ([], [(1000,),(1001,), (1002,)]))
  if db_check != 'Correct':
    print(db_check)
    return

  # Initialize Answer
  db.exec(sql)

  count = 0
  tbl = []
  if db.err != 0:
    count -= 1000
    
  # Should pass
  db.exec("INSERT INTO Handover VALUES (1000, 100)")
  count += insert(db.res[-1], True, 'Initial handover', tbl)
  print('▓', end='', flush=True)
  
  # Should fail
  db.exec("INSERT INTO Handover VALUES (1002, 101)")
  count += insert(db.res[-1], False, 'Handover with different locations', tbl)  
  print('▓', end='', flush=True)
  
  # Should fail
  db.exec("INSERT INTO Handover VALUES (1002, 100)")
  count += insert(db.res[-1], False, 'Handover with different locations', tbl)  
  print('▓', end='', flush=True)
  
  # Should pass
  db.exec("INSERT INTO Handover VALUES (1001, 101)")
  count += insert(db.res[-1], True, 'Handover with same locations', tbl)
  print('▓', end='', flush=True)

  # Should pass
  db.exec("INSERT INTO Handover VALUES (1002, 102)")
  count += insert(db.res[-1], True, 'Handover with different locations', tbl)  
  print('▓', end='', flush=True)

  db.close()
  print('█')
  print(table(['Check', 'Comment'], tbl))


'''
Trigger #4
'''
def trigger4(sql):
  print('Trigger #4:', end=' ', flush=True)

  # Connect and reset
  db = DB(**config).reset()
  print(' ', end='', flush=True)

  # Setup the database
  db.exec("INSERT INTO Customers VALUES ('email', DATE('1970-01-01'), 'address', 80000000, 'fsname', 'lsname')")
  db.exec("INSERT INTO Customers VALUES ('email2', DATE('1980-01-02'), 'address2', 80000001, 'fsname1', 'lsname1')")
  db.exec("INSERT INTO Customers VALUES ('email3', DATE('1980-01-02'), 'address3', 80000101, 'fsname1', 'lsname1')")

  db.exec("INSERT INTO Locations VALUES (123456, 'lname', 'laddr')")
  db.exec("INSERT INTO Locations VALUES (118203, 'lname2', 'laddr2')")
  db.exec("INSERT INTO Locations VALUES (119200, 'lname3', 'laddr3')")
    
  db.exec("INSERT INTO Employees VALUES (100, 'name1', 90000000, 123456)")
  db.exec("INSERT INTO Employees VALUES (101, 'name2', 90100000, 118203)")
  db.exec("INSERT INTO Employees VALUES (102, 'name3', 90000020, 119200)")
  
  db.exec("INSERT INTO CarModels VALUES ('brand', 'model', 4, 1000, 200)")
  db.exec("INSERT INTO CarModels VALUES ('brand2', 'model2', 4, 1000, 200)")
  db.exec("INSERT INTO CarModels VALUES ('brand2', 'model', 4, 1000, 200)")
  db.exec("INSERT INTO CarModels VALUES ('brand', 'model2', 4, 1000, 200)")

  db.exec("INSERT INTO CarDetails VALUES ('plate1', 'color', 2000, 'brand', 'model', 123456)")
  db.exec("INSERT INTO CarDetails VALUES ('plate2', 'color', 2000, 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO CarDetails VALUES ('plate3a', 'color', 2000, 'brand', 'model', 119200)")
  db.exec("INSERT INTO CarDetails VALUES ('plate3b', 'color', 2000, 'brand2', 'model', 119200)")
  db.exec("INSERT INTO CarDetails VALUES ('plate3c', 'color', 2000, 'brand', 'model2', 119200)")
  db.exec("INSERT INTO CarDetails VALUES ('plate3d', 'color', 2000, 'brand2', 'model2', 119200)")
  
  db.exec("INSERT INTO Bookings VALUES (1000, DATE('2023-01-01'), 6, 'email', 'ccnum', DATE('2022-12-01'), 'brand', 'model', 123456)")
  db.exec("INSERT INTO Bookings VALUES (1001, DATE('2023-01-01'), 6, 'email2', 'ccnum', DATE('2022-12-01'), 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO Bookings VALUES (1002, DATE('2023-01-01'), 6, 'email3', 'ccnum',  DATE('2022-12-01'), 'brand2', 'model2', 119200)")
  print('░', end='', flush=True)

  # Check DB
  db_check = unordered(db.fetch("SELECT bid FROM Bookings;").res[-1], ([], [(1000,),(1001,), (1002,)]))
  if db_check != 'Correct':
    print(db_check)
    return
  
  # Initialize Answer
  db.exec(sql)
  print('▒', end='', flush=True)

  count = 0
  tbl = []
  if db.err != 0:
    count -= 1000
  
  # Should pass
  db.exec("INSERT INTO Assigns VALUES (1000, 'plate1')")
  count += insert(db.res[-1], True, 'Inital assign', tbl)
  print('▓', end='', flush=True)
  
  # Should pass
  db.exec("INSERT INTO Assigns VALUES (1001, 'plate2')")
  count += insert(db.res[-1], True, 'Same brand & model', tbl)
  print('▓', end='', flush=True)
  
  # Should fail
  db.exec("INSERT INTO Assigns VALUES (1002, 'plate3a')")
  count += insert(db.res[-1], False, 'Different brand & models', tbl)
  print('▓', end='', flush=True)
  
  # Should fail
  db.exec("INSERT INTO Assigns VALUES (1002, 'plate3b')")
  count += insert(db.res[-1], False, 'Different models', tbl)
  print('▓', end='', flush=True)
  
  # Should fail
  db.exec("INSERT INTO Assigns VALUES (1002, 'plate3c')")
  count += insert(db.res[-1], False, 'Different brand', tbl)
  print('▓', end='', flush=True)
  
  # Should fail
  db.exec("INSERT INTO Assigns VALUES (1002, 'plate3d')")
  count += insert(db.res[-1], True, 'Same brand & model again', tbl)
  print('▓', end='', flush=True)

  db.close()
  print('█')
  print(table(['Check', 'Comment'], tbl))


'''
Trigger #5
'''
def trigger5(sql):
  print('Trigger #5:', end=' ', flush=True)

  # Connect and reset
  db = DB(**config).reset()
  print(' ', end='', flush=True)

  # Setup the database
  db.exec("INSERT INTO Customers VALUES ('email', DATE('1970-01-01'), 'address', 80000000, 'fsname', 'lsname')")
  db.exec("INSERT INTO Customers VALUES ('email2', DATE('1980-01-02'), 'address2', 80000001, 'fsname1', 'lsname1')")
  db.exec("INSERT INTO Customers VALUES ('email3', DATE('1980-01-02'), 'address3', 80000101, 'fsname1', 'lsname1')")

  db.exec("INSERT INTO Locations VALUES (123456, 'lname', 'laddr')")
  db.exec("INSERT INTO Locations VALUES (118203, 'lname2', 'laddr2')")
  db.exec("INSERT INTO Locations VALUES (119200, 'lname3', 'laddr3')")
    
  db.exec("INSERT INTO Employees VALUES (100, 'name1', 90000000, 123456)")
  db.exec("INSERT INTO Employees VALUES (101, 'name2', 90100000, 118203)")
  db.exec("INSERT INTO Employees VALUES (102, 'name3', 90000020, 119200)")
    
  db.exec("INSERT INTO CarModels VALUES ('brand', 'model', 4, 1000, 200)")
  db.exec("INSERT INTO CarModels VALUES ('brand2', 'model2', 4, 1000, 200)")

  db.exec("INSERT INTO CarDetails VALUES ('plate1', 'color', 2000, 'brand', 'model', 123456)")
  db.exec("INSERT INTO CarDetails VALUES ('plate2', 'color', 2000, 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO CarDetails VALUES ('plate3', 'color', 2000, 'brand', 'model', 119200)")
  
  db.exec("INSERT INTO Bookings VALUES (1000, DATE('2023-01-01'), 6, 'email', 'ccnum', DATE('2022-12-01'), 'brand', 'model', 123456)")
  db.exec("INSERT INTO Bookings VALUES (1001, DATE('2023-01-01'), 6, 'email2', 'ccnum', DATE('2022-12-01'), 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO Bookings VALUES (1002, DATE('2023-01-01'), 6, 'email3', 'ccnum',  DATE('2022-12-01'), 'brand2', 'model2', 119200)")
  print('░', end='', flush=True)

  # Check DB
  db_check = unordered(db.fetch("SELECT bid FROM Bookings;").res[-1], ([], [(1000,),(1001,), (1002,)]))
  if db_check != 'Correct':
    print(db_check)
    return

  # Initialize Answer
  db.exec(sql)
  print('▒', end='', flush=True)

  count = 0
  tbl = []
  if db.err != 0:
    count -= 1000
  
  # Should pass
  db.exec("INSERT INTO Assigns VALUES (1000, 'plate1')")
  count += insert(db.res[-1], True, 'Same model and in same location', tbl)
  print('▓', end='', flush=True)
  
  # Should fail
  db.exec("INSERT INTO Assigns VALUES (1002, 'plate2')")
  count += insert(db.res[-1], False, 'Same model but in different location', tbl)
  print('▓', end='', flush=True)
  
  # Should pass
  db.exec("INSERT INTO Assigns VALUES (1001, 'plate2')")
  count += insert(db.res[-1], True, 'Same model and in same location', tbl)  
  print('▓', end='', flush=True)

  db.close()
  print('█')
  print(table(['Check', 'Comment'], tbl))


'''
Trigger #6
'''
def trigger6(sql):
  print('Trigger #6:', end=' ', flush=True)

  # Connect and reset
  db = DB(**config).reset()
  print(' ', end='', flush=True)

  # Setup the database
  db.exec("INSERT INTO Customers VALUES ('email', DATE('1970-01-01'), 'address', 80000000, 'fsname', 'lsname')")
  db.exec("INSERT INTO Customers VALUES ('email2', DATE('1980-01-02'), 'address2', 80000001, 'fsname1', 'lsname1')")
  db.exec("INSERT INTO Customers VALUES ('email3', DATE('1980-01-02'), 'address3', 80000101, 'fsname1', 'lsname1')")

  db.exec("INSERT INTO Locations VALUES (123456, 'lname', 'laddr')")
  db.exec("INSERT INTO Locations VALUES (118203, 'lname2', 'laddr2')")
  db.exec("INSERT INTO Locations VALUES (119200, 'lname3', 'laddr3')")
    
  db.exec("INSERT INTO Employees VALUES (100, 'name1', 90000000, 123456)")
  db.exec("INSERT INTO Employees VALUES (101, 'name2', 90100000, 118203)")
  db.exec("INSERT INTO Employees VALUES (102, 'name3', 90000020, 119200)")
  db.exec("INSERT INTO Employees VALUES (103, 'name4', 90000020, 119200)")
  
  db.exec("INSERT INTO Drivers VALUES (100, 'pdvl')")
  db.exec("INSERT INTO Drivers VALUES (101, 'pdvl1')")
  db.exec("INSERT INTO Drivers VALUES (102, 'pdvl2')")
  db.exec("INSERT INTO Drivers VALUES (103, 'pdvl3')")

  db.exec("INSERT INTO CarModels VALUES ('brand', 'model', 4, 1000, 200)")
  db.exec("INSERT INTO CarModels VALUES ('brand2', 'model2', 4, 1000, 200)")

  db.exec("INSERT INTO CarDetails VALUES ('plate1', 'color', 2000, 'brand', 'model', 123456)")
  db.exec("INSERT INTO CarDetails VALUES ('plate2', 'color', 2000, 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO CarDetails VALUES ('plate3', 'color', 2000, 'brand2', 'model2', 119200)")
  db.exec("INSERT INTO CarDetails VALUES ('plate4', 'color', 2000, 'brand', 'model', 119200)")
  
  db.exec("INSERT INTO Bookings VALUES (1000, DATE('2023-01-01'), 6, 'email', 'ccnum', DATE('2022-12-01'), 'brand', 'model', 123456)")
  db.exec("INSERT INTO Bookings VALUES (1001, DATE('2023-01-01'), 6, 'email2', 'ccnum', DATE('2022-12-01'), 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO Bookings VALUES (1002, DATE('2023-01-01'), 6, 'email3', 'ccnum',  DATE('2022-12-01'), 'brand2', 'model2', 119200)")
  db.exec("INSERT INTO Bookings VALUES (1003, DATE('2023-01-01'), 6, 'email3', 'ccnum',  DATE('2022-12-01'), 'brand', 'model', 119200)")

  db.exec("INSERT INTO Assigns VALUES (1000, 'plate1')")
  db.exec("INSERT INTO Assigns VALUES (1001, 'plate2')")
  db.exec("INSERT INTO Assigns VALUES (1002, 'plate3')")
  db.exec("INSERT INTO Assigns VALUES (1003, 'plate4')")
  print('░', end='', flush=True)

  # Check DB
  db_check = unordered(db.fetch("SELECT bid FROM Bookings;").res[-1], ([], [(1000,),(1001,), (1002,), (1003,)]))
  if db_check != 'Correct':
    print(db_check)
    return
  
  # Initialize Answer
  db.exec(sql)
  print('▒', end='', flush=True)

  count = 0
  tbl = []
  if db.err != 0:
    count -= 1000
    
  # Should pass
  db.exec("INSERT INTO Hires VALUES (1000, 100, DATE('2023-01-01'), DATE('2023-01-06'), 'ccnum')")
  count += insert(db.res[-1], True, 'Hired for the entire booking duration', tbl)
  print('▓', end='', flush=True)
  
  # Should pass
  db.exec("INSERT INTO Hires VALUES (1001, 101, DATE('2023-01-02'), DATE('2023-01-02'), 'ccnum')")
  count += insert(db.res[-1], True, 'Hired for only the first day of the booking duration', tbl)
  print('▓', end='', flush=True)
  
  # Should pass
  db.exec("INSERT INTO Hires VALUES (1003, 103, DATE('2023-01-06'), DATE('2023-01-06'), 'ccnum')")
  count += insert(db.res[-1], True, 'Hired for only the end day of the booking duration', tbl)
  print('▓', end='', flush=True)
  
  # Should fail
  db.exec("INSERT INTO Hires VALUES (1002, 102, DATE('2022-01-01'), DATE('2023-01-02'), 'ccnum')")
  count += insert(db.res[-1], False, 'Start hire is before the booking start date', tbl)  
  print('▓', end='', flush=True)

  # Should fail
  db.exec("INSERT INTO Hires VALUES (1002, 102, DATE('2023-01-01'), DATE('2023-01-10'), 'ccnum')")
  count += insert(db.res[-1], False, 'End hire is after the booking end date', tbl)  
  print('▓', end='', flush=True)

  # Should fail
  db.exec("INSERT INTO Hires VALUES (1002, 102, DATE('2022-12-31'), DATE('2023-01-10'), 'ccnum')")
  count += insert(db.res[-1], False, 'Start hire is before the booking start date and End hire is after the booking end date', tbl)  
  print('▓', end='', flush=True)

  # Should pass
  db.exec("INSERT INTO Hires VALUES (1002, 102, DATE('2023-01-02'), DATE('2023-01-05'), 'ccnum')")
  count += insert(db.res[-1], True, 'Hired in between start and end dates of booking', tbl)  
  print('▓', end='', flush=True)

  db.close()
  print('█')
  print(table(['Check', 'Comment'], tbl))


'''
Procedure #1
'''
def procedure1(sql):
  print('Procedure #1:', end=' ', flush=True)

  # Connect and reset
  db = DB(**config).reset()
  print(' ', end='', flush=True)

  # Setup the database
  db.exec("INSERT INTO Locations VALUES (123456, 'lname', 'laddr')")
  db.exec("INSERT INTO Locations VALUES (123457, 'lname1', 'laddr1')")
  db.exec("INSERT INTO Locations VALUES (123458, 'lname2', 'laddr2')")
  print('░', end='', flush=True)

  # Check DB
  db_check = unordered(db.fetch("SELECT zip FROM Locations;").res[-1], ([], [(123456,),(123457,), (123458,)]))
  if db_check != 'Correct':
    print(db_check)
    return

  # Initialize Answer
  db.exec(sql)
  print('▒', end='', flush=True)

  count = 0
  tbl = []
  if db.err != 0:
    count -= 1000
    
  invalid_eids = [100, None, 102, 103]
  invalid_enames = ['name0', 'name1', None, 'name3']
  invalid_ephones = [82932929, 999999999, 82936929, 84932929]
  invalid_zips = [123456, 123459, 123458]
  invalid_zips_contains_null = [123456, 123459, None]
  invalid_pdvls = [None, 'driver1', 'driver1', None]
    
  valid_eids = [100, 101, 102, 103]
  valid_enames = ['name0', 'name1', 'name2', 'name3']
  valid_ephones = [82932929, 82932329, None, 84932929]
  valid_zips = [123456, 123457, 123458, 123457]
  valid_pdvls = [None, 'driver1', 'driver2', None]
  
  # Should not change db 
  db.exec("CALL add_employees(%s, %s, %s, %s, %s)", invalid_eids, valid_enames, valid_ephones, valid_zips, valid_pdvls)
  db_check_invalid = unordered(db.fetch("SELECT eid FROM Employees;").res[-1], ([], []))
  count += check_db_state(db_check_invalid, 'Invalid eids', tbl)
  print('▓', end='', flush=True)
    
  # Should not change db 
  db.exec("CALL add_employees(%s, %s, %s, %s, %s)", valid_eids, invalid_enames, valid_ephones, valid_zips, valid_pdvls)
  db_check_invalid1 = unordered(db.fetch("SELECT eid FROM Employees;").res[-1], ([], []))
  count += check_db_state(db_check_invalid1, 'Invalid enames', tbl)
  print('▓', end='', flush=True)

  # Should not change db 
  db.exec("CALL add_employees(%s, %s, %s, %s, %s)", valid_eids, valid_enames, invalid_ephones, valid_zips, valid_pdvls)
  db_check_invalid2 = unordered(db.fetch("SELECT eid FROM Employees;").res[-1], ([], []))
  count += check_db_state(db_check_invalid2, 'Invalid ephones', tbl)
  print('▓', end='', flush=True)

  # Should not change db 
  db.exec("CALL add_employees(%s, %s, %s, %s, %s)", valid_eids, valid_enames, valid_ephones, invalid_zips, valid_pdvls)
  db_check_invalid3 = unordered(db.fetch("SELECT eid FROM Employees;").res[-1], ([], []))
  count += check_db_state(db_check_invalid3, 'Invalid zips', tbl)
  print('▓', end='', flush=True)

  # Should not change db 
  db.exec("CALL add_employees(%s, %s, %s, %s, %s)", valid_eids, valid_enames, valid_ephones, invalid_zips_contains_null, valid_pdvls)
  db_check_invalid4 = unordered(db.fetch("SELECT eid FROM Employees;").res[-1], ([], []))
  count += check_db_state(db_check_invalid4, 'Invalid zips containing Null', tbl)
  print('▓', end='', flush=True)

  # Should not change db 
  db.exec("CALL add_employees(%s, %s, %s, %s, %s)", valid_eids, valid_enames, valid_ephones, valid_zips, invalid_pdvls)
  db_check_invalid5 = unordered(db.fetch("SELECT eid FROM Employees;").res[-1], ([], []))
  count += check_db_state(db_check_invalid5, 'Invalid pdvls', tbl)
  print('▓', end='', flush=True)

  # Should not change db 
  db.exec("CALL add_employees(%s, %s, %s, %s, %s)", invalid_eids, invalid_enames, invalid_ephones, invalid_zips, invalid_pdvls)
  db_check_invalid6 = unordered(db.fetch("SELECT eid FROM Employees;").res[-1], ([], []))
  count += check_db_state(db_check_invalid6, 'All inputs are invalid', tbl)
  print('▓', end='', flush=True)
  
  # Should change db 
  db.exec("CALL add_employees(%s, %s, %s, %s, %s)", valid_eids, valid_enames, valid_ephones, valid_zips, valid_pdvls)
  db_check_valid = unordered(db.fetch("SELECT eid FROM Employees;").res[-1], ([], [(100,),(101,), (102,), (103,)]))
  count += check_db_state(db_check_valid, 'All inputs are valid', tbl)
  print('▓', end='', flush=True)

  db.close()
  print('█')
  print(table(['Check', 'Comment'], tbl))


'''
Procedure #2
'''
def procedure2(sql):
  print('Procedure #2:', end=' ', flush=True)

  # Connect and reset
  db = DB(**config).reset()
  print(' ', end='', flush=True)

  # Setup the database
  db.exec("INSERT INTO Locations VALUES (123456, 'lname', 'laddr')")
  db.exec("INSERT INTO Locations VALUES (123457, 'lname1', 'laddr1')")
  db.exec("INSERT INTO Locations VALUES (123458, 'lname2', 'laddr2')")
  print('░', end='', flush=True)

  # Check DB
  db_check = unordered(db.fetch("SELECT zip FROM Locations;").res[-1], ([], [(123456,),(123457,), (123458,)]))
  if db_check != 'Correct':
    print(db_check)
    return

  # Initialize Answer
  db.exec(sql)
  print('▒', end='', flush=True)

  count = 0
  tbl = []
  if db.err != 0:
    count -= 1000

  valid_brand = 'brand1'
  valid_model = 'model1'
  valid_capacity = 5
  valid_deposit = 100
  valid_daily = 50
  valid_plates = ['plate1', 'plate2']
  valid_colors = ['red', 'blue']
  valid_pyears = [1920, 2000]
  valid_zips = [123456, 123457]
  
  invalid_plates_duplicate = ['plate1', 'plate1']
  invalid_plates_null = ['plate1', None]
  invalid_colors = ['red', None]
  invalid_pyears = [1920, 1900]
  invalid_zips = [123490, 123457]
  
  # Should not change db 
  db.exec("CALL add_car(%s, %s, %s, %s, %s, %s, %s, %s, %s)", None, valid_model, valid_capacity, valid_deposit, valid_daily, valid_plates, valid_colors, valid_pyears, valid_zips)
  db_check_invalid_models = unordered(db.fetch("SELECT brand FROM CarModels;").res[-1], ([], []))
  db_check_invalid_details = unordered(db.fetch("SELECT plate FROM CarDetails C where C.brand = 'brand1';").res[-1], ([], []))
  db_check_invalid = 'Correct'
  if (db_check_invalid_models != 'Correct' or db_check_invalid_details != 'Correct'):
    db_check_invalid = 'Incorrect'
  count += check_db_state(db_check_invalid, 'Brand is NULL', tbl)
  print('▓', end='', flush=True)
  
  # Should not change db 
  db.exec("CALL add_car(%s, %s, %s, %s, %s, %s, %s, %s, %s)", valid_brand, None, valid_capacity, valid_deposit, valid_daily, valid_plates, valid_colors, valid_pyears, valid_zips)
  db_check_invalid_models_1 = unordered(db.fetch("SELECT brand FROM CarModels;").res[-1], ([], []))
  db_check_invalid_details_1 = unordered(db.fetch("SELECT plate FROM CarDetails C where C.brand = 'brand1';").res[-1], ([], []))
  db_check_invalid_1 = 'Correct'
  if (db_check_invalid_models_1 != 'Correct' or db_check_invalid_details_1 != 'Correct'):
    db_check_invalid_1 = 'Incorrect'
  count += check_db_state(db_check_invalid_1, 'Model is NULL', tbl)
  print('▓', end='', flush=True)
  
  # Should not change db 
  db.exec("CALL add_car(%s, %s, %s, %s, %s, %s, %s, %s, %s)", valid_brand, valid_model, -1, valid_deposit, valid_daily, valid_plates, valid_colors, valid_pyears, valid_zips)
  db_check_invalid_models_2 = unordered(db.fetch("SELECT brand FROM CarModels;").res[-1], ([], []))
  db_check_invalid_details_2 = unordered(db.fetch("SELECT plate FROM CarDetails C where C.brand = 'brand1';").res[-1], ([], []))
  db_check_invalid_2 = 'Correct'
  if (db_check_invalid_models_2 != 'Correct' or db_check_invalid_details_2 != 'Correct'):
    db_check_invalid_2 = 'Incorrect'
  count += check_db_state(db_check_invalid_2, 'Capacity is negative', tbl)
  print('▓', end='', flush=True)
  
  # Should not change db 
  db.exec("CALL add_car(%s, %s, %s, %s, %s, %s, %s, %s, %s)", valid_brand, valid_model, valid_capacity, -1, valid_daily, valid_plates, valid_colors, valid_pyears, valid_zips)
  db_check_invalid_models_3 = unordered(db.fetch("SELECT brand FROM CarModels;").res[-1], ([], []))
  db_check_invalid_details_3 = unordered(db.fetch("SELECT plate FROM CarDetails C where C.brand = 'brand1';").res[-1], ([], []))
  db_check_invalid_3 = 'Correct'
  if (db_check_invalid_models_3 != 'Correct' or db_check_invalid_details_3 != 'Correct'):
    db_check_invalid_3 = 'Incorrect'
  count += check_db_state(db_check_invalid_3, 'Deposit is negative', tbl)
  print('▓', end='', flush=True)
  
  # Should not change db 
  db.exec("CALL add_car(%s, %s, %s, %s, %s, %s, %s, %s, %s)", valid_brand, valid_model, valid_capacity, valid_deposit, -1, valid_plates, valid_colors, valid_pyears, valid_zips)
  db_check_invalid_models_4 = unordered(db.fetch("SELECT brand FROM CarModels;").res[-1], ([], []))
  db_check_invalid_details_4 = unordered(db.fetch("SELECT plate FROM CarDetails C where C.brand = 'brand1';").res[-1], ([], []))
  db_check_invalid_4 = 'Correct'
  if (db_check_invalid_models_4 != 'Correct' or db_check_invalid_details_4 != 'Correct'):
    db_check_invalid_4 = 'Incorrect'
  count += check_db_state(db_check_invalid_4, 'Daily is negative', tbl)
  print('▓', end='', flush=True)
  
  # Should not change db 
  db.exec("CALL add_car(%s, %s, %s, %s, %s, %s, %s, %s, %s)", valid_brand, valid_model, valid_capacity, valid_deposit, valid_daily, invalid_plates_duplicate, valid_colors, valid_pyears, valid_zips)
  db_check_invalid_models_5 = unordered(db.fetch("SELECT brand FROM CarModels;").res[-1], ([], []))
  db_check_invalid_details_5 = unordered(db.fetch("SELECT plate FROM CarDetails C where C.brand = 'brand1';").res[-1], ([], []))
  db_check_invalid_5 = 'Correct'
  if (db_check_invalid_models_5 != 'Correct' or db_check_invalid_details_5 != 'Correct'):
    db_check_invalid_5 = 'Incorrect'
  count += check_db_state(db_check_invalid_5, 'Duplicate plates', tbl)
  print('▓', end='', flush=True)
  
  # Should not change db 
  db.exec("CALL add_car(%s, %s, %s, %s, %s, %s, %s, %s, %s)", valid_brand, valid_model, valid_capacity, valid_deposit, valid_daily, invalid_plates_null, valid_colors, valid_pyears, valid_zips)
  db_check_invalid_models_6 = unordered(db.fetch("SELECT brand FROM CarModels;").res[-1], ([], []))
  db_check_invalid_details_6 = unordered(db.fetch("SELECT plate FROM CarDetails C where C.brand = 'brand1';").res[-1], ([], []))
  db_check_invalid_6 = 'Correct'
  if (db_check_invalid_models_6 != 'Correct' or db_check_invalid_details_6 != 'Correct'):
    db_check_invalid_6 = 'Incorrect'
  count += check_db_state(db_check_invalid_6, 'Plates contain NULL', tbl)
  print('▓', end='', flush=True)
  
  # Should not change db 
  db.exec("CALL add_car(%s, %s, %s, %s, %s, %s, %s, %s, %s)", valid_brand, valid_model, valid_capacity, valid_deposit, valid_daily, valid_plates, invalid_colors, valid_pyears, valid_zips)
  db_check_invalid_models_7 = unordered(db.fetch("SELECT brand FROM CarModels;").res[-1], ([], []))
  db_check_invalid_details_7 = unordered(db.fetch("SELECT plate FROM CarDetails C where C.brand = 'brand1';").res[-1], ([], []))
  db_check_invalid_7 = 'Correct'
  if (db_check_invalid_models_7 != 'Correct' or db_check_invalid_details_7 != 'Correct'):
    db_check_invalid_7 = 'Incorrect'
  count += check_db_state(db_check_invalid_7, 'Color array is invalid', tbl)
  print('▓', end='', flush=True)
  
  # Should not change db 
  db.exec("CALL add_car(%s, %s, %s, %s, %s, %s, %s, %s, %s)", valid_brand, valid_model, valid_capacity, valid_deposit, valid_daily, valid_plates, valid_colors, invalid_pyears, valid_zips)
  db_check_invalid_models_8 = unordered(db.fetch("SELECT brand FROM CarModels;").res[-1], ([], []))
  db_check_invalid_details_8 = unordered(db.fetch("SELECT plate FROM CarDetails C where C.brand = 'brand1';").res[-1], ([], []))
  db_check_invalid_8 = 'Correct'
  if (db_check_invalid_models_8 != 'Correct' or db_check_invalid_details_8 != 'Correct'):
    db_check_invalid_8 = 'Incorrect'
  count += check_db_state(db_check_invalid_8, 'Pyears array is invalid', tbl)
  print('▓', end='', flush=True)
  
  # Should not change db 
  db.exec("CALL add_car(%s, %s, %s, %s, %s, %s, %s, %s, %s)", valid_brand, valid_model, valid_capacity, valid_deposit, valid_daily, valid_plates, valid_colors, valid_pyears, invalid_zips)
  db_check_invalid_models_9 = unordered(db.fetch("SELECT brand FROM CarModels;").res[-1], ([], []))
  db_check_invalid_details_9 = unordered(db.fetch("SELECT plate FROM CarDetails C where C.brand = 'brand1';").res[-1], ([], []))
  db_check_invalid_9 = 'Correct'
  if (db_check_invalid_models_9 != 'Correct' or db_check_invalid_details_9 != 'Correct'):
    db_check_invalid_9 = 'Incorrect'
  count += check_db_state(db_check_invalid_9, 'Zip array is invalid', tbl)
  print('▓', end='', flush=True)
  
  # Should change db 
  db.exec("CALL add_car(%s, %s, %s, %s, %s, %s, %s, %s, %s)", valid_brand, valid_model, valid_capacity, valid_deposit, valid_daily, valid_plates, valid_colors, valid_pyears, valid_zips)
  db_check_valid_models = unordered(db.fetch("SELECT brand FROM CarModels;").res[-1], ([], [('brand1', )]))
  db_check_valid_details = unordered(db.fetch("SELECT plate FROM CarDetails C where C.brand = 'brand1';").res[-1], ([], [('plate1',), ('plate2',)]))
  db_check_valid = 'Correct'
  if (db_check_valid_models != 'Correct' or db_check_valid_details != 'Correct'):
    db_check_valid = 'Incorrect'
  count += check_db_state(db_check_valid, 'All fields are valid', tbl)
  print('▓', end='', flush=True)
  
  # Should change db 
  db.exec("CALL add_car(%s, %s, %s, %s, %s, %s, %s, %s, %s)", 'brand2', 'model2', valid_capacity, valid_deposit, valid_daily, [], [], [], [])
  db_check_valid_models_2 = unordered(db.fetch("SELECT brand FROM CarModels C where C.brand = 'brand2';").res[-1], ([], [('brand2', )]))
  db_check_valid_details_2 = unordered(db.fetch("SELECT plate FROM CarDetails C where C.brand = 'brand2';").res[-1], ([], []))
  db_check_valid_2 = 'Correct'
  if (db_check_valid_models_2 != 'Correct' or db_check_valid_details_2 != 'Correct'):
    db_check_valid_2 = 'Incorrect'
  count += check_db_state(db_check_valid_2, 'All fields are valid (no car details)', tbl)
  print('▓', end='', flush=True)

  db.close()
  print('█')
  print(table(['Check', 'Comment'], tbl))


'''
Procedure #3
'''
def procedure3(sql):
  print('Procedure #3:', end=' ', flush=True)

  # Connect and reset
  db = DB(**config).reset()
  print(' ', end='', flush=True)

  # Setup the database
  db.exec("INSERT INTO Customers VALUES ('email', DATE('1970-01-01'), 'address', 80000000, 'fsname', 'lsname')")
  db.exec("INSERT INTO Customers VALUES ('email2', DATE('1980-01-02'), 'address2', 80000001, 'fsname1', 'lsname1')")
  db.exec("INSERT INTO Customers VALUES ('email3', DATE('1980-01-02'), 'address3', 80000101, 'fsname1', 'lsname1')")

  db.exec("INSERT INTO Locations VALUES (123456, 'lname', 'laddr')")
  db.exec("INSERT INTO Locations VALUES (118203, 'lname2', 'laddr2')")
  db.exec("INSERT INTO Locations VALUES (119200, 'lname3', 'laddr3')")
    
  db.exec("INSERT INTO Employees VALUES (100, 'name1', 90000000, 123456)")
  db.exec("INSERT INTO Employees VALUES (101, 'name2', 90100000, 118203)")
  db.exec("INSERT INTO Employees VALUES (102, 'name3', 90000020, 119200)")
  db.exec("INSERT INTO Employees VALUES (103, 'name4', 90000020, 119200)")
  
  db.exec("INSERT INTO Drivers VALUES (100, 'pdvl')")
  db.exec("INSERT INTO Drivers VALUES (101, 'pdvl1')")
  db.exec("INSERT INTO Drivers VALUES (102, 'pdvl2')")
  db.exec("INSERT INTO Drivers VALUES (103, 'pdvl3')")
  
  db.exec("INSERT INTO CarModels VALUES ('brand', 'model', 4, 1000, 200)")
  db.exec("INSERT INTO CarModels VALUES ('brand2', 'model2', 4, 1000, 200)")

  db.exec("INSERT INTO CarDetails VALUES ('plate1', 'color', 2000, 'brand', 'model', 123456)")
  db.exec("INSERT INTO CarDetails VALUES ('plate2', 'color', 2000, 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO CarDetails VALUES ('plate3', 'color', 2000, 'brand2', 'model2', 119200)")
  
  db.exec("INSERT INTO Bookings VALUES (1000, DATE('2023-01-01'), 6, 'email', 'ccnum', DATE('2022-12-01'), 'brand', 'model', 123456)")
  db.exec("INSERT INTO Bookings VALUES (1001, DATE('2023-01-01'), 6, 'email2', 'ccnum', DATE('2022-12-01'), 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO Bookings VALUES (1002, DATE('2023-01-01'), 2, 'email3', 'ccnum2',  DATE('2022-12-01'), 'brand2', 'model2', 119200)")

  db.exec("INSERT INTO Assigns VALUES (1000, 'plate1')")
  db.exec("INSERT INTO Assigns VALUES (1001, 'plate2')")
  db.exec("INSERT INTO Assigns VALUES (1002, 'plate3')")

  db.exec("INSERT INTO Handover VALUES (1000, 100)")
  db.exec("INSERT INTO Handover VALUES (1001, 101)")
  db.exec("INSERT INTO Handover VALUES (1002, 102)")
  print('░', end='', flush=True)

  # Check DB
  db_check = unordered(db.fetch("SELECT bid FROM Bookings;").res[-1], ([], [(1000,),(1001,), (1002,)]))
  if db_check != 'Correct':
    print(db_check)
    return

  # Initialize Answer
  db.exec(sql)
  print('▒', end='', flush=True)

  count = 0
  tbl = []
  if db.err != 0:
    count -= 1000
  
  # Should not change db 
  before_call_1 = db.fetch("SELECT bid FROM Returned;")
  db.exec("CALL return_car(%s, %s)", None, None)
  db_check_invalid_null = unordered(db.fetch("SELECT bid FROM Returned;").res[-1], before_call_1.res[-1])
  count += check_db_state(db_check_invalid_null, 'bid and eid is null', tbl)
  print('▓', end='', flush=True)
  
  # Should not change db 
  before_call_2 = db.fetch("SELECT bid FROM Returned;")
  db.exec("CALL return_car(%s, %s)", None, 100)
  db_check_invalid_null_bid = unordered(db.fetch("SELECT bid FROM Returned;").res[-1], before_call_2.res[-1])
  count += check_db_state(db_check_invalid_null_bid, 'only bid is null', tbl)
  print('▓', end='', flush=True)
  
  # Should not change db 
  before_call_3 = db.fetch("SELECT bid FROM Returned;")
  db.exec("CALL return_car(%s, %s)", 1005, 100)
  db_check_invalid_bid = unordered(db.fetch("SELECT bid FROM Returned;").res[-1], before_call_3.res[-1])
  count += check_db_state(db_check_invalid_bid, 'bid does not exist', tbl)
  print('▓', end='', flush=True)

  # Should not change db 
  before_call_4 = db.fetch("SELECT bid FROM Returned;")
  db.exec("CALL return_car(%s, %s)", 1001, None)
  db_check_invalid_null_eid = unordered(db.fetch("SELECT bid FROM Returned;").res[-1], before_call_4.res[-1])
  count += check_db_state(db_check_invalid_null_eid, 'only eid is null', tbl)
  print('▓', end='', flush=True)
  
  # Should not change db 
  before_call_5 = db.fetch("SELECT bid FROM Returned;")
  db.exec("CALL return_car(%s, %s)", 1001, 200)
  db_check_invalid_eid = unordered(db.fetch("SELECT bid FROM Returned;").res[-1], before_call_5.res[-1])
  count += check_db_state(db_check_invalid_eid, 'eid does not exist', tbl)
  print('▓', end='', flush=True)
  
  # Should change db 
  db.exec("CALL return_car(%s, %s)", 1001, 100)
  db_check_valid_1 = unordered(db.fetch("SELECT * FROM Returned WHERE bid = 1001;").res[-1], ([], [(1001, 100, 'ccnum', 200)]))
  count += check_db_state(db_check_valid_1, 'bid and eid exists', tbl)
  print('▓', end='', flush=True)
  
  # Should change db 
  db.exec("CALL return_car(%s, %s)", 1002, 101)
  db_check_valid_2 = unordered(db.fetch("SELECT * FROM Returned WHERE bid = 1002;").res[-1], ([], [(1002, 101, 'ccnum2', -600)]))
  count += check_db_state(db_check_valid_2, 'bid and eid exists', tbl)
  print('▓', end='', flush=True)

  db.close()
  print('█')
  print(table(['Check', 'Comment'], tbl))


'''
Procedure #4
'''
def procedure4(sql):
  print('Procedure #4:', end=' ', flush=True)

  # Connect and reset
  db = DB(**config).reset()
  print(' ', end='', flush=True)

  # Setup the database
  db.exec("INSERT INTO Customers VALUES ('email', DATE('1970-01-01'), 'address', 80000000, 'fsname', 'lsname')")
  db.exec("INSERT INTO Customers VALUES ('email2', DATE('1980-01-02'), 'address2', 80000001, 'fsname1', 'lsname1')")
  db.exec("INSERT INTO Customers VALUES ('email3', DATE('1980-01-02'), 'address3', 80000101, 'fsname1', 'lsname1')")

  db.exec("INSERT INTO Locations VALUES (123456, 'lname', 'laddr')")
  db.exec("INSERT INTO Locations VALUES (118203, 'lname2', 'laddr2')")
  db.exec("INSERT INTO Locations VALUES (119200, 'lname3', 'laddr3')")
    
  db.exec("INSERT INTO Employees VALUES (100, 'name1', 90000000, 123456)")
  db.exec("INSERT INTO Employees VALUES (101, 'name2', 90100000, 118203)")
  db.exec("INSERT INTO Employees VALUES (102, 'name3', 90000020, 119200)")
  db.exec("INSERT INTO Employees VALUES (103, 'name4', 90000020, 119200)")
  
  db.exec("INSERT INTO Drivers VALUES (100, 'pdvl')")
  db.exec("INSERT INTO Drivers VALUES (101, 'pdvl1')")
  db.exec("INSERT INTO Drivers VALUES (102, 'pdvl2')")
  db.exec("INSERT INTO Drivers VALUES (103, 'pdvl3')")
  
  db.exec("INSERT INTO CarModels VALUES ('brand', 'model', 4, 1000, 200)")
  db.exec("INSERT INTO CarModels VALUES ('brand2', 'model2', 4, 1000, 200)")

  db.exec("INSERT INTO CarDetails VALUES ('plate1', 'color', 2000, 'brand', 'model', 123456)")
  db.exec("INSERT INTO CarDetails VALUES ('plate2', 'color', 2000, 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO CarDetails VALUES ('plate3', 'color', 2000, 'brand2', 'model2', 119200)")
  db.exec("INSERT INTO CarDetails VALUES ('plate4', 'color', 2000, 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO CarDetails VALUES ('plate5', 'color', 2000, 'brand', 'model', 119200)")

  db.exec("INSERT INTO Bookings VALUES (1000, DATE('2023-01-01'), 6, 'email', 'ccnum', DATE('2022-12-01'), 'brand', 'model', 123456)")
  db.exec("INSERT INTO Bookings VALUES (1001, DATE('2023-01-01'), 6, 'email2', 'ccnum', DATE('2022-12-01'), 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO Bookings VALUES (1002, DATE('2023-01-01'), 2, 'email3', 'ccnum2',  DATE('2022-12-01'), 'brand2', 'model2', 119200)")
  db.exec("INSERT INTO Bookings VALUES (1003, DATE('2023-01-01'), 6, 'email3', 'ccnum',  DATE('2022-12-01'), 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO Bookings VALUES (1004, DATE('2023-01-01'), 6, 'email3', 'ccnum',  DATE('2022-12-01'), 'brand', 'model', 119200)")

  db.exec("INSERT INTO Assigns VALUES (1000, 'plate1')")
  db.exec("INSERT INTO Assigns VALUES (1003, 'plate2')")
  print('░', end='', flush=True)

  # Check DB
  db_check = unordered(db.fetch("SELECT bid FROM Bookings;").res[-1], ([], [(1000,),(1001,), (1002,), (1003,), (1004,)]))
  if db_check != 'Correct':
    print(db_check)
    return

  # Initialize Answer
  db.exec(sql)
  print('▒', end='', flush=True)

  count = 0
  tbl = []
  if db.err != 0:
    count -= 1000
  
  # Should change db 
  db.exec("CALL auto_assign()")
  db_check_valid = unordered(db.fetch("SELECT * FROM Assigns;").res[-1], ([], [(1000, 'plate1',),(1001, 'plate4', ), (1002, 'plate3', ), (1003, 'plate2',), (1004, 'plate5', )]))
  count += check_db_state(db_check_valid, 'Number of bookings = Number of available plates', tbl)
  print('▓', end='', flush=True)

  db.close()
  print('█')
  print(table(['Check', 'Comment'], tbl))


'''
Function #1
'''
def function1(sql):
  print('Function #1:', end=' ', flush=True)

  # Connect and reset
  db = DB(**config).reset()
  print(' ', end='', flush=True)

  # Setup the database
  db.exec("INSERT INTO Customers VALUES ('email', DATE('1970-01-01'), 'address', 80000000, 'fsname', 'lsname')")
  db.exec("INSERT INTO Customers VALUES ('email2', DATE('1980-01-02'), 'address2', 80000001, 'fsname1', 'lsname1')")
  db.exec("INSERT INTO Customers VALUES ('email3', DATE('1980-01-02'), 'address3', 80000101, 'fsname1', 'lsname1')")

  db.exec("INSERT INTO Locations VALUES (123456, 'lname', 'laddr')")
  db.exec("INSERT INTO Locations VALUES (118203, 'lname2', 'laddr2')")
  db.exec("INSERT INTO Locations VALUES (119200, 'lname3', 'laddr3')")
    
  db.exec("INSERT INTO Employees VALUES (100, 'name1', 90000000, 123456)")
  db.exec("INSERT INTO Employees VALUES (101, 'name2', 90100000, 118203)")
  db.exec("INSERT INTO Employees VALUES (102, 'name3', 90000020, 119200)")
  db.exec("INSERT INTO Employees VALUES (103, 'name4', 90000020, 119200)")
  
  db.exec("INSERT INTO Drivers VALUES (100, 'pdvl')")
  db.exec("INSERT INTO Drivers VALUES (101, 'pdvl1')")
  db.exec("INSERT INTO Drivers VALUES (102, 'pdvl2')")
  db.exec("INSERT INTO Drivers VALUES (103, 'pdvl3')")
  
  db.exec("INSERT INTO CarModels VALUES ('brand', 'model', 4, 1000, 300)")
  db.exec("INSERT INTO CarModels VALUES ('brand2', 'model2', 4, 1000, 200)")

  db.exec("INSERT INTO CarDetails VALUES ('plate1', 'color', 2000, 'brand', 'model', 123456)")
  db.exec("INSERT INTO CarDetails VALUES ('plate2', 'color', 2000, 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO CarDetails VALUES ('plate3', 'color', 2000, 'brand2', 'model2', 119200)")
  db.exec("INSERT INTO CarDetails VALUES ('plate4', 'color', 2000, 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO CarDetails VALUES ('plate5', 'color', 2000, 'brand', 'model', 119200)")

  db.exec("INSERT INTO Bookings VALUES (1000, DATE('2023-01-01'), 10, 'email', 'ccnum', DATE('2022-12-01'), 'brand', 'model', 123456)")
  db.exec("INSERT INTO Bookings VALUES (1001, DATE('2023-12-01'), 6, 'email2', 'ccnum', DATE('2022-12-01'), 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO Bookings VALUES (1002, DATE('2023-01-06'), 2, 'email3', 'ccnum',  DATE('2022-12-01'), 'brand2', 'model2', 119200)")
  db.exec("INSERT INTO Bookings VALUES (1003, DATE('2023-01-03'), 1, 'email3', 'ccnum',  DATE('2022-12-01'), 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO Bookings VALUES (1004, DATE('2023-12-12'), 6, 'email3', 'ccnum',  DATE('2022-12-01'), 'brand', 'model', 119200)")

  db.exec("INSERT INTO Assigns VALUES (1000, 'plate1')")
  db.exec("INSERT INTO Assigns VALUES (1003, 'plate2')")
  db.exec("INSERT INTO Assigns VALUES (1004, 'plate5')")
  
  db.exec("INSERT INTO Hires VALUES (1000, 100, DATE('2023-01-02'), DATE('2023-01-11'), 'ccnum')")
  db.exec("INSERT INTO Hires VALUES (1003, 101, DATE('2023-01-03'), DATE('2023-01-04'), 'ccnum')")
  db.exec("INSERT INTO Hires VALUES (1004, 103, DATE('2023-12-12'), DATE('2023-12-12'), 'ccnum')")
  print('░', end='', flush=True)

  # Check DB
  db_check = unordered(db.fetch("SELECT bid FROM Bookings;").res[-1], ([], [(1000,),(1001,), (1002,), (1003,), (1004,)]))
  if db_check != 'Correct':
    print(db_check)
    return

  # Initialize Answer
  db.exec(sql)
  print('▒', end='', flush=True)

  count = 0
  tbl = []
  if db.err != 0:
    count -= 1000
  
  revenue = db.fetch("SELECT compute_revenue(%s, %s)", "2023-01-04", "2023-01-08")
  db_check_valid = unordered(revenue.res[-1], ([], [(3020, )]))
  count += check_db_state(db_check_valid, 'Initial revenue', tbl)
  print('▓', end='', flush=True)
  
  revenue1 = db.fetch("SELECT compute_revenue(%s, %s)", "2023-01-04", "2023-01-06")
  db_check_valid_1 = unordered(revenue1.res[-1], ([], [(3020, )]))
  count += check_db_state(db_check_valid_1, 'Smaller duration but covered by initial case', tbl)
  print('▓', end='', flush=True)
  
  revenue2 = db.fetch("SELECT compute_revenue(%s, %s)", "2023-01-07", "2023-01-10")
  db_check_valid_2 = unordered(revenue2.res[-1], ([], [(3000, )]))
  count += check_db_state(db_check_valid_2, 'Covering fewer bookings', tbl)
  print('▓', end='', flush=True)
  
  revenue3 = db.fetch("SELECT compute_revenue(%s, %s)", "2023-01-03", "2023-01-03")
  db_check_valid_3 = unordered(revenue3.res[-1], ([], [(3120, )]))
  count += check_db_state(db_check_valid_3, 'Covering more bookings', tbl)
  print('▓', end='', flush=True)
  
  revenue4 = db.fetch("SELECT compute_revenue(%s, %s)", "2023-01-04", "2023-01-04")
  db_check_valid_4 = unordered(revenue4.res[-1], ([], [(3020, )]))
  count += check_db_state(db_check_valid_4, 'Same as initial revenue but the range is just 1 day', tbl)
  print('▓', end='', flush=True)
  
  revenue5 = db.fetch("SELECT compute_revenue(%s, %s)", "2023-02-04", "2023-02-04")
  db_check_valid_5 = unordered(revenue5.res[-1], ([], [(0, )]))
  count += check_db_state(db_check_valid_5, 'Does not cover any bookings', tbl)
  print('▓', end='', flush=True)

  db.close()
  print('█')
  print(table(['Check', 'Comment'], tbl))


'''
Function #2
'''
def function2(sql):
  print('Function #2:', end=' ', flush=True)

  # Connect and reset
  db = DB(**config).reset()
  print(' ', end='', flush=True)

  # Setup the database
  db.exec("INSERT INTO Customers VALUES ('email', DATE('1970-01-01'), 'address', 80000000, 'fsname', 'lsname')")
  db.exec("INSERT INTO Customers VALUES ('email2', DATE('1980-01-02'), 'address2', 80000001, 'fsname1', 'lsname1')")
  db.exec("INSERT INTO Customers VALUES ('email3', DATE('1980-01-02'), 'address3', 80000101, 'fsname1', 'lsname1')")

  db.exec("INSERT INTO Locations VALUES (123456, 'lname', 'laddr')")
  db.exec("INSERT INTO Locations VALUES (118203, 'lname2', 'laddr2')")
  db.exec("INSERT INTO Locations VALUES (119200, 'lname3', 'laddr3')")
    
  db.exec("INSERT INTO Employees VALUES (100, 'name1', 90000000, 123456)")
  db.exec("INSERT INTO Employees VALUES (101, 'name2', 90100000, 118203)")
  db.exec("INSERT INTO Employees VALUES (102, 'name3', 90000020, 119200)")
  db.exec("INSERT INTO Employees VALUES (103, 'name4', 90000020, 119200)")
  
  db.exec("INSERT INTO Drivers VALUES (100, 'pdvl')")
  db.exec("INSERT INTO Drivers VALUES (101, 'pdvl1')")
  db.exec("INSERT INTO Drivers VALUES (102, 'pdvl2')")
  db.exec("INSERT INTO Drivers VALUES (103, 'pdvl3')")
  
  db.exec("INSERT INTO CarModels VALUES ('brand', 'model', 4, 1000, 300)")
  db.exec("INSERT INTO CarModels VALUES ('brand2', 'model2', 4, 1000, 200)")

  db.exec("INSERT INTO CarDetails VALUES ('plate1', 'color', 2000, 'brand', 'model', 123456)")
  db.exec("INSERT INTO CarDetails VALUES ('plate2', 'color', 2000, 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO CarDetails VALUES ('plate3', 'color', 2000, 'brand2', 'model2', 119200)")
  db.exec("INSERT INTO CarDetails VALUES ('plate4', 'color', 2000, 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO CarDetails VALUES ('plate5', 'color', 2000, 'brand', 'model', 119200)")
  db.exec("INSERT INTO CarDetails VALUES ('plate6', 'color', 2000, 'brand2', 'model2', 123456)")

  db.exec("INSERT INTO Bookings VALUES (1000, DATE('2023-01-01'), 10, 'email', 'ccnum', DATE('2022-12-01'), 'brand', 'model', 123456)")
  db.exec("INSERT INTO Bookings VALUES (1001, DATE('2023-01-01'), 6, 'email2', 'ccnum', DATE('2022-12-01'), 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO Bookings VALUES (1002, DATE('2023-01-01'), 2, 'email3', 'ccnum',  DATE('2022-12-01'), 'brand2', 'model2', 119200)")
  db.exec("INSERT INTO Bookings VALUES (1003, DATE('2023-01-01'), 1, 'email3', 'ccnum',  DATE('2022-12-01'), 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO Bookings VALUES (1004, DATE('2023-01-01'), 6, 'email3', 'ccnum',  DATE('2022-12-01'), 'brand', 'model', 119200)")

  db.exec("INSERT INTO Assigns VALUES (1000, 'plate1')")
  db.exec("INSERT INTO Assigns VALUES (1003, 'plate2')")
  db.exec("INSERT INTO Assigns VALUES (1004, 'plate5')")
  
  db.exec("INSERT INTO Hires VALUES (1000, 100, DATE('2023-01-02'), DATE('2023-01-11'), 'ccnum')")
  db.exec("INSERT INTO Hires VALUES (1003, 101, DATE('2023-01-03'), DATE('2023-01-04'), 'ccnum')")
  db.exec("INSERT INTO Hires VALUES (1004, 103, DATE('2023-12-12'), DATE('2023-12-12'), 'ccnum')")
    
  db.exec("INSERT INTO Bookings VALUES (2000, DATE('2024-01-01'), 10, 'email', 'ccnum', DATE('2023-12-01'), 'brand2', 'model2', 123456)")
  db.exec("INSERT INTO Bookings VALUES (2001, DATE('2024-01-01'), 10, 'email2', 'ccnum', DATE('2023-12-01'), 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO Bookings VALUES (2002, DATE('2024-01-01'), 10, 'email3', 'ccnum',  DATE('2023-12-01'), 'brand2', 'model2', 119200)")
  db.exec("INSERT INTO Bookings VALUES (2003, DATE('2024-01-12'), 5, 'email2', 'ccnum', DATE('2023-12-01'), 'brand2', 'model2', 118203)")
  db.exec("INSERT INTO Bookings VALUES (2004, DATE('2024-01-12'), 5, 'email3', 'ccnum',  DATE('2023-12-01'), 'brand2', 'model2', 119200)")

  db.exec("INSERT INTO Assigns VALUES (2000, 'plate6')")
  db.exec("INSERT INTO Assigns VALUES (2001, 'plate2')")
  db.exec("INSERT INTO Assigns VALUES (2002, 'plate3')")
  db.exec("INSERT INTO Assigns VALUES (2003, 'plate2')")
  db.exec("INSERT INTO Assigns VALUES (2004, 'plate3')")

  print('░', end='', flush=True)

  # Check DB
  db_check = unordered(db.fetch("SELECT bid FROM Bookings;").res[-1], ([], [(1000,), (1001,), (1002,), (1003,), (1004,),
                                                                            (2000,), (2001,), (2002,), (2003,), (2004,)]))
  if db_check != 'Correct':
    print(db_check)
    return

  # Initialize Answer
  db.exec(sql)
  print('▒', end='', flush=True)

  count = 0
  tbl = []
  if db.err != 0:
    count -= 1000
  
  # Should output correct table
  revenue = db.fetch("SELECT * FROM top_n_location(%s, %s, %s)", 1, "2023-01-04", "2023-01-08")
  db_check_valid = ordered(revenue.res[-1], (['lname', 'revenue', 'rank'], [('lname', Decimal('3000'), 1),]))
  count += check_db_state(db_check_valid, 'Simple test 1', tbl)
  print('▓', end='', flush=True)
  
  revenue = db.fetch("SELECT * FROM top_n_location(%s, %s, %s)", 2, "2023-01-04", "2023-01-08")
  db_check_valid = ordered(revenue.res[-1], (['lname', 'revenue', 'rank'], [('lname', Decimal('3000'), 1), ('lname3', Decimal('1700'), 2)]))
  count += check_db_state(db_check_valid, 'Simple test 2', tbl)
  print('▓', end='', flush=True)
  
  revenue = db.fetch("SELECT * FROM top_n_location(%s, %s, %s)", 3, "2023-01-04", "2023-01-08")
  db_check_valid = ordered(revenue.res[-1], (['lname', 'revenue', 'rank'], [('lname', Decimal('3000'), 1), ('lname3', Decimal('1700'), 2), ('lname2', Decimal('20'), 3)]))
  count += check_db_state(db_check_valid, 'Simple test 3', tbl)
  print('▓', end='', flush=True)
  
  revenue = db.fetch("SELECT * FROM top_n_location(%s, %s, %s)", 4, "2023-01-04", "2023-01-08")
  db_check_valid = ordered(revenue.res[-1], (['lname', 'revenue', 'rank'], [('lname', Decimal('3000'), 1), ('lname3', Decimal('1700'), 2), ('lname2', Decimal('20'), 3)]))
  count += check_db_state(db_check_valid, 'Simple test 4', tbl)
  print('▓', end='', flush=True)
  
  revenue = db.fetch("SELECT * FROM top_n_location(%s, %s, %s)", 1, "2024-01-05", "2024-01-15")
  db_check_valid = ordered(revenue.res[-1], (['lname', 'revenue', 'rank'], []))
  count += check_db_state(db_check_valid, 'Duplicate rank test 1', tbl)
  print('▓', end='', flush=True)
  
  revenue = db.fetch("SELECT * FROM top_n_location(%s, %s, %s)", 2, "2024-01-05", "2024-01-15")
  db_check_valid = ordered(revenue.res[-1], (['lname', 'revenue', 'rank'], [('lname2', Decimal('2900'), 2), ('lname3', Decimal('2900'), 2)]))
  count += check_db_state(db_check_valid, 'Duplicate rank test 2', tbl)
  print('▓', end='', flush=True)
  
  revenue = db.fetch("SELECT * FROM top_n_location(%s, %s, %s)", 3, "2024-01-05", "2024-01-15")
  db_check_valid = ordered(revenue.res[-1], (['lname', 'revenue', 'rank'], [('lname2', Decimal('2900'), 2), ('lname3', Decimal('2900'), 2), ('lname', Decimal('1900'), 3)]))
  count += check_db_state(db_check_valid, 'Duplicate rank test 3', tbl)
  print('▓', end='', flush=True)
  
  revenue = db.fetch("SELECT * FROM top_n_location(%s, %s, %s)", 4, "2024-01-05", "2024-01-15")
  db_check_valid = ordered(revenue.res[-1], (['lname', 'revenue', 'rank'], [('lname2', Decimal('2900'), 2), ('lname3', Decimal('2900'), 2), ('lname', Decimal('1900'), 3)]))
  count += check_db_state(db_check_valid, 'Duplicate rank test 4', tbl)
  print('▓', end='', flush=True)

  db.close()
  print('█')
  print(table(['Check', 'Comment'], tbl))




'''
Testing: Uncomment the functions below
         to test the respective component
'''
trigger1(triggers)
trigger2(triggers)
trigger3(triggers)
trigger4(triggers)
trigger5(triggers)
trigger6(triggers)
procedure1(triggers)
procedure2(triggers)
procedure3(triggers)
procedure4(triggers)
function1(triggers)
function2(triggers)
