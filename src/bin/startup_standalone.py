###########################################################
#
# Copyright (c) 2011, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['Tactic', 'tactic_test']

import os, sys
# set up environment
os.environ['TACTIC_APP_SERVER'] = "cherrypy"
os.environ['TACTIC_MODE'] = "production"
# set it so that the temp directories are cleaned up
os.environ['TACTIC_CLEANUP'] = "true"

import tacticenv

tactic_install_dir = tacticenv.get_install_dir()
tactic_site_dir = tacticenv.get_site_dir()


sys.path.insert(0, "%s/src" % tactic_install_dir)
sys.path.insert(0, "%s/tactic_sites" % tactic_install_dir)
sys.path.insert(0, tactic_site_dir)
sys.path.insert(0, "%s/3rd_party/CherryPy" % tactic_install_dir)


from pyasm.common import Environment, Config

class TacticStartup(object):

    def __init__(my, **kwargs):
        my.kwargs = kwargs
        my.is_started = False
        my.thread = None

    def execute(my):
        hostname = my.kwargs.get("hostname")
        if not hostname:
            hostname = Config.get_value("install", "hostname")

        port = my.kwargs.get("port")
        if not port:
            port = Config.get_value("install", "port")
        if not port:
            port = 9123
        else:
            port = int(port)

        do_startup(port, server=hostname)

    def execute_thread(my):
        if my.is_started:
            return

        import threading
        my.thread = threading.Thread(None, my.execute)
        my.thread.setDaemon(True)
        my.thread.start()

        my.is_started = True



    def stop_thread(my):
        my.thread.stop()




    def upgrade(my):

        # Note this should only be called when the database is local ...
        # for now, just sqlite database
        vendor = Config.get_value("database", "vendor")
        if vendor != 'Sqlite':
            return
        

        version = Environment.get_release_version()
        print "Upgrade database to version [%s] ..." % version

        import sys
        #path = __file__
        #dirname = os.path.dirname(path)
        #path = "%s/upgrade.py" % dirname
        dir = os.getcwd()
        file_path = sys.modules[__name__].__file__
        full_path = os.path.join(dir, file_path)
        dirname = os.path.dirname(full_path)
        # take another directory off
        dirname = os.path.dirname(dirname)
        if os.name == 'posix':
            executable = "%s/python/bin/python" % dirname
        else:
            executable = "%s/python/python.exe" % dirname
        #print 'exec: ', executable

        install_dir = tacticenv.get_install_dir()
        path = "%s/src/bin/upgrade_db.py" % install_dir

        import subprocess
        subprocess.call([executable, path , "-f", "-y"])
        print "... done upgrade"



def do_startup(port, server=""):

    #from tactic.startup import FirstRunInit
    #cmd = FirstRunInit()
    #cmd.execute()

    if os.name != 'nt' and os.getuid() == 0:
        print 
        print "You should not run this as root. Run it as the Web server process's user. e.g. apache"
        print
	return

    thread_count = Config.get_value("services", "thread_count") 
    

    if not thread_count:
        thread_count = 10
    else: 
        thread_count = int(thread_count)


    from pyasm.web.cherrypy30_startup import CherryPyStartup
    startup = CherryPyStartup()

    startup.set_config('global', 'server.socket_port', port)

    startup.set_config('global', 'server.socket_queue_size', 100)
    startup.set_config('global', 'server.thread_pool', thread_count)
    #startup.set_config('global', 'server.socket_host', server)

    #startup.set_config('global', 'log.screen', True)

    startup.set_config('global', 'request.show_tracebacks', True)
    startup.set_config('global', 'server.log_unhandled_tracebacks', True)

    startup.set_config('global', 'engine.autoreload_on', True)




    hostname = None
    server_default = '127.0.0.1'

    if not server:
        hostname = Config.get_value("install", "hostname") 
        if hostname == 'localhost':
            # swap it to IP to suppress CherryPy Warning
            hostname = server_default
        if hostname:
            # special host name for IIS which can't load balance across many
            # ports with the same service
            hostname = hostname.replace("{port}", str(port))
            server = hostname
        else:
            server = server_default
       
    startup.set_config('global', 'server.socket_host', server)

    startup.execute()





def Tactic(**kwargs):
    from tactic.startup import FirstRunInit
    cmd = FirstRunInit()
    cmd.execute()

    # start as a separate thread
    startup = TacticStartup(**kwargs)
    startup.upgrade()
    startup.execute_thread()
    #startup.execute()

    return startup




def tactic_test():

    tactic = Tactic()

    # issue TACTIC commands
    count = 0
    while 1:
        print count
        count +=1
        import time
        time.sleep(10)

        try:
            #server = TacticServerStub(protocol="local")

            print tactic.ping()
            print tactic.query("sthpw/login")

        except Exception, e:
            print "ERROR: ", e




if __name__ == '__main__':

    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:s:", ["port=","server="])
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)

    kwargs = {}
    for o, a in opts:
        if o == "-p":
            kwargs['port'] = a
        elif o == '-s':
            kwargs['hostname'] = a

    #tactic_test()
    Tactic(**kwargs)
    while 1:
        import time
        time.sleep(10)
    print "exiting ...."



