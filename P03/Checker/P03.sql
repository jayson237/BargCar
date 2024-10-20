/*
Group #50
1. Bryan Castorius Halim
  - Testing
  - Trigger 1 and 2
  - Procedure 3
2. Jason Lienardi
  - Trigger 3
  - Procedure 1
  - Function 1 and 2
3. Jayson Ng
  - Trigger 2 and 4
  - Procedure 2 and 4
  - Function 1 and 2
4. Ng Yan Jie
  - Trigger 5 and 6
  - Procedure 4
  - Function 1
*/

-- Number 1
CREATE OR REPLACE FUNCTION check_overlap_func() 
RETURNS TRIGGER AS $$
DECLARE
    overlap_found BOOLEAN;
    curs CURSOR FOR (
      SELECT * FROM Hires 
      WHERE eid = NEW.eid
    );
    r RECORD;
    entry_fromdate DATE;
    entry_todate DATE;

BEGIN
    overlap_found := FALSE;

    OPEN curs;
    LOOP
      FETCH curs INTO r;
      EXIT WHEN NOT FOUND;
      entry_fromdate := r.fromdate;
      entry_todate := r.todate;
      IF (((entry_fromdate, entry_todate) OVERLAPS (NEW.fromdate, NEW.todate)) OR (entry_todate = NEW.fromdate) OR (NEW.todate = entry_fromdate)) THEN
        overlap_found := TRUE;
        EXIT;
      END IF;
    END LOOP;
    CLOSE curs;

    IF overlap_found THEN
        RAISE EXCEPTION 'Drivers cannot be double-booked or have the same end and start date';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_overlap_trigger
BEFORE INSERT ON Hires 
FOR EACH ROW EXECUTE FUNCTION check_overlap_func();

-- Number 2
CREATE OR REPLACE FUNCTION prevent_car_double_booking()
RETURNS TRIGGER AS $$
DECLARE
  car_already_booked BOOLEAN;
BEGIN
  SELECT EXISTS (
    SELECT 1
    FROM Assigns JOIN Bookings ON Assigns.bid = Bookings.bid
    WHERE Assigns.plate = NEW.plate AND
          (
            (Bookings.sdate <= (SELECT sdate + days - 1 FROM Bookings WHERE bid = NEW.bid)) AND
            ((SELECT sdate FROM Bookings WHERE bid = NEW.bid) <= (Bookings.sdate + Bookings.days - 1))
          )
  ) INTO car_already_booked;

  IF car_already_booked THEN
    RAISE EXCEPTION 'This car is already booked for an overlapping period.';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_car_double_booking
BEFORE INSERT ON Assigns
FOR EACH ROW
EXECUTE FUNCTION prevent_car_double_booking();


-- Number 3
CREATE OR REPLACE FUNCTION check_employee_location()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM Bookings b
        JOIN Employees e ON NEW.eid = e.eid
        WHERE b.bid = NEW.bid AND b.zip <> e.zip
    ) THEN
        RAISE EXCEPTION 'Employee must be located in the same location as the booking';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_employee_location_trigger
BEFORE INSERT ON Handover
FOR EACH ROW
EXECUTE FUNCTION check_employee_location();

-- Number 4
CREATE OR REPLACE FUNCTION verify_car_model_for_booking()
RETURNS TRIGGER AS $$
BEGIN
   IF NOT EXISTS (
    SELECT 1
    FROM CarDetails cd
    JOIN Bookings b ON b.brand = cd.brand AND b.model = cd.model
    WHERE cd.plate = NEW.plate AND b.bid = NEW.bid
  ) THEN
        RAISE EXCEPTION 'Car assigned to the booking must be for the car models for the booking';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_car_model_before_assign
BEFORE INSERT ON Assigns
FOR EACH ROW EXECUTE FUNCTION verify_car_model_for_booking();

-- Number 5
CREATE OR REPLACE FUNCTION check_car_location()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM Bookings b
        JOIN cardetails c ON NEW.plate = c.plate
        WHERE b.bid = NEW.bid AND b.zip <> c.zip
    ) THEN
        RAISE EXCEPTION 'Car must be located in the same location as the booking';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_car_location_trigger
BEFORE INSERT ON Assigns
FOR EACH ROW
EXECUTE FUNCTION check_car_location();

