CREATE TABLE [Resource_Request] (
    Resource_Request_ID int NOT NULL,
    Resource_ID int NOT NULL,
    Borrower_ID int NOT NULL,
    Due_Date date NOT NULL,
    Approved BIT,
    Approving_staff_ID int,
    CONSTRAINT [PK_RESOURCE_REQUEST] PRIMARY KEY CLUSTERED ([Resource_Request_ID] ASC)
);

CREATE TABLE [Resources] (
    Resource_ID int NOT NULL,
    Resource_Name varchar(100) NOT NULL,
    Value decimal NOT NULL,
    Purchase_Date date NOT NULL,
    CONSTRAINT [PK_RESOURCES] PRIMARY KEY CLUSTERED ([Resource_ID] ASC)
);

CREATE TABLE [Teams] (
    Team_ID int NOT NULL,
    Team_Name varchar(100) NOT NULL,
    CONSTRAINT [PK_TEAMS] PRIMARY KEY CLUSTERED ([Team_ID] ASC)
);

CREATE TABLE [StudentLife_Staff] (
    Staff_ID int NOT NULL,
    Staff_Name varchar(100) NOT NULL,
    CONSTRAINT [PK_STUDENTLIFE_STAFF] PRIMARY KEY CLUSTERED ([Staff_ID] ASC)
);

CREATE TABLE [Club_Teams] (
    Team_ID int NOT NULL,
    Club_Name varchar(100) NOT NULL,
    CONSTRAINT [PK_CLUB_TEAMS] PRIMARY KEY CLUSTERED ([Team_ID] ASC)
);

CREATE TABLE [Borrowed_Resources] (
    Resource_ID int NOT NULL,
    Borrower_ID int NOT NULL,
    Event_ID int NOT NULL,
    Due_Date date NOT NULL,
    CONSTRAINT [PK_BORROWED_RESOURCES] PRIMARY KEY CLUSTERED ([Resource_ID] ASC)
);

CREATE TABLE [Events] (
    Event_ID int NOT NULL,
    Event_Name varchar(100) NOT NULL,
    Date date NOT NULL,
    Time time NOT NULL,
    Location varchar(100) NOT NULL,
    Budget decimal NOT NULL,
    CONSTRAINT [PK_EVENTS] PRIMARY KEY CLUSTERED ([Event_ID] ASC)
);

CREATE TABLE [Member_Attendance] (
    Event_ID int NOT NULL,
    Student_ID varchar(100) NOT NULL,
    Attended BIT NOT NULL,
    CONSTRAINT [PK_MEMBER_ATTENDANCE] PRIMARY KEY CLUSTERED ([Event_ID] ASC)
);

CREATE TABLE [Students] (
    Student_ID varchar(100) NOT NULL,
    Student_Name varchar(100) NOT NULL,
    CONSTRAINT [PK_STUDENTS] PRIMARY KEY CLUSTERED ([Student_ID] ASC)
);

CREATE TABLE [Event_Request] (
    Event_Request_ID int NOT NULL,
    Event_Name varchar(100) NOT NULL,
    Club_Name varchar(100) NOT NULL,
    Date date NOT NULL,
    Time time NOT NULL,
    Location varchar(100) NOT NULL,
    Budget decimal NOT NULL,
    Approved BIT NOT NULL,
    Approving_staff_ID int,
    CONSTRAINT [PK_EVENT_REQUEST] PRIMARY KEY CLUSTERED ([Event_Request_ID] ASC)
);

CREATE TABLE [Clubs] (
    Club_Name varchar(100) NOT NULL,
    Funds decimal NOT NULL,
    CONSTRAINT [PK_CLUBS] PRIMARY KEY CLUSTERED ([Club_Name] ASC)
);

