USE master;
GO

-- Drop database safely if exists (avoid "in use" error)
IF DB_ID('SRMS_DB') IS NOT NULL
BEGIN
    ALTER DATABASE SRMS_DB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE SRMS_DB;
END
GO

CREATE DATABASE SRMS_DB;
GO

USE SRMS_DB;
GO

-- =============================================
-- 0. CLEANUP (drop objects if exist)
-- =============================================

-- Drop procedures if exist (to avoid "already exists")
IF OBJECT_ID('dbo.sp_OpenKeys', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_OpenKeys;
-- HERE IS THE CHANGE: Renamed to usp_AddUser
IF OBJECT_ID('dbo.usp_AddUser', 'P') IS NOT NULL DROP PROCEDURE dbo.usp_AddUser;
IF OBJECT_ID('dbo.sp_Login', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_Login;

IF OBJECT_ID('dbo.sp_ViewStudents', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_ViewStudents;
IF OBJECT_ID('dbo.sp_GetAverageGrade', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_GetAverageGrade;
IF OBJECT_ID('dbo.sp_GetStudentGrades', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_GetStudentGrades;
IF OBJECT_ID('dbo.sp_InsertGrade', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_InsertGrade;
IF OBJECT_ID('dbo.sp_GetStudentAttendance', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_GetStudentAttendance;
IF OBJECT_ID('dbo.sp_UpdateAttendance', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_UpdateAttendance;
IF OBJECT_ID('dbo.sp_GetAllUsers', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_GetAllUsers;
IF OBJECT_ID('dbo.sp_UpdateCourseDescription', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_UpdateCourseDescription;
GO

-- Drop trigger if exist
IF OBJECT_ID('dbo.trg_FlowControl_Course_Update', 'TR') IS NOT NULL
    DROP TRIGGER dbo.trg_FlowControl_Course_Update;
GO

-- Drop roles if exist
IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'AdminRole') DROP ROLE AdminRole;
IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'InstructorRole') DROP ROLE InstructorRole;
IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'TARole') DROP ROLE TARole;
IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'StudentRole') DROP ROLE StudentRole;
IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'GuestRole') DROP ROLE GuestRole;
GO

-- Drop tables in FK-safe order
IF OBJECT_ID('dbo.Attendance', 'U') IS NOT NULL DROP TABLE dbo.Attendance;
IF OBJECT_ID('dbo.Grades', 'U') IS NOT NULL DROP TABLE dbo.Grades;
IF OBJECT_ID('dbo.Course', 'U') IS NOT NULL DROP TABLE dbo.Course;
IF OBJECT_ID('dbo.Instructor', 'U') IS NOT NULL DROP TABLE dbo.Instructor;
IF OBJECT_ID('dbo.Student', 'U') IS NOT NULL DROP TABLE dbo.Student;
IF OBJECT_ID('dbo.Users', 'U') IS NOT NULL DROP TABLE dbo.Users;
GO

-- Drop Symmetric key / Certificate / Master key if exist
IF EXISTS (SELECT * FROM sys.symmetric_keys WHERE name = 'SRMS_Key_AES256')
    DROP SYMMETRIC KEY SRMS_Key_AES256;
GO

IF EXISTS (SELECT * FROM sys.certificates WHERE name = 'SRMS_Cert')
    DROP CERTIFICATE SRMS_Cert;
GO

IF EXISTS (SELECT * FROM sys.symmetric_keys WHERE name = '##MS_DatabaseMasterKey##')
    DROP MASTER KEY;
GO


-- =============================================
-- 1. ENCRYPTION SETUP (AES_256)
-- =============================================
CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'StrongMasterKeyPassword123!';
GO

CREATE CERTIFICATE SRMS_Cert WITH SUBJECT = 'SRMS Data Encryption';
GO

CREATE SYMMETRIC KEY SRMS_Key_AES256
    WITH ALGORITHM = AES_256
    ENCRYPTION BY CERTIFICATE SRMS_Cert;
GO

-- Open Key Helper Procedure (Application must call this)
CREATE PROCEDURE sp_OpenKeys
AS
BEGIN
    OPEN SYMMETRIC KEY SRMS_Key_AES256 DECRYPTION BY CERTIFICATE SRMS_Cert;
END;
GO


-- =============================================
-- 2. SCHEMA DEFINITION
-- =============================================

CREATE TABLE Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    Username NVARCHAR(50) UNIQUE NOT NULL,
    Username_Enc VARBINARY(MAX), 
    Username_Hash AS CHECKSUM(Username_Enc),
    PasswordHash VARBINARY(64) NOT NULL,
    UserRole NVARCHAR(20) NOT NULL CHECK (UserRole IN ('Admin', 'Instructor', 'TA', 'Student', 'Guest')),
    ClearanceLevel INT NOT NULL CHECK (ClearanceLevel BETWEEN 1 AND 4)
);
GO

CREATE TABLE Student (
    StudentID INT IDENTITY(1,1) PRIMARY KEY,
    FullName_Enc VARBINARY(MAX),
    Email_Enc VARBINARY(MAX),
    Phone_Enc VARBINARY(MAX),
    DOB_Enc VARBINARY(MAX),
    Department NVARCHAR(50),
    ClearanceLevel INT DEFAULT 2
);
GO

CREATE TABLE Instructor (
    InstructorID INT IDENTITY(1,1) PRIMARY KEY,
    FullName_Enc VARBINARY(MAX),
    Email_Enc VARBINARY(MAX),
    ClearanceLevel INT DEFAULT 3
);
GO

CREATE TABLE Course (
    CourseID INT IDENTITY(1,1) PRIMARY KEY,
    CourseName NVARCHAR(100),
    Description NVARCHAR(MAX),
    PublicInfo NVARCHAR(MAX),
    SecurityLevel INT DEFAULT 1
);
GO

CREATE TABLE Grades (
    GradeID INT IDENTITY(1,1) PRIMARY KEY,
    StudentID INT FOREIGN KEY REFERENCES Student(StudentID),
    CourseID INT FOREIGN KEY REFERENCES Course(CourseID),
    GradeValue_Enc VARBINARY(MAX),
    DateEntered DATETIME DEFAULT GETDATE(),
    SecurityLevel INT DEFAULT 3
);
GO

CREATE TABLE Attendance (
    AttendanceID INT IDENTITY(1,1) PRIMARY KEY,
    StudentID INT FOREIGN KEY REFERENCES Student(StudentID),
    CourseID INT FOREIGN KEY REFERENCES Course(CourseID),
    Status BIT,
    DateRecorded DATETIME,
    SecurityLevel INT DEFAULT 3
);
GO


-- =============================================
-- 4. ACCESS CONTROL (RBAC) & PROCEDURES
-- =============================================

-- HERE IS THE CHANGE: Renamed to usp_AddUser to avoid system proc collision
CREATE PROCEDURE usp_AddUser
    @Username NVARCHAR(50),
    @Password NVARCHAR(50),
    @Role NVARCHAR(20),
    @Clearance INT
AS
BEGIN
    OPEN SYMMETRIC KEY SRMS_Key_AES256 DECRYPTION BY CERTIFICATE SRMS_Cert;
    
    INSERT INTO Users (Username, Username_Enc, PasswordHash, UserRole, ClearanceLevel)
    VALUES (
        @Username,
        EncryptByKey(Key_GUID('SRMS_Key_AES256'), @Username),
        HASHBYTES('SHA2_512', @Password),
        @Role,
        @Clearance
    );
    
    CLOSE SYMMETRIC KEY SRMS_Key_AES256;
END;
GO

CREATE PROCEDURE sp_Login
    @Username NVARCHAR(50),
    @Password NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    OPEN SYMMETRIC KEY SRMS_Key_AES256 DECRYPTION BY CERTIFICATE SRMS_Cert;

    DECLARE @UserID INT;
    DECLARE @Role NVARCHAR(20);
    DECLARE @Clearance INT;

    SELECT TOP 1 
        @UserID = UserID, 
        @Role = UserRole, 
        @Clearance = ClearanceLevel
    FROM Users
    WHERE CONVERT(NVARCHAR(50), DecryptByKey(Username_Enc)) = @Username
      AND PasswordHash = HASHBYTES('SHA2_512', @Password);

    IF @UserID IS NOT NULL
        SELECT @UserID AS UserID, @Role AS Role, @Clearance AS Clearance;
    ELSE
        SELECT -1 AS UserID, 'Failed' AS Role, 0 AS Clearance;
    
    CLOSE SYMMETRIC KEY SRMS_Key_AES256;
END;
GO


-- =============================================
-- 5. MLS & INFERENCE CONTROL VIEWS (Procedures)
-- =============================================

CREATE PROCEDURE sp_ViewStudents
    @RequestorClearance INT
AS
BEGIN
    OPEN SYMMETRIC KEY SRMS_Key_AES256 DECRYPTION BY CERTIFICATE SRMS_Cert;

    IF @RequestorClearance < 2
    BEGIN
        SELECT 'Access Denied: Insufficient Clearance' AS Error;
        CLOSE SYMMETRIC KEY SRMS_Key_AES256;
        RETURN;
    END

    SELECT 
        StudentID,
        CONVERT(NVARCHAR(100), DecryptByKey(FullName_Enc)) AS FullName,
        CONVERT(NVARCHAR(100), DecryptByKey(Email_Enc)) AS Email,
        Department
    FROM Student;
    
    CLOSE SYMMETRIC KEY SRMS_Key_AES256;
END;
GO

CREATE PROCEDURE sp_GetAverageGrade
    @CourseID INT,
    @RequestorRole NVARCHAR(20)
AS
BEGIN
    OPEN SYMMETRIC KEY SRMS_Key_AES256 DECRYPTION BY CERTIFICATE SRMS_Cert;
    
    DECLARE @Count INT;
    SELECT @Count = COUNT(*) FROM Grades WHERE CourseID = @CourseID;

    IF @Count < 3
        SELECT NULL AS AverageGrade, 'Query Set Size Violation: Too few records' AS Warning;
    ELSE
        SELECT AVG(CAST(CONVERT(NVARCHAR(20), DecryptByKey(GradeValue_Enc)) AS DECIMAL(5,2))) AS AverageGrade
        FROM Grades
        WHERE CourseID = @CourseID;

    CLOSE SYMMETRIC KEY SRMS_Key_AES256;
END;
GO

CREATE PROCEDURE sp_GetStudentGrades
    @StudentID INT
AS
BEGIN
    OPEN SYMMETRIC KEY SRMS_Key_AES256 DECRYPTION BY CERTIFICATE SRMS_Cert;

    SELECT 
        C.CourseName,
        CONVERT(NVARCHAR(20), DecryptByKey(G.GradeValue_Enc)) AS Grade,
        G.DateEntered
    FROM Grades G
    JOIN Course C ON G.CourseID = C.CourseID
    WHERE G.StudentID = @StudentID;

    CLOSE SYMMETRIC KEY SRMS_Key_AES256;
END;
GO

CREATE PROCEDURE sp_InsertGrade
    @InstructorID INT,
    @StudentID INT,
    @CourseID INT,
    @GradeValue NVARCHAR(10)
AS
BEGIN
    OPEN SYMMETRIC KEY SRMS_Key_AES256 DECRYPTION BY CERTIFICATE SRMS_Cert;
    
    INSERT INTO Grades (StudentID, CourseID, GradeValue_Enc, DateEntered, SecurityLevel)
    VALUES (
        @StudentID, 
        @CourseID, 
        EncryptByKey(Key_GUID('SRMS_Key_AES256'), @GradeValue),
        GETDATE(),
        3
    );

    CLOSE SYMMETRIC KEY SRMS_Key_AES256;
END;
GO


-- =============================================
-- 6. FLOW CONTROL (No Write Down)
-- =============================================
CREATE TRIGGER trg_FlowControl_Course_Update
ON Course
FOR UPDATE
AS
BEGIN
    RETURN;
END;
GO

CREATE PROCEDURE sp_GetStudentAttendance
    @StudentID INT
AS
BEGIN
    SELECT 
        C.CourseName,
        CASE A.Status WHEN 1 THEN 'Present' ELSE 'Absent' END AS Status,
        A.DateRecorded
    FROM Attendance A
    JOIN Course C ON A.CourseID = C.CourseID
    WHERE A.StudentID = @StudentID;
END;
GO

CREATE PROCEDURE sp_UpdateAttendance
    @StudentID INT,
    @CourseID INT,
    @Status BIT,
    @DateRecorded DATETIME
AS
BEGIN
    INSERT INTO Attendance (StudentID, CourseID, Status, DateRecorded, SecurityLevel)
    VALUES (@StudentID, @CourseID, @Status, @DateRecorded, 3);
END;
GO

CREATE PROCEDURE sp_GetAllUsers
AS
BEGIN
    OPEN SYMMETRIC KEY SRMS_Key_AES256 DECRYPTION BY CERTIFICATE SRMS_Cert;
    
    SELECT 
        UserID,
        CONVERT(NVARCHAR(50), DecryptByKey(Username_Enc)) AS Username,
        UserRole,
        ClearanceLevel
    FROM Users;

    CLOSE SYMMETRIC KEY SRMS_Key_AES256;
END;
GO

CREATE PROCEDURE sp_UpdateCourseDescription
    @UserId INT,
    @CourseID INT,
    @NewDesc NVARCHAR(MAX)
AS
BEGIN
    DECLARE @UserClearance INT;
    SELECT @UserClearance = ClearanceLevel FROM Users WHERE UserID = @UserId;
    
    DECLARE @ObjectSecurity INT;
    SELECT @ObjectSecurity = SecurityLevel FROM Course WHERE CourseID = @CourseID;

    IF @UserClearance > @ObjectSecurity
    BEGIN
        THROW 51000, 'Flow Control Violation: No Write Down (User Clearance > Object Level)', 1;
        RETURN;
    END

    UPDATE Course SET Description = @NewDesc WHERE CourseID = @CourseID;
END;
GO


-- =============================================
-- 4.1 SQL SERVER ROLES (RBAC)  (moved AFTER procs exist)
-- =============================================
CREATE ROLE AdminRole;
CREATE ROLE InstructorRole;
CREATE ROLE TARole;
CREATE ROLE StudentRole;
CREATE ROLE GuestRole;
GO

GRANT SELECT ON Course TO GuestRole;
DENY SELECT ON Student TO GuestRole;
DENY SELECT ON Instructor TO GuestRole;
DENY SELECT ON Grades TO GuestRole;
DENY SELECT ON Attendance TO GuestRole;
DENY SELECT ON Users TO GuestRole;
GO

GRANT EXECUTE ON sp_Login TO StudentRole;
GRANT EXECUTE ON sp_ViewStudents TO StudentRole;
GRANT EXECUTE ON sp_GetStudentGrades TO StudentRole;
GRANT EXECUTE ON sp_GetStudentAttendance TO StudentRole;
DENY SELECT ON Grades TO StudentRole;
DENY SELECT ON Attendance TO StudentRole;
DENY UPDATE ON Student TO StudentRole;
GO

GRANT EXECUTE ON sp_Login TO TARole;
GRANT EXECUTE ON sp_ViewStudents TO TARole;
GRANT EXECUTE ON sp_UpdateAttendance TO TARole;
GRANT EXECUTE ON sp_GetStudentAttendance TO TARole;
GRANT SELECT ON Course TO TARole;
DENY SELECT ON Grades TO TARole;
DENY EXECUTE ON sp_InsertGrade TO TARole;
GO

GRANT EXECUTE ON sp_Login TO InstructorRole;
GRANT EXECUTE ON sp_ViewStudents TO InstructorRole;
GRANT EXECUTE ON sp_InsertGrade TO InstructorRole;
GRANT EXECUTE ON sp_GetAverageGrade TO InstructorRole;
GRANT EXECUTE ON sp_GetStudentAttendance TO InstructorRole;
GRANT EXECUTE ON sp_UpdateAttendance TO InstructorRole;
GRANT SELECT ON Course TO InstructorRole;
DENY DELETE ON Grades TO InstructorRole;
GO

-- HERE IS THE CHANGE: Renamed to usp_AddUser
GRANT EXECUTE ON dbo.usp_AddUser TO AdminRole;
GRANT EXECUTE ON dbo.sp_GetAllUsers TO AdminRole;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Student TO AdminRole;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Instructor TO AdminRole;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Course TO AdminRole;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Grades TO AdminRole;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Attendance TO AdminRole;
GRANT SELECT, UPDATE ON dbo.Users TO AdminRole;
GO


-- =============================================
-- 7. SEED DATA
-- =============================================
-- HERE IS THE CHANGE: Calling usp_AddUser instead of sp_AddUser
EXEC usp_AddUser 'admin', 'admin123', 'Admin', 4;
EXEC usp_AddUser 'inst1', 'pass123', 'Instructor', 3;
EXEC usp_AddUser 'ta1', 'pass123', 'TA', 2;
EXEC usp_AddUser 'std1', 'pass123', 'Student', 2;
EXEC usp_AddUser 'guest1', 'pass123', 'Guest', 1;
GO

INSERT INTO Course (CourseName, Description, PublicInfo, SecurityLevel) 
VALUES ('CS101', 'Intro to CS', 'Syllabus available', 1);
GO

OPEN SYMMETRIC KEY SRMS_Key_AES256 DECRYPTION BY CERTIFICATE SRMS_Cert;

INSERT INTO Student (FullName_Enc, Email_Enc, Department, ClearanceLevel)
VALUES 
(EncryptByKey(Key_GUID('SRMS_Key_AES256'), 'John Doe'), EncryptByKey(Key_GUID('SRMS_Key_AES256'), 'john@test.com'), 'CS', 2),
(EncryptByKey(Key_GUID('SRMS_Key_AES256'), 'Jane Smith'), EncryptByKey(Key_GUID('SRMS_Key_AES256'), 'jane@test.com'), 'CS', 2),
(EncryptByKey(Key_GUID('SRMS_Key_AES256'), 'Bob Alice'), EncryptByKey(Key_GUID('SRMS_Key_AES256'), 'bob@test.com'), 'CS', 2);

CLOSE SYMMETRIC KEY SRMS_Key_AES256;
GO

-- HERE IS THE CHANGE: Renamed to usp_AddUser
GRANT EXECUTE ON dbo.usp_AddUser TO AdminRole;
GO



USE SRMS_DB;
GO

SELECT UserID, UserRole, ClearanceLevel
FROM Users;





USE SRMS_DB;
GO
-- هاتلي كل المستخدمين ورتبهم من الأحدث للأقدم
SELECT * FROM Users ORDER BY UserID DESC;