-- Number 6
CREATE OR REPLACE FUNCTION check_hire_date() RETURNS TRIGGER AS $$
BEGIN
    IF (NEW.fromdate < (SELECT sdate FROM Bookings B WHERE B.bid = NEW.bid) OR NEW.todate > (SELECT sdate + days FROM Bookings B WHERE B.bid = NEW.bid)) THEN
        RAISE EXCEPTION 'Drivers must be hired within the start date and end date of a booking';
    END IF;
    RETURN NEW;
END;
$$ Language plpgsql;

CREATE OR REPLACE TRIGGER check_hire_date_trigger
BEFORE INSERT ON Hires
FOR EACH ROW EXECUTE FUNCTION check_hire_date();

/*
  Write your Routines Below
    Comment out your routine if you cannot complete
    the routine.
    If any of your routine causes error (even those
    that are incomplete), you may get 0 mark for P03.
*/

-- PROCEDURE 1
CREATE OR REPLACE PROCEDURE add_employees (
    eids INT[],
    enames TEXT[],
    ephones INT[],
    zips INT[],
    pdvls TEXT[]
) AS $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..array_length(eids,1) LOOP
        INSERT INTO Employees (eid, ename, ephone, zip)
        VALUES (eids[i], enames[i], ephones[i], zips[i]);

        IF pdvls[i] IS NOT NULL THEN
            INSERT INTO Drivers (eid, pdvl)
            VALUES (eids[i], pdvls[i]);
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- PROCEDURE 2
CREATE OR REPLACE PROCEDURE add_car (
    brand TEXT,
    model TEXT,
    capacity INT,
    deposit NUMERIC,
    daily NUMERIC,
    plates TEXT[],
    colors TEXT[],
    pyears INT[],
    zips INT[]
) AS $$
BEGIN
    INSERT INTO CarModels (brand, model, capacity, deposit, daily)
    VALUES (brand, model, capacity, deposit, daily);

    IF array_length(plates, 1) > 0 THEN
        FOR i IN 1 .. array_length(plates, 1) LOOP
            INSERT INTO CarDetails (plate, color, pyear, brand, model, zip)
            VALUES (plates[i], colors[i], pyears[i], brand, model, zips[i]);
        END LOOP;
    END IF;
END;
$$ LANGUAGE plpgsql;


-- PROCEDURE 3
CREATE OR REPLACE PROCEDURE return_car (
  bid INT, eid INT
) AS $$
DECLARE
  total_cost INT;
  ccnum_returned TEXT;
BEGIN
  SELECT (cm.daily * b.days) - cm.deposit INTO total_cost
  FROM Bookings b
  JOIN CarModels cm ON cm.model = b.model AND cm.brand = b.brand
  WHERE b.bid = return_car.bid; 

  SELECT b.ccnum INTO ccnum_returned
  FROM bookings b 
  WHERE b.bid = return_car.bid;

  INSERT INTO Returned VALUES (bid, eid, ccnum_returned, total_cost);
END;
$$ LANGUAGE plpgsql;


-- PROCEDURE 4
CREATE OR REPLACE PROCEDURE auto_assign() AS $$
DECLARE
  booking RECORD;
  car_detail RECORD;
BEGIN
  FOR booking IN (
    SELECT B.bid, B.sdate, B.days, B.brand, B.model, B.zip
    FROM Bookings B
    WHERE NOT EXISTS (
      SELECT 1
      FROM Assigns A
      WHERE A.bid = B.bid
    )
    ORDER BY B.bid ASC
  )
  LOOP
    FOR car_detail IN (
      SELECT CD.plate, CD.brand, CD.model, CD.zip
      FROM CarDetails CD
      WHERE CD.brand = booking.brand AND CD.model = booking.model AND CD.zip = booking.zip
      ORDER BY CD.plate ASC
    )
    LOOP
      IF NOT EXISTS (
        SELECT 1
        FROM Assigns A
        JOIN Bookings B ON A.bid = B.bid
        WHERE A.plate = car_detail.plate
          AND (
            (booking.sdate BETWEEN B.sdate AND B.sdate + B.days - 1)
            OR (booking.sdate + booking.days - 1 BETWEEN B.sdate AND B.sdate + B.days - 1)
          )
      ) THEN
        INSERT INTO Assigns (bid, plate) VALUES (booking.bid, car_detail.plate);
        EXIT;
      END IF;
    END LOOP;
  END LOOP;
