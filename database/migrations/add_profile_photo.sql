-- Check if column doesn't exist before adding
IF NOT EXISTS (
    SELECT * 
    FROM sys.columns 
    WHERE object_id = OBJECT_ID('time') AND name = 'profile_photo'
)
BEGIN
    ALTER TABLE [time] 
    ADD profile_photo NVARCHAR(255) NULL 
    CONSTRAINT DF_Time_ProfilePhoto DEFAULT 'default_profile.png'
END