CREATE TABLE [Borrower] (
    Borrower_ID int NOT NULL,
    Team_ID int NOT NULL,
    Club_Name varchar(100) NOT NULL,
    Student_ID varchar(100) NOT NULL,
    Role varchar(100) NOT NULL,
    CONSTRAINT [PK_BORROWER] PRIMARY KEY CLUSTERED ([Borrower_ID] ASC)
);

CREATE TABLE [EventClub] (
    Event_ID int NOT NULL,
    Club_Name varchar(100) NOT NULL,
    CONSTRAINT [PK_EVENTCLUB] PRIMARY KEY CLUSTERED ([Event_ID] ASC)
);

CREATE TABLE [Club_member] (
    Club_Name varchar(100) NOT NULL,
    Student_ID varchar(100) NOT NULL,
    Team_ID int NOT NULL,
    Position varchar(100) NOT NULL,
    CONSTRAINT [PK_CLUB_MEMBER] PRIMARY KEY CLUSTERED ([Club_Name] ASC)
);

CREATE TABLE [Club_Funds_Tracker] (
    Club_Name varchar(100) NOT NULL,
    Amount decimal NOT NULL,
    Reason varchar(100) NOT NULL,
    CONSTRAINT [PK_CLUB_FUNDS_TRACKER] PRIMARY KEY CLUSTERED ([Club_Name] ASC)
);

CREATE TABLE [EventFeedback] (
    Event_ID int NOT NULL,
    Student_ID varchar(100) NOT NULL,
    Feedback varchar(100) NOT NULL,
    CONSTRAINT [PK_EVENTFEEDBACK] PRIMARY KEY CLUSTERED ([Event_ID] ASC)
);

ALTER TABLE [Resource_Request] ADD CONSTRAINT [Resource_Request_fk0] FOREIGN KEY ([Resource_ID]) REFERENCES [Resources]([Resource_ID]) ON UPDATE CASCADE;
ALTER TABLE [Resource_Request] ADD CONSTRAINT [Resource_Request_fk1] FOREIGN KEY ([Borrower_ID]) REFERENCES [Borrower]([Borrower_ID]) ON UPDATE CASCADE;
ALTER TABLE [Resource_Request] ADD CONSTRAINT [Resource_Request_fk2] FOREIGN KEY ([Approving_staff_ID]) REFERENCES [StudentLife_Staff]([Staff_ID]) ON UPDATE CASCADE;

ALTER TABLE [Teams] ADD CONSTRAINT [Teams_fk0] FOREIGN KEY ([Team_ID]) REFERENCES [Club_Teams]([Team_ID]) ON UPDATE CASCADE;

ALTER TABLE [Club_Teams] ADD CONSTRAINT [Club_Teams_fk0] FOREIGN KEY ([Team_ID]) REFERENCES [Teams]([Team_ID]) ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE [Club_Teams] ADD CONSTRAINT [Club_Teams_fk1] FOREIGN KEY ([Club_Name]) REFERENCES [Clubs]([Club_Name]) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE [Borrowed_Resources] ADD CONSTRAINT [Borrowed_Resources_fk0] FOREIGN KEY ([Resource_ID]) REFERENCES [Resources]([Resource_ID]) ON UPDATE CASCADE;
ALTER TABLE [Borrowed_Resources] ADD CONSTRAINT [Borrowed_Resources_fk1] FOREIGN KEY ([Borrower_ID]) REFERENCES [Borrower]([Borrower_ID]) ON UPDATE CASCADE;
ALTER TABLE [Borrowed_Resources] ADD CONSTRAINT [Borrowed_Resources_fk2] FOREIGN KEY ([Event_ID]) REFERENCES [Events]([Event_ID]) ON UPDATE CASCADE;

ALTER TABLE [Member_Attendance] ADD CONSTRAINT [Member_Attendance_fk0] FOREIGN KEY ([Event_ID]) REFERENCES [Events]([Event_ID]) ON UPDATE CASCADE;
ALTER TABLE [Member_Attendance] ADD CONSTRAINT [Member_Attendance_fk1] FOREIGN KEY ([Student_ID]) REFERENCES [Students]([Student_ID]) ON UPDATE CASCADE;

