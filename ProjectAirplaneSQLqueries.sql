CREATE TABLE Airport(
    airportID varChar(5),
  	name varChar(20) NOT null,
    city varChar(10),
    country varChar(15),
    numTerminal int,
    type enum("domestic", "international", "both"),
    PRIMARY KEY (airportID)
);

CREATE TABLE Flight(
    AirlineName varChar(20),
  	flightNum char(10),
    departDate date,
    departTime time,
    arrivalDate date,
    arrivalTime time,
    departAirportID varChar(5),
    arrivalAirportID varChar(5),
	basePrice int,
    flightStatus enum("delayed", "on time", "cancelled"),
    PRIMARY KEY (AirlineName, flightNum, departDate, departTime),
    FOREIGN KEY (AirlineName) REFERENCES Airline(AirlineName),
    FOREIGN KEY (departAirportID) REFERENCES Airport(airportID),
    FOREIGN KEY (arrivalAirportID) REFERENCES Airport(airportID)
);

CREATE TABLE Airline(
    AirlineName varChar(20),
    PRIMARY KEY (AirlineName)
);

CREATE TABLE AirlineStaff(
    username varChar(15),
  	password varChar(15),
    firstName varChar(20),
    lastName varChar(20),
    birthDate date,
    airlineName varChar(20),
    PRIMARY KEY (username),
    FOREIGN KEY (airlineName) REFERENCES Airline(AirlineName)
);

CREATE TABLE AirlineStaffEmail(
    username varChar(15),
    email varChar(20),
    PRIMARY KEY (username),
    FOREIGN KEY (username) REFERENCES AirlineStaff(username)
);

CREATE TABLE AirlineStaffPhoneNum(
    username varChar(15),
    phoneNum char(10),
    PRIMARY KEY (username),
    FOREIGN KEY (username) REFERENCES AirlineStaff(username)
);

CREATE TABLE Airplane(
    planeID char(5),
    airlineName varChar(20),
  	numSeat numeric(4,0),
    manufacutre varChar(20),
    modelNum varChar(10),
    age int,
    manuDate date, 
    PRIMARY KEY (planeID),
    FOREIGN KEY (airlineName) REFERENCES Airline(AirlineName)  
);

CREATE TABLE Ticket(
    ticketID char(5),
    flightNum char (10),
    firstName varChar(20),
    lastName varChar(20),
    email varChar(20),
    ticketPrice int,
    paymentType enum("credit", "debit"),
    cardNo char(16),
    cardName varChar(20),
    expDate date,
    PRIMARY KEY (ticketID),
    FOREIGN KEY (flightNum) REFERENCES Flight(flightNum)  
);

CREATE TABLE Purchase(
  	ticketID char(5),
    email varChar(20),
    purchaseDate date,
    PRIMARY KEY (ticketID),
    FOREIGN KEY (ticketID) REFERENCES Ticket(ticketID),
    FOREIGN KEY (email) REFERENCES Customer(email)
);

CREATE TABLE Customer(
    email char(20),
    password varChar(20),
    firstName varChar(20),
    lastName varChar(20),
    buildingNum varChar(10),
    streetName varChar(20),
    aptNum varChar(10),
    city varChar(10),
    state varChar(15),
    zipCode char(5),
    phoneNum char(10),
    PRIMARY KEY (email)
);

CREATE TABLE Passport(
  	passportNum varChar(15),
    passportExpDate date,
    passportCountry varChar(15),
    birthDate date, 
    email varChar(20),
    PRIMARY KEY (passportNum),
    FOREIGN KEY (email) REFERENCES Customer(email)
);

CREATE TABLE Maintenance(
    planeID char(5),
    undergoing boolean,
    startDate date,
    endDate date,
    startTime time, 
    endTime time,
    PRIMARY KEY(startDate),
    FOREIGN KEY(planeID) REFERENCES Airplane(planeID)
);  

CREATE TABLE Review(
    flightNum char(10),
    email char(20),
    customerComment varChar(300),
    PRIMARY KEY(flightNum),
    FOREIGN KEY(flightNum) REFERENCES Flight(flightNum),
    FOREIGN KEY(email) REFERENCES Customer(email),
    rating int CHECK (rating <= 5)
);  

insert into Airline values ("Jet Blue");
insert into Airline values ("Delta Airline")
insert into Airline values ("Korean Air")

insert into Airport values ("JFK", "John F. Kennedy Airport", "NYC", "US", null, "international");
insert into Airport values ("PVG", "Shanghai Pudong International Airport", "Shanghai", "China", null, "international");

