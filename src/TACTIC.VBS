
if WScript.Arguments.Count = 1 then
    url = WScript.Arguments(0)
else
	url = ""
end if

Set sh = CreateObject("WScript.Shell")
Set fs = CreateObject("Scripting.FileSystemObject")

ex = fs.GetParentFolderName(Wscript.ScriptFullName)

sh.CurrentDirectory = ex
ex = ex & "\TACTIC.bat"
ws = chr(34) & ex & chr(34) & chr(32) & url 

sh.Run ws , 0
Set sh = Nothing
