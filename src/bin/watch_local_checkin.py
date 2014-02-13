###########################################################
#
# Copyright (c) 2014, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['WatchLocalRepoCmd']

import tacticenv

import threading
import time
import os

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
#from watch_folder import BaseLoggingEventHandler

class CheckinLoggingEventHandler(LoggingEventHandler):

    def on_created(self, event):
        return

    def on_modified(self, event):
        return



    def on_moved(self, event):
        #base_dir = server.get_base_dirs().get("linux_local_repo_dir")
        # use watch folder to upload paths
        #for path in repo_paths:
        #    server.upload_file(path, base_dir=base_dir)

        src_path = event.src_path
        dest_path = event.dest_path

        if src_path.endswith(".temp"):
            try:
                PATHS.append(dest_path)
                print "ADDED PATHS: ", PATHS
            except Exception, e:
                print "Error: ", e



    def upload_file(self, path):
        from tactic_client_lib import TacticServerStub
        server = TacticServerStub.get(protocol="xmlrpc")

        path = path.replace("\\", "/")
        print "Uploading file: ", path

        if os.name == 'nt':
            base_dir = server.get_base_dirs().get("win32_local_repo_dir")
        else:
            base_dir = server.get_base_dirs().get("linux_local_repo_dir")
        # use watch folder to upload paths
        server.upload_file(path, base_dir=base_dir)

        ticket = server.get_transaction_ticket()

        rel_path = path.replace("%s/" % base_dir, "")

        # notify the server
        command = 'spt.tools.watch_folder.watch_server_checkin.NotifyFileUploadCmd'
        kwargs = {
                'ticket': ticket,
                'base_dir': base_dir,
                'rel_path': rel_path,
                'path': path
        }

        try:
            server.execute_cmd(command, kwargs)

            # delete the file
            # TODO: maybe this needs to moved to a local repo, but right now
            # any file that is in this folder will be uploaded
            os.unlink(path)

        except Exception, e:
            print "ERORR processing [%s]" % path
            print "ERROR: ", e



PATHS = []
class WatchFolderUploadThread(threading.Thread):

    def run(my):
        paths = PATHS
        event_handler = CheckinLoggingEventHandler()
        while 1:
            try:
                path = paths.pop(0)
            except IndexError:
                time.sleep(1)
                continue

            try:
                base, ext = os.path.splitext(path)
                locked_path = "%s.locked" % base

                # if there already is a locked file, then skip this one because
                # is being uploaded
                if os.path.exists(locked_path):
                    continue

                #self.upload_file(dest_path)
                f = open( locked_path, "w")
                f.close()

                print "uploading path: ", path
                event_handler.upload_file(path)
                #time.sleep(10)
                #os.unlink(path)
            finally:
                os.unlink( locked_path )

 

class WatchLocalRepoCmd(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        project = kwargs.get("project")
        server = kwargs.get("server")
        ticket = kwargs.get("ticket")

        if project:
            os.environ['TACTIC_PROJECT'] = project
        if server:
            os.environ['TACTIC_SERVER'] = server
        if ticket:
            os.environ['TACTIC_TICKET'] = ticket


        self.observer = None


    def start(self):
        from tactic_client_lib import TacticServerStub
        server = TacticServerStub.get(protocol="xmlrpc")
        base_dirs = server.get_base_dirs()
        if os.name == "nt":
            repo_dir = base_dirs.get("win32_local_repo_dir")
        else:
            repo_dir = base_dirs.get("linux_local_repo_dir")
            #repo_dir = "/tmp/sthpw"

        if not os.path.exists(repo_dir):
            os.makedirs(repo_dir)


        event_handler = CheckinLoggingEventHandler()

        print "repo_dir: ", repo_dir

        # upload all files in this folder
        for root, dirnames, basenames in os.walk(repo_dir):
            for basename in basenames:
                tmp, ext = os.path.splitext(basename)
                if ext in ['.temp', 'locked']:
                    continue
                full_path = "%s/%s" % (root, basename)
                print "path: ", full_path
                PATHS.append(full_path)
                #event_handler.upload_file(full_path)

        upload = WatchFolderUploadThread()
        upload.daemon = True
        upload.start()


        print "---"
        from watchdog.observers import Observer
        self.observer = Observer()
        self.observer.schedule(event_handler, path=repo_dir, recursive=True)
        self.observer.start()


    def stop(self):
        self.observer.stop()



    def main(self):
        self.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print "KEYBOARD BREAK"
            self.stop()


def main():
    WatchLocalRepoCmd().main()


if __name__ == "__main__":
    ticket = 'b22bf1c42424708b55ec775751cd0eab'
    os.environ['TACTIC_SERVER'] = '192.168.1.96'
    os.environ['TACTIC_TICKET'] = ticket


    main()




