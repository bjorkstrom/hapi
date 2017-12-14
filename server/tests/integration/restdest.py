from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import queue

ReceivedPosts = None


class _ReqHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """
        Handle POST requests.

        Put the request's header and body on the global ReceivedPosts
        queue, and reply with '204 no more content'

        """
        global ReceivedPosts
        body = self.rfile.read(int(self.headers.get("Content-Length")))

        ReceivedPosts.put((self.path, self.headers, body))

        # Reply with '204 - no more content for you'
        self.send_response(204)
        self.end_headers()


class EventsRestDest:
    """
    Emulates a RestEndpoint destination, e.g. a web server where
    we can send events.

    When an object of this class is created, an http thread is started
    serving POST requests on the specified port.

    Using get_recv_events() method, the received request are returned.
    """
    def _run(self, port):
        server_address = ("127.0.0.1", port)
        self.httpd = HTTPServer(server_address, _ReqHandler)
        self.httpd.serve_forever()

    def __init__(self, port=8081):
        global ReceivedPosts

        ReceivedPosts = queue.Queue()

        self.thread = threading.Thread(target=self._run,
                                       args=(port,))
        self.thread.start()

    def get_recv_events(self, num):
        """
        Get num received POST requests and shutdown the http server.
        """
        global ReceivedPosts

        events = []
        for _ in range(num):
            events.append(ReceivedPosts.get())

        self.httpd.shutdown()
        self.thread.join()

        return events
