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

__all__ = ['PythonApplet']

import tacticenv
from pyasm.common import Config, Common, ZipUtil


import sys, os, shutil, hashlib
import json
import urllib
import time
from PySide import QtCore, QtGui, QtWebKit, QtNetwork



class PythonApplet(QtCore.QObject):

    @QtCore.Slot(str)  
    def show_message(self, msg):  
        '''Open a message box and display the specified message.'''
        QtGui.QMessageBox.information(None, "Info", msg)


    @QtCore.Slot(str)
    def set_ticket(my, ticket):
        my.setProperty("ticket", ticket)


    @QtCore.Slot(str)
    def execute(my, cmd):
        # FIXME: should use subprocess
        os.system(cmd)

    @QtCore.Slot(str)
    def execute_shell(my, cmd):
        # FIXME: should use subprocess
        os.system(cmd)


    @QtCore.Slot(str, str, result=str)
    def execute_python_cmd(my, class_name, kwargs):
        import sys
        exec_class_name = 'tactic_client_lib.scm.CmdWrapper'
        kwargs = json.loads(kwargs)
        kwargs['class_name'] = class_name
        cmd = Common.create_from_class_path(exec_class_name, [], kwargs)
        ret_val = cmd.execute()
        return json.dumps(ret_val)




    @QtCore.Slot(str)
    def open_explorer(my, dir):
        if sys.platform == 'win32':
            dir = dir.replace("/", "\\")
            os.system('''explorer "%s"''' % dir)
        else:
            dir = dir.replace("\\", "/")
            # Assume OSX
            os.system('''/usr/bin/open "%s"''' % dir);

    @QtCore.Slot(str)
    def open_folder(my, dir):
        if sys.platform == 'win32':
            dir = dir.replace("/", "\\")
            os.system('''explorer "%s"''' % dir)
        else:
            dir = dir.replace("\\", "/")
            # Assume OSX
            os.system('''/usr/bin/open "%s"''' % dir);




    @QtCore.Slot(str, str)
    def create_file(my, path, doc):
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        f = open(path, 'w')
        f.write(doc)
        f.close()


    @QtCore.Slot(str, result=str)
    def get_md5(my, path):
        try:
            f = open(path, 'rb')
            CHUNK = 1024*1024
            m = hashlib.md5()
            while 1:
                chunk = f.read(CHUNK)
                if not chunk:
                    break
                m.update(chunk)
            md5_checksum = m.hexdigest()
            f.close()
            return md5_checksum
        except IOError, e:
            # do not print to stdout, write to stderr later if desired
            sys.stderr.write("WARNING: error getting md5 on [%s]: " % path)
            return ""


    @QtCore.Slot(str, result=bool)
    def exists(my, path):
        return os.path.exists(path)


    @QtCore.Slot(str, result=str)
    def get_path_info(my, path):
        stat = os.stat(path)
        info = {
            'path': path,
            'size': stat.st_size,
            'mtime': stat.st_mtime
        }

	return json.dumps(info)


    @QtCore.Slot(str, result=bool)
    def is_dir(my, path):
        return os.path.isdir(path)


    @QtCore.Slot(str)
    def makedirs(my, dir):
        os.makedirs(dir)


    @QtCore.Slot(str, int, result=str)
    def list_dir(my, dir, depth):
	paths = []
        for root, dirs, files in os.walk(dir):
	    root = root.replace("\\", "/")
	    for dir in dirs:
	        paths.append( "%s/%s/" % (root, dir) )
	    for file in files:
	        paths.append( "%s/%s" % (root, file) )
        return json.dumps(paths)

    @QtCore.Slot(str, result=str)
    def list_recursive_dir(my, dir):
	return my.list_dir(dir, 0)


    @QtCore.Slot(str, result=int)
    def get_size(my, path):
        return os.path.getsize(path)


    # FIXME: not implemented
    @QtCore.Slot(str, int, str, result=str)
    def command_port(my, url, port, cmd):
        my.show_message("command_port - Not implemented")
	return "Not implemented"


    # FIXME: not implemented
    @QtCore.Slot(result=str)
    def get_connect_error(my):
        my.show_message("get_connect_error - Not implemented")
	return "Not implemented"


    @QtCore.Slot(str, str)
    def copy_file(my, from_path, to_path):
        dirname = os.path.dirname(to_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        shutil.copy(from_path, to_path)

    @QtCore.Slot(str, str)
    def copytree(my, from_path, to_path):
        if os.path.isdir(from_path):
            try:
                shutil.copytree(from_path, to_path)
            except OSError as ex:
                if ex.errno == errno.ENOENT:
                    my.make_dirs(to_path) 
                    shutil.copy(from_path, to_path)
                else:
                    msg = ex.__str__()
                    my.js_alert(msg)
                    return
        else:
            my.make_dirs(to_path) 
            shutil.copy(from_path, to_path)

    @QtCore.Slot(str)
    def rmtree(my, path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.unlink(path)

    @QtCore.Slot(str, str)
    def move_file(my, from_path, to_path):
        shutil.move(from_path, to_path)


    @QtCore.Slot(str, result=str)
    def read_file(my, path):
        f = open(path, 'r')
        data = f.read()
        f.close()
        return data


    @QtCore.Slot(str, result=str)
    def open_file(my, path):
        os.system(path)
	return data


    @QtCore.Slot(str, str, str, result=str)
    def upload_file(my, server_url, path, subdir=None):
        ticket = my.property("ticket")
        from upload_multipart import UploadMultipart
        upload = UploadMultipart()
        upload.set_upload_server(server_url)
        if ticket:
            upload.set_ticket(ticket)
        upload.execute(path)
	return path

    @QtCore.Slot(str, str, str, result=str)
    def do_upload(my, server_url, path, subdir=None):
	return my.upload_file(server_url=server_url, path=path, subdir=subdir)


    @QtCore.Slot(str, result=str)
    def upload_directory(my, path):
        my.show_message("upload_directory - Not implemented")
	return "Not implemented"


    @QtCore.Slot(str, str)
    def download_file(my, url, to_path):
        dirname = os.path.dirname(to_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname) 
        urllib.urlretrieve(url, to_path)

        


    @QtCore.Slot(str, bool, result=str)
    def open_file_browser(my, current_dir, select_dir=False):
        # FIXME: this is very specific to nuke.  Should have some kind of an
        # environment
        try:
            import nuke
            file_path = nuke.getFilename('Get File Contents')
        except ImportError:
            #from QtCore.QObject import tr

            # default to select files
            if not select_dir:
                caption = "Select File"
                file_paths = QtGui.QFileDialog.getOpenFileName(None,caption,current_dir)
                file_path = file_paths[0]

            else:
                caption = "Select Directory"
                file_path = QtGui.QFileDialog.getExistingDirectory(None,caption,current_dir)

            if not file_path.strip():
                return None

        return json.dumps([file_path])



    @QtCore.Slot(str, result=str)
    def get_env(my, name):
        return os.environ.get(name)


    @QtCore.Slot(str, result=str)
    def execute_python(my, script):
        exec(script)
        return "OK"


    @QtCore.Slot(str, result=str)
    def open_browser_url(my, url):
        #var env = spt.Environment.get();
        #var ticket = env.get_ticket();
        #pyApplet.open_window(document.location + "admin?login_ticket=" + ticket)

        import subprocess
        py_exec = "python"
        path = __file__
        args = [url]
        retcode = subprocess.Popen([py_exec, path, args])
        return retcode


    @QtCore.Slot(str, str, result=str)
    def unzip_file(my, from_path, to_dir):
        zip_util = ZipUtil()
        return zip_util.extract(from_path, to_dir)



    # TEST start the watch folder
    @QtCore.Slot(str, str, str, result=str)
    def start_watch_folder(my, server, ticket, project):
        from watch_local_checkin import WatchLocalRepoCmd
        WatchLocalRepoCmd(
                server=server,
                ticket=ticket,
                project=project
        ).start()
        return "OK"


    def _py_version(my):  
        '''Return the Python version.'''
        return sys.version  
    py_version = QtCore.Property(str, fget=_py_version)

    def set_web_page(my, web_page):
        '''store the QWebPage in the applet to do alert'''
        my.web_page = web_page

    def js_alert(my, msg):
        my.web_page.javaScriptAlert(my.web_page.mainFrame(), msg)

    def make_dirs(my, to_path):
        dirname = os.path.dirname(to_path)
        try:
            if not os.path.exists(dirname):
                os.makedirs(dirname)
        except OSError, ex:
            msg = "Error creating directory %s.\n%s" %(dirname, ex.__str__())
            print msg
            my.js_alert(msg)


    instance = None
    def get(cls):
        if cls.instance == None:
            cls.instance = PythonApplet()
        return cls.instance
    get = classmethod(get)






def encode(class_name, args=[], kwargs={}):
    data = [
        class_name,
        args,
        kwargs
    ]
    import binascii, json
    encoded = binascii.hexlify(json.dumps(data))
    return encoded




def check_tactic(url, limit=3, verbose=True):
    import urllib2

    # Trying to connect to the server

    count = 1
    while 1:
        try:
            connection = urllib2.urlopen(url)
            ret_val = connection.code
            connection.close()
            if ret_val == 200:
                return True
            if verbose:
                print "WARNING: received value: [%s] from server" % ret_val
        except urllib2.HTTPError, e:
            if verbose:
                print "ERROR: ", e
        except urllib2.URLError, e:
            if verbose:
                print "ERROR: ", e

        count += 1
        if count > limit:
            return False



#
# Standalone client
#



class CustomMainWindow(QtGui.QMainWindow):

    # Cookies implementation referenced from
    # http://code.google.com/p/devicenzo/source/browse/trunk/devicenzo.py?spec=svn52&r=52#24


    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.settings = QtCore.QSettings("Southpaw Technology Inc", "TACTIC")

        self.cookie_jar = QtNetwork.QNetworkCookieJar()
        cookies = []
        for c in self.get("cookiejar", []):
            # For some reason, it has to be parsed as a string (not unicode)
            cookie = QtNetwork.QNetworkCookie.parseCookies(str(c))[0]
            cookies.append(cookie)
        self.cookie_jar.setAllCookies(cookies)

    def load_url(self, url):
        webView = CustomWebView()  
        webView.load(QtCore.QUrl(url))
        webView.page().networkAccessManager().setCookieJar(self.cookie_jar)
        self.setCentralWidget(webView)  


    def put(self, key, value):
        "Persist an object somewhere under a given key"
        self.settings.setValue(key, json.dumps(value))
        self.settings.sync()

    def get(self, key, default=None):
        "Get the object stored under 'key' in persistent storage, or the default value"
        v = self.settings.value(key)
        if v:
            return json.loads(unicode(v))
        else:
            return default


    def closeEvent(self, evt):
        for c in self.cookie_jar.allCookies():
            cookie = c.toRawForm()
        self.put("cookiejar", [str(c.toRawForm()) for c in self.cookie_jar.allCookies()])


class CustomWebView(QtWebKit.QWebView):
    def __init__(self, parent = None):

        QtWebKit.QWebView.__init__(self, parent)

        settings = self.settings()
        settings.setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)
        settings.setAttribute(QtWebKit.QWebSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)


        def loadJavaScriptObjects():
            applet = PythonApplet()  
            self.page().mainFrame().addToJavaScriptWindowObject("pyApplet", applet) 
        QtCore.QObject.connect(self.page().mainFrame(),
           QtCore.SIGNAL('javaScriptWindowObjectCleared()'), loadJavaScriptObjects)




    def createWindow(self, webWindowType):
        self.view = CustomWebView()
        self.view.setGeometry(100, 100, 1024, 768)
        self.view.setWindowTitle("TACTIC")
        self.view.show()
        return self.view



def open_tactic(url=None, client_only=False):   
    import os
    app = QtGui.QApplication("TACTIC")
    app_dir = app.applicationDirPath()
    if os.name =='posix' and app_dir.find('.app') != -1:
        #app.setLibraryPaths(["/Applications/TACTIC-3.9.app/Contents/PlugIns"])
        working_dir = os.getcwd()
        os.chdir(app_dir)
        library_dir = os.path.abspath("../../../PlugIns")
        app.setLibraryPaths([library_dir])
        os.chdir(working_dir)

    pixmap = QtGui.QPixmap("bin/favicon.ico")
    icon = QtGui.QIcon(pixmap)
    QtGui.QApplication.setWindowIcon(icon)
    
    pixmap = QtGui.QPixmap("bin/tactic_silver.png")
    splash = QtGui.QSplashScreen(pixmap)
    splash.show()

    start_server = False
    data_dir = tacticenv.get_data_dir()

    if not url:
        if os.path.exists(data_dir):
            url = Config.get_value("window", "url")
            if url and not url.startswith("http://") and not url.startswith("https://") and not url.startswith("./"):
                url = "%s/config/%s" % (tacticenv.get_data_dir(), url)
        start_server = True

    if not url:
        url = 'http://127.0.0.1:9123/tactic'
        start_server = True

    print "url: ", url

    if client_only:
        start_server = False


    #url = "./index.html"
    #start_server = False


    # static page initializes too quickly
    if start_server:
        if not check_tactic(url, limit=1, verbose=False):
            print "Running TACTIC Server ..."
            path = __file__
            import os
            path = path.replace("\\", "/")
            parts = path.split("/")
            path = "/".join(parts[:-2])
            if not path:
                path = "."
            #executable = r'''START "TACTIC Server" /B "%s\python\python.exe" "%s\bin\startup_standalone.py"''' % (path,path)
            if os.name == 'nt':
                executable = r'''%s\TACTIC Server.bat''' % path
            else:
                executable = r'''%s/TACTIC Server.sh''' % path
            #os.system(executable)
            import subprocess
            try:
                subprocess.call([executable])
            except Exception, e:
                # FIXME: This happens on OSX but seems to be harmless
                if str(e).find("Interrupted system call") != -1:
                    pass
                else:
                    print "WARNING: ", e


        if not check_tactic(url, limit=2, verbose=False):

            # afte trying once continue every 1/2 second
            while 1:
                if check_tactic(url, limit=2, verbose=False):
                    break
                time.sleep(0.5)




 
    window = CustomMainWindow()
    if os.path.exists(data_dir):
        geometry = Config.get_value("window", "geometry")
        title = Config.get_value("window", "title")
    else:
        geometry = None
        title = None

    if title:
        title = "TACTIC"

    if geometry:
        parts = geometry.split(",")
        parts = [int(x) for x in parts]
        window.setGeometry(parts[0], parts[1], parts[2], parts[3])
    window.setWindowTitle("TACTIC")
    window.load_url(url)

    window.show()  
    splash.finish(window)



    start_watch_folder = False
    if start_watch_folder:
        server = url
        from watch_local_checkin import WatchLocalRepoCmd
        WatchLocalRepoCmd(
                server=url,
                ticket=ticket,
                project=project
        ).start()
 

  
    sys.exit(app.exec_())


 
if __name__ == "__main__":
    
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-c", "--client_only", dest="client_only", action="store_true", help="run TACTIC Client only")
   

    (options, args) = parser.parse_args()
    client_only = options.client_only
    if args:
        open_tactic(url=args[0], client_only=client_only)
    else:
        open_tactic(client_only=client_only)