END;
$$ LANGUAGE plpgsql;


-- FUNCTION 1
CREATE OR REPLACE FUNCTION compute_revenue (
  sdate DATE, edate DATE
) RETURNS NUMERIC AS $$
BEGIN
  RETURN COALESCE((
    SELECT SUM(daily * days)
    FROM Bookings B
    JOIN Assigns A ON B.bid = A.bid
    JOIN CarModels C ON B.brand = C.brand AND B.model = C.model
    WHERE B.sdate <= compute_revenue.edate
    AND B.sdate + B.days - 1 >= compute_revenue.sdate
  ), 0) +
  COALESCE((
    SELECT SUM((todate - fromdate + 1) * 10)
    FROM Hires H
    WHERE H.fromdate <= compute_revenue.edate
    AND H.todate >= compute_revenue.sdate 
  ), 0) -
  COALESCE((
    SELECT 100 * COUNT(DISTINCT A.plate)
    FROM Assigns A
    JOIN Bookings B ON A.bid = B.bid
    WHERE B.sdate <= compute_revenue.edate
    AND B.sdate + B.days - 1 >= compute_revenue.sdate
  ), 0);
END;
$$ LANGUAGE plpgsql;


-- FUNCTION 2
CREATE OR REPLACE FUNCTION top_n_location(n INT, sdate DATE, edate DATE)
RETURNS TABLE (lname TEXT, revenue NUMERIC, rank INT) AS $$
DECLARE
  current_location RECORD;
  current_revenue NUMERIC;
  prev_revenue NUMERIC := -1;
  real_rank INT := 0;
  current_rank INT := 0;
  count_same_revenue INT := 0;
BEGIN
  CREATE TEMPORARY TABLE revenue_table (
    lname TEXT,
    revenue NUMERIC
  ) ON COMMIT DROP;

  FOR current_location IN
    SELECT l.lname, l.zip
    FROM Locations l
  LOOP
   current_revenue := (
    (SELECT COALESCE(SUM(daily * days), 0)
    FROM Bookings B
    JOIN Assigns A ON B.bid = A.bid
    JOIN CarModels C ON B.brand = C.brand AND B.model = C.model
    WHERE B.sdate <= top_n_location.edate
    AND B.sdate + B.days - 1 >= top_n_location.sdate AND B.zip = current_location.zip) +
    (SELECT COALESCE(SUM((todate - fromdate + 1) * 10), 0)
    FROM Hires H
    JOIN Employees E ON H.eid = E.eid
    WHERE H.fromdate <= top_n_location.edate
    AND H.todate >= top_n_location.sdate AND E.zip = current_location.zip) -
    (SELECT COALESCE(100 * COUNT(DISTINCT A.plate), 0)
    FROM Assigns A
    JOIN Bookings B ON A.bid = B.bid
    JOIN CarDetails C ON A.plate = C.plate
    WHERE B.sdate <= top_n_location.edate
    AND B.sdate + B.days - 1 >= top_n_location.sdate AND C.zip = current_location.zip)
  );

    INSERT INTO revenue_table (lname, revenue)
    VALUES (current_location.lname, current_revenue);
  END LOOP;

  CREATE TEMPORARY TABLE sorted_table AS
  SELECT * FROM revenue_table ORDER BY revenue DESC, lname ASC;

  CREATE TEMPORARY TABLE duplicate_count AS
  SELECT so.revenue, COUNT(*) AS count
  FROM sorted_table so
  GROUP BY so.revenue;

  FOR current_location IN SELECT so.lname, so.revenue FROM sorted_table so LOOP
    current_revenue := current_location.revenue;
    IF current_revenue <> prev_revenue THEN
      real_rank := real_rank + (SELECT count FROM duplicate_count D WHERE D.revenue = current_revenue);
    END IF;
    current_rank := real_rank;
    IF current_rank > n THEN
      EXIT;
    END IF;
    lname := current_location.lname;
    revenue := current_location.revenue;
    rank := current_rank;
    RETURN NEXT;
    prev_revenue := current_revenue;
  END LOOP;

  DROP TABLE revenue_table;
  DROP TABLE sorted_table;
  DROP TABLE duplicate_count;
END;
$$ LANGUAGE plpgsql;
