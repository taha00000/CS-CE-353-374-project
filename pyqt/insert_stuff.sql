-- Insert into Resources table
INSERT INTO Resources (Resource_ID, Resource_Name, Value, Purchase_Date) VALUES
    (1, 'Microphone', 150.00, '2023-01-15'),
    (2, 'Camera', 500.00, '2023-03-20'),
    (3, 'Flash drive', 20.00, '2023-05-10');

-- Insert into Teams table
INSERT INTO Teams (Team_ID, Team_Name) VALUES
    (1, 'Team A'),
    (2, 'Team B'),
    (3, 'Team C');

-- Insert into StudentLife_Staff table
INSERT INTO StudentLife_Staff (Staff_ID, Staff_Name) VALUES
    (101, 'John Doe'),
    (102, 'Jane Smith'),
    (103, 'Alice Johnson');

-- Insert into Club_Teams table
INSERT INTO Club_Teams (Team_ID, Club_Name) VALUES
    (1, 'Science Club'),
    (2, 'Literature Club'),
    (3, 'Music Club');

-- Insert into Borrowed_Resources table
INSERT INTO Borrowed_Resources (Resource_ID, Borrower_ID, Event_ID, Due_Date) VALUES
    (1, 101, 201, '2023-08-20'),
    (2, 102, 202, '2023-09-10'),
    (3, 103, 203, '2023-07-25');

-- Insert into Events table
INSERT INTO Events (Event_ID, Event_Name, Date, Time, Location, Budget) VALUES
    (201, 'Science Fair', '2023-08-15', '10:00:00', 'Auditorium', 1000.00),
    (202, 'Literature Symposium', '2023-09-05', '13:00:00', 'Library', 800.00),
    (203, 'Music Concert', '2023-07-20', '19:00:00', 'Open Ground', 1200.00);

-- Insert into Member_Attendance table
INSERT INTO Member_Attendance (Event_ID, Student_ID, Attended) VALUES
    (201, 'S12345', 1),
    (202, 'S23456', 0),
    (203, 'S34567', 1);

-- Insert into Students table
INSERT INTO Students (Student_ID, Student_Name) VALUES
    ('S12345', 'John Doe'),
    ('S23456', 'Jane Smith'),
    ('S34567', 'Alice Johnson');

-- Insert into Event_Request table
INSERT INTO Event_Request (Event_Request_ID, Event_Name, Club_Name, Date, Time, Location, Budget, Approved, Approving_staff_ID) VALUES
    (301, 'Seminar', 'Science Club', '2023-10-10', '14:00:00', 'Conference Hall', 500.00, 1, 101),
    (302, 'Drama Festival', 'Literature Club', '2023-11-05', '18:00:00', 'Auditorium', 700.00, 0, NULL),
    (303, 'Charity Concert', 'Music Club', '2023-12-15', '20:00:00', 'Open Ground', 1000.00, 0, NULL);

-- Insert into Clubs table
INSERT INTO Clubs (Club_Name, Funds) VALUES
    ('Science Club', 5000.00),
    ('Literature Club', 3000.00),
    ('Music Club', 7000.00);

-- Insert into Borrower table
INSERT INTO Borrower (Borrower_ID, Team_ID, Club_Name, Student_ID, Role) VALUES
    (101, 1, 'Science Club', 'S12345', 'President'),
    (102, 2, 'Literature Club', 'S23456', 'Vice President'),
    (103, 3, 'Music Club', 'S34567', 'Secretary');

-- Insert into EventClub table
INSERT INTO EventClub (Event_ID, Club_Name) VALUES
    (201, 'Science Club'),
    (202, 'Literature Club'),
    (203, 'Music Club');

-- Insert into Club_member table
INSERT INTO Club_member (Club_Name, Student_ID, Team_ID, Position) VALUES
    ('Science Club', 'S12345', 1, 'President'),
    ('Literature Club', 'S23456', 2, 'Vice President'),
    ('Music Club', 'S34567', 3, 'Secretary');

-- Insert into Club_Funds_Tracker table
INSERT INTO Club_Funds_Tracker (Club_Name, Amount, Reason) VALUES
    ('Science Club', 1000.00, 'Fundraising'),
    ('Literature Club', 500.00, 'Event expenses'),
    ('Music Club', 1200.00, 'Equipment purchase');

-- Insert into EventFeedback table
INSERT INTO EventFeedback (Event_ID, Student_ID, Feedback) VALUES
    (201, 'S12345', 'Great event, well organized!'),
    (202, 'S23456', 'Good effort, but needs improvement.'),
    (203, 'S34567', 'Excellent performance, enjoyed it!');

