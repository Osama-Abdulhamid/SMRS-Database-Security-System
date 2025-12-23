USE SRMS_DB;
GO

-- =============================================
-- PART B: ROLE REQUEST WORKFLOW
-- =============================================

-- 1. Create Role Requests Table
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[RoleRequests]'))
    DROP TABLE RoleRequests;
GO

CREATE TABLE RoleRequests (
    RequestID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT NOT NULL FOREIGN KEY REFERENCES Users(UserID),
    CurrentRole NVARCHAR(20),
    RequestedRole NVARCHAR(20),
    Reason NVARCHAR(MAX),
    RequestStatus NVARCHAR(20) DEFAULT 'Pending' CHECK (RequestStatus IN ('Pending', 'Approved', 'Denied')),
    RequestDate DATETIME DEFAULT GETDATE(),
    AdminComments NVARCHAR(MAX)
);
GO

-- 2. Procedure: Student Submits Request
-- CHANGE: Renamed to usp_SubmitRoleRequest to match Part A convention
CREATE PROCEDURE usp_SubmitRoleRequest
    @UserID INT,
    @RequestedRole NVARCHAR(20),
    @Reason NVARCHAR(MAX)
AS
BEGIN
    DECLARE @CurrentRole NVARCHAR(20);
    SELECT @CurrentRole = UserRole FROM Users WHERE UserID = @UserID;
    
    -- Basic validation
    IF @CurrentRole = @RequestedRole
    BEGIN
        THROW 50001, 'Cannot request upgrade to same role.', 1;
        RETURN;
    END

    INSERT INTO RoleRequests (UserID, CurrentRole, RequestedRole, Reason)
    VALUES (@UserID, @CurrentRole, @RequestedRole, @Reason);
END;
GO

-- 3. Procedure: Admin Reviews Request (Approve/Deny)
-- CHANGE: Renamed to usp_ProcessRoleRequest to match Part A convention
CREATE PROCEDURE usp_ProcessRoleRequest
    @RequestID INT,
    @AdminUserID INT, -- To verify Admin performed it
    @Action NVARCHAR(10), -- 'Approve' or 'Deny'
    @Comments NVARCHAR(MAX) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Verify Admin
    DECLARE @AdminRole NVARCHAR(20);
    SELECT @AdminRole = UserRole FROM Users WHERE UserID = @AdminUserID;
    
    IF @AdminRole <> 'Admin'
    BEGIN
        THROW 50002, 'Only Admins can process requests.', 1;
        RETURN;
    END

    -- Get Request Details
    DECLARE @TargetUserID INT;
    DECLARE @NewRole NVARCHAR(20);
    DECLARE @CurrentStatus NVARCHAR(20);
    
    SELECT @TargetUserID = UserID, @NewRole = RequestedRole, @CurrentStatus = RequestStatus
    FROM RoleRequests WHERE RequestID = @RequestID;

    IF @CurrentStatus <> 'Pending'
    BEGIN
        THROW 50003, 'Request is not Pending.', 1;
        RETURN;
    END

    IF @Action = 'Approve'
    BEGIN
        UPDATE RoleRequests 
        SET RequestStatus = 'Approved', AdminComments = @Comments
        WHERE RequestID = @RequestID;
        
        -- Update User Role actual
        -- Also need to upgrade Clearance probably? 
        -- Mapping: Admin(4), Instructor(3), TA(2), Student(2), Guest(1)
        DECLARE @NewClearance INT;
        SET @NewClearance = CASE @NewRole
            WHEN 'Admin' THEN 4
            WHEN 'Instructor' THEN 3
            WHEN 'TA' THEN 2
            WHEN 'Student' THEN 2
            ELSE 1
        END;

        UPDATE Users 
        SET UserRole = @NewRole, ClearanceLevel = @NewClearance
        WHERE UserID = @TargetUserID;
    END
    ELSE IF @Action = 'Deny'
    BEGIN
        UPDATE RoleRequests 
        SET RequestStatus = 'Denied', AdminComments = @Comments
        WHERE RequestID = @RequestID;
    END
END;
GO


SELECT name
FROM sys.procedures
ORDER BY name;
