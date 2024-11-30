@echo off
sqlcmd -S localhost -U sa -P Larocca@1234 -i create_user_table.sql
pause
