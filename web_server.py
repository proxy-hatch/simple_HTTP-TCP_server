#!/usr/bin/python3.5
import mimetypes
import posixpath
import sys
import http.server      # this is a high level abstracted library that makes use of "socket" library
                        # http.server.BaseHTTPRequestHandler is chosen as the building block for this server
import shutil

"""
Developed to satisfy Lab 2 assignment of CMPT371

References:
the http.server manual at https://docs.python.org/3.5/library/http.server.html?highlight=http.server#module-http.server
AND 
this simple HTTP server example using this library at the python wiki:
https://wiki.python.org/moin/BaseHttpServer#Example_Code
AND
the source code of class http.server.SimpleHTTPRequestHandler (Ver.=Python3.5)

Author: Yu Xuan (Shawn) Wang
Student #: 301227972
Last Updated: July 6, 2017
"""


def usage():
    """Display when parameters entered are invalid"""
    print('usage: [My_Port_Number]')
    print('Valid port numbers are 1025-65535')
    sys.exit(1)


class MyHandler(http.server.BaseHTTPRequestHandler):
    """
    The methods for this class are modified based on the source code of class
    SimpleHTTPRequestHandler (Ver.=Python3.5)
    This serves files from the current directory and any of its subdirectories.
    The GET and HEAD requests are identical except that the HEAD request omits the actual contents of the file.
    """

    def do_GET(self):
        """Serve a GET request. """
        f = self.send_head()
        if f:
            try:
                # copy file to wfile,
                # the output stream for writing a response back to the client
                self.copyfile(f, self.wfile)
            finally:
                # close the file
                f.close()
        # terminate connection, as mentioned here: https://stackoverflow.com/a/24766943
        self.finish()
        self.connection.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        # header is sent, no need to send data for HEAD method.
        # close f if opened
        if f:
            f.close()
        # terminate connection, as mentioned here: https://stackoverflow.com/a/24766943
        self.finish()
        self.connection.close()

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the output file by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        # reject requeststhat that are not HTTP 1.0
        if(self.request_version!= 'HTTP/1.0'):
            self.send_error(http.HTTPStatus.HTTP_VERSION_NOT_SUPPORTED, "HTTP version not supported. THis server only accepts HTTP/1.0 ")  # send 505
            return None

        path = self.path
        f = None
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')  # read-only, support opening file in binary mode
        except OSError:
            self.send_error(http.HTTPStatus.NOT_FOUND, "File not found")  # send 404
            return None

        try:
            self.send_response(http.HTTPStatus.OK)  # send 200
            self.send_header("Content-type", ctype)
            self.end_headers()
            return f
        except:
            f.close()
            raise

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        """
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        """Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        used for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init()  # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream',  # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        '.txt': 'text/plain',
    })

def main():
    # parse and validate arguments
    args = sys.argv[1:]
    if not args:
        usage()
    PORT_NUMBER = int(args[0])
    # ensure valid port number in range 1025-65535
    if (not isinstance(PORT_NUMBER, int)) or PORT_NUMBER < 1025 or PORT_NUMBER > 65535:
        usage()
    server_class = http.server.HTTPServer  # HTTPServer is a socketserver.TCPServer subclass
    """Note: Upon initialization, the queue size for request backlog is already pre-configured to 5
    
    This is an attribute in class socketserver and called in server_activate() (line 463: https://github.com/python/cpython/blob/3.5/Lib/socketserver.py)
    The class http.server.HTTPServer is a subclass of socketserver.TCP, so it inherent this as well.
    
    This is explained in the manual here (find request_queue_size in page): 
    https://docs.python.org/3.5/library/socketserver.html#request_queue_size
    
    """
    httpd = server_class(("", PORT_NUMBER), MyHandler)
    try:
        httpd.serve_forever()  # handle request until an explicit shutdown() request or hangup. Default poll_interval=0.5
    except KeyboardInterrupt:  # shutdowon upon key press
        pass
    httpd.server_close()  # close the server (and socket)


if __name__ == '__main__':
    main()
