#!/usr/bin/python2.7
from __future__ import division
#from subprocess import PIPE, Popen
import commands
import psutil

def get_cpu_temperature():
    temp = commands.getoutput('cat /sys/class/thermal/thermal_zone0/temp')
    return float(temp) / 1000
#    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
#    output, _error = process.communicate()
#    return float(output[output.index('=') + 1:output.rindex("'")])


def myapp(environ, start_response):
    cpu_temperature = get_cpu_temperature()
    cpu_usage = psutil.cpu_percent()

    start_response('200 OK', [('Content-Type', 'text/html')])
    yield('<html>\n')
    yield('<body>\n')
    yield('<p>cpu_temperature: ' + str(cpu_temperature) + '</p>\n')
    yield('<p>cpu_usage: ' + str(cpu_usage) + '</p>\n')

    ram = psutil.phymem_usage()
    ram_total = ram.total / 2**20       # MiB.
    ram_used = ram.used / 2**20
    ram_free = ram.free / 2**20
    ram_percent_used = ram.percent

    yield('<p>ram_total: ' + "{0:.2f}".format(ram_total) + 'MB</p>\n')
    yield('<p>ram_used: ' + str(ram.percent) + '%</p>\n')

    disk = psutil.disk_usage('/')
    disk_total = disk.total / 2**30     # GiB.
    disk_used = disk.used / 2**30
    disk_free = disk.free / 2**30
    disk_percent_used = disk.percent

    yield('<p>disk_total: ' + "{0:.2f}".format(disk_total) + 'GB</p>\n')
    yield('<p>disk_used: ' + str(disk.percent) + '%</p>\n')
    yield('</body>\n')
    yield('</html>\n')

if __name__ == '__main__':
    from flup.server.fcgi import WSGIServer
    WSGIServer(myapp).run()