--Customer (3)
insert into Customer values ("jl10285@nyu.edu", "20000105", "Jun", "Lee", "40 east", "7th street", "202C", "NYC", "NY", "10003", "1088259785");
insert into Customer values ("jy2639@nyu.edu", "12344321", "Joonha", "Yu", "25 west", "44th street", "36", "NYC", "NY", "10013", "0123456789");
insert into Customer values ("hl3679@nyu.edu", "87654321", "Andy", "Lee", "80", "1th street", "404E", "NYC", "NY", "13333", "0111222333");

insert into Passport values ("M1234567", '2028-05-15', "South Korea", '2000-01-05', "jl10285@nyu.edu");
insert into Passport values ("M7654321", '2026-06-09', "South Korea", '1999-03-04', "jy2639@nyu.edu");
insert into Passport values ("M3334445", '2027-07-08', "South Korea", '2001-11-07', "hl3679@nyu.edu");

--Airplanes (3)

insert into Airplane values ("56789", "Jet Blue", 800, "Boeing", "747", 4, '2019-10-31');
insert into Airplane values ("12345", "Jet Blue", 500, "Airbus", "A319", 2, '2021-10-31');
insert into Airplane values ("12000", "Jet Blue", 1200, "Airbus", "A380", 1, '2022-10-31');

--Airline Staff working for Jet Blue
insert into AirlineStaff values ("joonrb", "12344321", "Daun", "Kim", '2002-11-06', "Jet Blue");
insert into AirlineStaff values ("staff", "11111111", "Emerson", "Matts", '2000-01-01', "Delta Airline")
insert into AirlineStaff values ("ethan", "00001111", "Ethan", "Hunt", '2001-12-25', "Korean Air")

insert into AirlineStaffEmail values ("joonrb", "dk123@gmail.com");
insert into AirlineStaffPhoneNum values ("joonrb", "0123456789");
insert into AirlineStaffEmail values ("staff", "staff@email.com");
insert into AirlineStaffPhoneNum values ("staff", "01012345678");
insert into AirlineStaffEmail values ("ethan", "ethan@hunt.com");
insert into AirlineStaffPhoneNum values ("ethan", "0000000000");

--Several flights on time, delayed status

insert into flight values ("Jet Blue", "J333666999", '2023-11-07', '14:30:00', '2023-11-09', '11:30:00', "JFK", "PVG", 1500, "on time");
insert into flight values ("Jet Blue", "A111222333", '2023-11-11', '05:00:00', '2023-11-11', '22:20:00', "PVG", "JFK", 3500, "on time");
insert into flight values ("Jet Blue", "C1234565789", '2023-01-23', '07:30:00', '2023-01-24', '20:20:00', "JFK", "PVG", 1200, "delayed");
insert into flight values ("Jet Blue", "F147258369", '2023-02-01', '12:30:00', '2023-02-01', '23:40:00', "PVG", "JFK", 2000, "delayed");
insert into flight values ("Jet Blue", "Z000000000", '2022-12-12', '04:10:00', '2022-12-13', '18:30:00', "JFK", "PVG", 5500, "cancelled");
insert into flight values ("Jet Blue", "X100000001", '2022-12-25', '22:20:00', '2022-12-25', '12:30:00', "PVG", "JFK", 5500, "cancelled");

-- tickets corresponding to flights 

insert into Ticket values ("33345", "J333666999", "Jun", "Lee", "jl10285@nyu.edu", 1500, "credit", "1234567891011123", "JunLee", '2027-05-01');
insert into Ticket values ("33445", "A111222333", "Jun", "Lee", "jl10285@nyu.edu", 1500, "credit", "1234567891011123", "JunLee", '2027-05-01');
insert into Ticket values ("12345", "C1234565789", "Joonha", "Yu", "jy2639@nyu.edu", 1500, "debit", "0000111122223333", "JoonhaYu", '2028-2-02');
insert into Ticket values ("54321", "F147258369", "Joonha", "Yu", "jy2639@nyu.edu", 1500, "debit", "0000111122223333", "JoonhaYu", '2028-02-02');
insert into Ticket values ("55555", "Z000000000", "Andy", "Lee", "hl3679@nyu.edu", 1500, "credit", "3211110987654321", "AndyLee", '2027-9-09');
insert into Ticket values ("00000", "X100000001", "Andy", "Lee", "hl3679@nyu.edu", 1500, "credit", "3211110987654321", "AndyLee", '2027-9-09');

-- purchase records

insert into Purchase values ("33345", "jl10285@nyu.edu", '2023-01-05');
insert into Purchase values ("33445", "jl10285@nyu.edu", '2023-01-05');
insert into Purchase values ("12345", "jy2639@nyu.edu", '2022-12-25');
insert into Purchase values ("54321", "jy2639@nyu.edu", '2022-12-25');
insert into Purchase values ("55555", "hl3679@nyu.edu", '2023-11-07');
insert into Purchase values ("00000", "hl3679@nyu.edu", '2023-11-07');