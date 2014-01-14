Set sh = CreateObject("WScript.Shell")
Set fs = CreateObject("Scripting.FileSystemObject")
ex = fs.GetParentFolderName(Wscript.ScriptFullName)
sh.CurrentDirectory = ex
ex = ex & "\TACTIC Server.bat"
sh.Run chr(34) & ex & Chr(34)
Set sh = Nothing
