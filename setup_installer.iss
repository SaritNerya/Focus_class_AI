; התקנת Windows ללקוח (צד תלמידה) בעזרת Inno Setup.
; לפני ההרצה יש לבנות את ה-exe מתוך client/main.py, לדוגמה:
;   pyinstaller --name main --onefile --noconsole client/main.py
; זה מייצר dist\main.exe, שהוא הקובץ שסקריפט זה אורז ומתקין.
[Setup]
AppName=FocusClass
AppVersion=1.0
DefaultDirName={autopf}\FocusClass
OutputDir=Output
OutputBaseFilename=Setup_FocusClass
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion

Source: "dependencies\UnityCaptureFilter32.dll"; DestDir: "{app}"
Source: "dependencies\UnityCaptureFilter64.dll"; DestDir: "{app}"

[Run]
Filename: "{sys}\regsvr32.exe"; Parameters: "/s ""{app}\UnityCaptureFilter32.dll"""; Flags: runhidden waituntilterminated
Filename: "{sys}\regsvr32.exe"; Parameters: "/s ""{app}\UnityCaptureFilter64.dll"""; Flags: runhidden waituntilterminated

Filename: "{app}\main.exe"; Description: "הפעל את FocusClass"; Flags: nowait postinstall skipifsilent

[Icons]
Name: "{autoprograms}\FocusClass"; Filename: "{app}\main.exe"