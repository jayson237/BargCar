CREATE TABLE Customers (
    email TEXT PRIMARY KEY,
    address TEXT NOT NULL,
    fsname TEXT,
    lsname TEXT NOT NULL,
    phone TEXT NOT NULL,
    dob DATE NOT NULL CHECK (dob < NOW())
);

CREATE TABLE InitiatesBookings (
    bid INT PRIMARY KEY,
    sdate DATE NOT NULL,
    days INT NOT NULL,
    ccnum INT NOT NULL,
    bdate DATE NOT NULL,
    email TEXT REFERENCES Customers NOT NULL,
    UNIQUE (bid, sdate, days),
    CHECK (bdate < sdate)
);

CREATE TABLE Locations (
    zip INT PRIMARY KEY,
    laddr TEXT NOT NULL, 
    lname TEXT UNIQUE NOT NULL
);

CREATE TABLE CarModels (
    brand TEXT,
    model TEXT,
    capacity INT NOT NULL,
    deposit MONEY NOT NULL,
    daily MONEY NOT NULL,
    PRIMARY KEY (brand, model)
);

CREATE TABLE RentsBookings (
    bid INT REFERENCES InitiatesBookings,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    PRIMARY KEY (bid), 
    FOREIGN KEY (brand, model) REFERENCES CarModels
);

CREATE TABLE ForBookings (
    bid INT REFERENCES InitiatesBookings,
    zip INT REFERENCES Locations NOT NULL,
    PRIMARY KEY (bid)
);

CREATE TABLE CarDetailsDetailsFor (
    plate TEXT PRIMARY KEY,
    color TEXT NOT NULL,
    pyear INT NOT NULL, 
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    FOREIGN KEY (brand, model) REFERENCES CarModels
);

CREATE TABLE Assigns (
    bid INT REFERENCES InitiatesBookings,
    plate TEXT REFERENCES CarDetailsDetailsFor,
    PRIMARY KEY (bid)
);

CREATE TABLE CarDetailsParks (
    plate TEXT REFERENCES CarDetailsDetailsFor,
    zip INT REFERENCES Locations NOT NULL,
    PRIMARY KEY (plate)
);

CREATE TABLE EmployeesWorks (
    eid INT PRIMARY KEY,
    ename TEXT NOT NULL,
    ephone INT NOT NULL,
    zip INT REFERENCES Locations NOT NULL
);

CREATE TABLE Drivers (
    eid INT REFERENCES EmployeesWorks ON DELETE CASCADE,
    pdvl TEXT UNIQUE NOT NULL,
    PRIMARY KEY (eid)
);

CREATE TABLE Returned (
    bid INT REFERENCES Assigns(bid),
    eid INT REFERENCES EmployeesWorks,
    ccnum INT NOT NULL,
    cost INT NOT NULL,
    PRIMARY KEY (bid),
    CHECK (cost < 0 OR ccnum IS NOT NULL)
);

CREATE TABLE Handover (
    bid INT REFERENCES Assigns,
    eid INT, 
    plate INT REFERENCES Assigns NOT NULL,
    PRIMARY KEY (bid),
    FOREIGN KEY (eid) REFERENCES EmployeesWorks
);

CREATE TABLE Hires (
    bid INT,
    sdate DATE,
    days INT, 
    eid INT, 
    fromdate DATE NOT NULL,
    todate DATE NOT NULL,
    ccnum INT NOT NULL,
    PRIMARY KEY (bid),
    FOREIGN KEY (eid) REFERENCES Drivers,
    FOREIGN KEY (bid, sdate, days) REFERENCES InitiatesBookings(bid, sdate, days),
    CHECK (fromdate < todate),
    CHECK (fromdate >= sdate AND todate <= sdate + days * INTERVAL '1 day')
);