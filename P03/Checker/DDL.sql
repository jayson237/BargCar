DROP TABLE IF EXISTS Hires      CASCADE;
DROP TABLE IF EXISTS Returned   CASCADE;
DROP TABLE IF EXISTS Handover   CASCADE;
DROP TABLE IF EXISTS Assigns    CASCADE;
DROP TABLE IF EXISTS Bookings   CASCADE;
DROP TABLE IF EXISTS CarDetails CASCADE;
DROP TABLE IF EXISTS CarModels  CASCADE;
DROP TABLE IF EXISTS Drivers    CASCADE;
DROP TABLE IF EXISTS Employees  CASCADE;
DROP TABLE IF EXISTS Locations  CASCADE;
DROP TABLE IF EXISTS Customers  CASCADE;

CREATE TABLE Customers (
  email     TEXT  PRIMARY KEY,
  dob       DATE  NOT NULL CHECK (dob < NOW()),
  address   TEXT  NOT NULL,
  phone     INT   CHECK (phone >= 80000000 AND phone <= 99999999),
  fsname    TEXT  NOT NULL,
  lsname    TEXT  NOT NULL
);

CREATE TABLE Locations (
  zip       INT   PRIMARY KEY,
  lname     TEXT  NOT NULL UNIQUE,
  laddr     TEXT  NOT NULL
);

CREATE TABLE Employees (
  eid       INT   PRIMARY KEY,
  ename     TEXT  NOT NULL,
  ephone    INT   CHECK (ephone >= 80000000 AND ephone <= 99999999),
  zip       INT   NOT NULL
    REFERENCES Locations (zip)
);

CREATE TABLE Drivers (
  eid       INT   PRIMARY KEY
    REFERENCES Employees (eid)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  pdvl      TEXT  NOT NULL UNIQUE
);

CREATE TABLE CarModels (
  brand     TEXT,
  model     TEXT,
  capacity  INT     NOT NULL CHECK (capacity > 0),
  deposit   NUMERIC NOT NULL CHECK (deposit > 0),
  daily     NUMERIC NOT NULL CHECK (daily > 0),
  PRIMARY KEY (brand, model)
);

CREATE TABLE CarDetails (
  plate     TEXT  PRIMARY KEY,
  color     TEXT  NOT NULL,
  pyear     INT   CHECK(pyear > 1900),
  brand     TEXT  NOT NULL,
  model     TEXT  NOT NULL,
  zip       INT   NOT NULL
    REFERENCES Locations (zip),
  FOREIGN KEY (brand, model) REFERENCES CarModels (brand, model)
);

CREATE TABLE Bookings (
  bid       INT   PRIMARY KEY,
  sdate     DATE  NOT NULL,
  days      INT   NOT NULL CHECK (days > 0),
  email     TEXT  NOT NULL
    REFERENCES Customers (email),
  ccnum     TEXT  NOT NULL,
  bdate     DATE  NOT NULL CHECK (bdate < sdate),
  brand     TEXT  NOT NULL,
  model     TEXT  NOT NULL,
  zip       INT   NOT NULL
    REFERENCES Locations (zip),
  FOREIGN KEY (brand, model) REFERENCES CarModels (brand, model)
);

CREATE TABLE Assigns (
  bid       INT   PRIMARY KEY
    REFERENCES Bookings (bid),
  plate     TEXT  NOT NULL
    REFERENCES CarDetails (plate)
);

CREATE TABLE Handover (
  bid       INT   PRIMARY KEY
    REFERENCES Assigns (bid),
  eid       INT   NOT NULL
    REFERENCES Employees (eid)
);

CREATE TABLE Returned (
  bid       INT   PRIMARY KEY
    REFERENCES Handover (bid),
  eid       INT   NOT NULL
    REFERENCES Employees (eid),
  ccnum     TEXT  CHECK (cost <= 0 OR ccnum IS NOT NULL),
  cost      NUMERIC   NOT NULL
);

CREATE TABLE Hires (
  bid       INT   PRIMARY KEY
    REFERENCES Assigns (bid),
  eid       INT   NOT NULL
    REFERENCES Drivers (eid),
  fromdate  DATE  NOT NULL,
  todate    DATE  NOT NULL CHECK (todate >= fromdate),
  ccnum     TEXT  NOT NULL
);