ALTER TABLE [Event_Request] ADD CONSTRAINT [Event_Request_fk0] FOREIGN KEY ([Club_Name]) REFERENCES [Clubs]([Club_Name]) ON UPDATE CASCADE;
--ALTER TABLE [Event_Request] ADD CONSTRAINT [Event_Request_fk1] FOREIGN KEY ([Date]) REFERENCES [Events]([Date]) ON UPDATE CASCADE;
--ALTER TABLE [Event_Request] ADD CONSTRAINT [Event_Request_fk2] FOREIGN KEY ([Time]) REFERENCES [Events]([Time]) ON UPDATE CASCADE;
--ALTER TABLE [Event_Request] ADD CONSTRAINT [Event_Request_fk3] FOREIGN KEY ([Location]) REFERENCES [Events]([Location]) ON UPDATE CASCADE;
--ALTER TABLE [Event_Request] ADD CONSTRAINT [Event_Request_fk4] FOREIGN KEY ([Budget]) REFERENCES [Events]([Budget]) ON UPDATE CASCADE;
--ALTER TABLE [Event_Request] ADD CONSTRAINT [Event_Request_fk5] FOREIGN KEY ([Approving_staff_ID]) REFERENCES [StudentLife_Staff]([Staff_ID]) ON UPDATE CASCADE;

ALTER TABLE [Borrower] ADD CONSTRAINT [Borrower_fk0] FOREIGN KEY ([Team_ID]) REFERENCES [Teams]([Team_ID]) ON UPDATE CASCADE;
ALTER TABLE [Borrower] ADD CONSTRAINT [Borrower_fk1] FOREIGN KEY ([Club_Name]) REFERENCES [Clubs]([Club_Name]) ON UPDATE CASCADE;
ALTER TABLE [Borrower] ADD CONSTRAINT [Borrower_fk2] FOREIGN KEY ([Student_ID]) REFERENCES [Students]([Student_ID]) ON UPDATE CASCADE;

ALTER TABLE [EventClub] ADD CONSTRAINT [EventClub_fk0] FOREIGN KEY ([Event_ID]) REFERENCES [Events]([Event_ID]) ON UPDATE CASCADE;
ALTER TABLE [EventClub] ADD CONSTRAINT [EventClub_fk1] FOREIGN KEY ([Club_Name]) REFERENCES [Clubs]([Club_Name]) ON UPDATE CASCADE;

ALTER TABLE [Club_member] ADD CONSTRAINT [Club_member_fk0] FOREIGN KEY ([Club_Name]) REFERENCES [Clubs]([Club_Name]) ON UPDATE CASCADE;
ALTER TABLE [Club_member] ADD CONSTRAINT [Club_member_fk1] FOREIGN KEY ([Student_ID]) REFERENCES [Students]([Student_ID]) ON UPDATE CASCADE;
ALTER TABLE [Club_member] ADD CONSTRAINT [Club_member_fk2] FOREIGN KEY ([Team_ID]) REFERENCES [Teams]([Team_ID]) ON UPDATE CASCADE;

ALTER TABLE [Club_Funds_Tracker] ADD CONSTRAINT [Club_Funds_Tracker_fk0] FOREIGN KEY ([Club_Name]) REFERENCES [Clubs]([Club_Name]) ON UPDATE CASCADE;

ALTER TABLE [EventFeedback] ADD CONSTRAINT [EventFeedback_fk0] FOREIGN KEY ([Event_ID]) REFERENCES [Events]([Event_ID]) ON UPDATE CASCADE;
ALTER TABLE [EventFeedback] ADD CONSTRAINT [EventFeedback_fk1] FOREIGN KEY ([Student_ID]) REFERENCES [Students]([Student_ID]) ON UPDATE CASCADE;
