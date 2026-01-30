MsgBox "El VBS se ejecutó correctamente"
Set shell = CreateObject("WScript.Shell")
shell.Run """G:\Escri\tickets\api.bat""", 0
