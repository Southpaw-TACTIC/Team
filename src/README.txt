Welcome to TACTIC TEAM
-------------------------------------------------------

You can use one of the 2 methods to access TACTIC:

1. Double-click on the TACTIC 4.3 icon on your desktop to start the server and client at the same time.

2. To connect to TACTIC TEAM through a regular browser like Firefox or Chrome, you can use the following URL:

    http://127.0.0.1:9123/tactic/


On first start-up, you will be asked to set the password for the user "admin", which has the highest access level to TACTIC for administration. In Windows Task Manager, you will see a process running as TACTIC Server.exe. This is the server. If you are using the Desktop client, you will also see a TACTIC.exe process. 



Connection from muliple clients
-------------------------------------------------------

To start it in a way where other people in your internal network can connect to it, you can follow these steps:
1. In Windows, type in ipconfig and for instance you find that your IP is 192.168.139.1:

2. In Command Prompt, cd to the bin folder of TACTIC:

C:\Program Files (x86)\TACTIC 4.3\bin>"../python/python" startup_standalone.py -
p 9000 -s 192.168.139.1
 

Now, other users can then connect to your TACTIC TEAM using the URL
http://192.168.139.1:9000/tactic
 
The TACTIC Server process only appears if it is started through double clicking the icon on the desktop, but that is currently hardcoded to start locally in 127.0.0.1:9123 for easy self-running setup. This will be improved in the future.

For connections across the internet or a larger scale usage, TACTIC Enterprise is recommended as it involves the installation of a Web Server. 

Developer
-------------------------------------------------------
1. If the TACTIC TEAM server is shut down, you can start it by running:

   "C:\Program Files (x86)\TACTIC 4.3\python\python" startup_standalone.py 
   
It is vital to use the python in this particular directory. 

2. To start the TACTIC TEAM Desktop client on its own, you can double-click on
the TACTIC Client.bat file in C:\Program Files (x86)\TACTIC 4.3

