--Entities

CREATE TABLE Person(
  email VARCHAR(50) PRIMARY KEY,
  pname VARCHAR(30),
  gender CHAR,
  dob DATE,
  weight REAL,
  height INTEGER
)

CREATE TABLE Food(
  fid INTEGER PRIMARY KEY,
  fname VARCHAR(30),
  calories INTEGER NOT NULL,
  serving_size INTEGER,
  proteins INTEGER,
  carbs INTEGER,
  fats INTEGER
)

CREATE TABLE Diet(
  did INTEGER PRIMARY KEY,
  dname VARCHAR(20) NOT NULL,
  calorie_total INTEGER
)

CREATE TABLE Workout_Program(
  wid INTEGER PRIMARY KEY,
  wname VARCHAR(20) NOT NULL,
  total_cal_expend_per_lb INTEGER
)

CREATE TABLE Exercise(
  eid INTEGER PRIMARY KEY,
  ename VARCHAR(30),
  cal_expend_per_lb INTEGER NOT NULL
)

CREATE TABLE Strength_Exercise(
  eid INTEGER PRIMARY KEY REFERENCES Exercise(eid),
  sets INTEGER,
  reps INTEGER,
  weight INTEGER
)

CREATE TABLE Cardio_Exercise(
  eid INTERGER PRIMARY KEY REFERENCES Exercise(eid),
  duration INTEGER,
  speed INTEGER
)

CREATE TABLE Competition(
  cid INTEGER PRIMARY KEY,
  cname VARCHAR (30),
  start DATE,
  stop DATE,
  win_condition INTEGER
)

--Relationships
CREATE TABLE Consists_Of(
  did INTEGER,
  fid INTEGER,
  PRIMARY KEY(did, fid),
  FOREIGN KEY(did) REFERENCES Diet
    ON DELETE CASCADE,
  FOREIGN KEY(fid) REFERENCES Food
    ON UPDATE CASCADE
)

CREATE TABLE Consumes(
  email VARCHAR(50),
  did INTEGER,
  PRIMARY KEY(email),
  FOREIGN KEY(email) REFERENCES Person
    ON DELETE CASCADE,
  FOREIGN KEY(did) REFERENCES Diet
)

CREATE TABLE Follow(
  email VARCHAR(50),
  wid INTEGER,
  PRIMARY KEY(email),
  FOREIGN KEY(email) REFERENCES Person
    ON DELETE CASCADE,
  FOREIGN KEY(wid) REFERENCES Workout_Program
    ON UPDATE CASCADE
)

CREATE TABLE Uses(
  wid INTEGER,
  eid INTEGER,
  PRIMARY KEY(wid,ename),
  FOREIGN KEY(wid) REFERENCES Workout_Program
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY(eid) REFERENCES Exercise
    ON UPDATE CASCADE
)

CREATE TABLE Participates(
  email VARCHAR(50),
  cid INTEGER,
  start DATE,
  date_created DATE,
  PRIMARY KEY(email, cid),
  FOREIGN KEY(email) REFERENCES Person
    ON DELETE CASCADE,
  FOREIGN KEY(cid) REFERENCES Competition
)
