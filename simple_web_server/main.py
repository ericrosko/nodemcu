try:
    import usocket as socket
except:
    import socket

response_404 = """HTTP/1.0 404 NOT FOUND

<h1>404 Not Found</h1>
"""

response_500 = """HTTP/1.0 500 INTERNAL SERVER ERROR

<h1>500 Internal Server Error</h1>
"""

response_template = """HTTP/1.0 200 OK

%s
"""

import machine
import ntptime, utime
from machine import RTC
from time import sleep

seconds = ntptime.time()
rtc = RTC()
rtc.datetime(utime.localtime(seconds))

def time():
    body = """<html>
<body>
<h1>Time</h1>
<p>%s</p>
</body>
</html>
""" % str(rtc.datetime())

    return response_template % body


def dummy():
    body = "This is a dummy endpoint."

    return response_template % body


def light_on():
    led = machine.Pin(5, machine.Pin.OUT)
    led.value(1)
    body = """<html>
<body>
<h1>LED</h1>
<p>%s</p>
</body>
</html>
""" % "LED value 1 ON"
    return response_template % body


def light_off():
    led = machine.Pin(5, machine.Pin.OUT)
    led.value(0)
    body = """<html>
<body>
<h1>LED</h1>
<p>%s</p>
</body>
</html>
""" % "LED value 0 OFF"
    return response_template % body


def switch():
    
    switch_pin = machine.Pin(5, machine.Pin.IN)
    body = """<html>
<body>
<h1>Switch</h1>
<p>%s</p>
</body>
</html>
""" % "state: {}".format(switch_pin.value())
    return response_template % body


# routing dictionary
handlers = {
    'time': time,
    'dummy': dummy,
    'light_on': light_on,
    'light_off': light_off,
    'switch': switch
}


def main():
    s = socket.socket()
    ai = socket.getaddrinfo("0.0.0.0", 8080)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(addr)
    s.listen(5)
    print("Listening, connect your browser to http://<this_host>:8080")

    while True:
        res = s.accept()
        client_s = res[0]
        client_addr = res[1]
        req = client_s.recv(4096)
        # print("Request:")
        # print(req)

        try:
            path = req.decode().split("\r\n")[0].split(" ")[1]
            print("path:\n", path)

            # this condensed line below can be re-written
            # handler = handlers[path.strip('/').split('/')[0]]

            # so this will return an array of one item, like ['time'] or ['dummy']
            # it only returns one item because it *has* to return an array, and
            # it only has one item it can return for this app "/time", or "/dummy"
            # if we had two items "/time/today/" it would return ['time', 'today']
            commandArray = path.strip('/').split('/')

            # the next line extracts the text command from the array.  There is only one
            # item possible here, so the zero index is hard-coded:
            command = commandArray[0]

            # at this point command is just text, ie 'time'
            # now use that text as the key in the handler's dictionary which returns
            # a function pointer/method name to the associated method
            handler = handlers[command]  # i.e. handlers['time']

            # handler is now just a method/function pointer which can be called by adding ()
            # the method returns text in the form of an html page
            response = handler()

        except KeyError:
            # response = "eric says not working"
            response = response_404
        except Exception as e:
            response = response_500
            print(str(e))

        client_s.send(b"\r\n".join([line.encode() for line in response.split("\n")]))

        client_s.close()
        print()


main()
