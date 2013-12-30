#!/usr/bin/python2.7
from __future__ import division
#from subprocess import PIPE, Popen
import commands
import psutil
from urlparse import parse_qs
import json, thread, time

class gv:
    def __init__(self):
        self.lightEnable = False
        self.actionTick  = 0
        self.action      = 'none'

        self.schNumItems = 1
        self.schItem = []
        self.schItem.append(' { "day":"tue", "hh":"12", "mm":"00","ss":"00","enable":"true" } ')

gv = gv()

def get_cpu_temperature():
    temp = commands.getoutput('cat /sys/class/thermal/thermal_zone0/temp')
    return float(temp) / 1000
#    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
#    output, _error = process.communicate()
#    return float(output[output.index('=') + 1:output.rindex("'")])

def system_stats():
    cpu_temperature = get_cpu_temperature()
    cpu_usage = psutil.cpu_percent()

    resp  = '<html>\n'
    resp += '<body>\n'
    resp += '<p>cpu_temperature: ' + str(cpu_temperature) + '</p>\n'
    resp += '<p>cpu_usage: ' + str(cpu_usage) + '</p>\n'

    ram = psutil.phymem_usage()
    ram_total = ram.total / 2**20       # MiB.
    ram_used = ram.used / 2**20
    ram_free = ram.free / 2**20
    ram_percent_used = ram.percent

    resp += '<p>ram_total: ' + "{0:.2f}".format(ram_total) + 'MB</p>\n'
    resp += '<p>ram_used: ' + str(ram.percent) + '%</p>\n'

    disk = psutil.disk_usage('/')
    disk_total = disk.total / 2**30     # GiB.
    disk_used = disk.used / 2**30
    disk_free = disk.free / 2**30
    disk_percent_used = disk.percent

    resp += '<p>disk_total: ' + "{0:.2f}".format(disk_total) + 'GB</p>\n'
    resp += '<p>disk_used: ' + str(disk.percent) + '%</p>\n'
    resp += '</body>\n'
    resp += '</html>\n'

    return resp

def light_enable():
    gv.actionTick = time.time() + 5
    gv.action = 'enable'
    resp = '&nbsp;'
    return resp

def light_disable():
    gv.actionTick = time.time() + 5
    gv.action = 'disable'
    resp = '&nbsp;'
    return resp

def light_state():
    if gv.lightEnable == True:
        resp = 'Enabled'
    else:
        resp = 'Disabled'
    return resp

def sch_json_string(item):
    if (item < gv.schNumItems):
        return gv.schItem[item]
    else:
        return ' { "day":"mon", "hh":"hh", "mm":"mm", "ss":"ss", "enable":"false" } '

def sch_reset():
    gv.schNumItems = 0;
    gv.schItem = [];

def sch_add(jsonString):
    gv.schNumItems = gv.schNumItems + 1
    gv.schItem.append(jsonString)
    return 'idx: ' + str(gv.schNumItems) + ' - ' + gv.schItem[gv.schNumItems-1]

def myapp(environ, start_response):
    htmlResp = '200 OK'
    bodyResp = '&nbsp'

    try:
        post_request_size = int(environ.get('CONTENT_LENGTH', 0))
    except(ValueError):
        post_request_size = 0

    if post_request_size == 0:
        qry = parse_qs(environ['QUERY_STRING'])

        if 'light' in qry:
            if qry['light'][0] == 'on':
                bodyResp = light_enable()
            elif qry['light'][0] == 'off':
                bodyResp = light_disable()
            elif qry['light'][0] == 'state':
                bodyResp = light_state()
            else:
                htmlResp = '406 Not Acceptable'
        elif 'sch' in qry:
            if qry['sch'][0] == 'json' and 'item' in qry:
                bodyResp = sch_json_string(int(qry['item'][0]))
            elif qry['sch'][0] == 'numItems':
                bodyResp = str(gv.schNumItems)
            elif qry['sch'][0] == 'reset':
                bodyResp = sch_reset()
            else:
                htmlResp = '406 Not Acceptable'
        elif 'stats' in qry:
            bodyResp = system_stats()
        else:
            htmlResp = '406 Not Acceptable'

    else:
        bodyResp = sch_add(environ['wsgi.input'].read(post_request_size))


    start_response(htmlResp, [('Content-Type', 'text/html')])

    yield bodyResp

def main_loop():
    gv.schNumItems = gv.schNumItems + 1
    gv.schItem.append('{"day":"mon","hh":"2","mm":"3","ss":"4","enable":"on"}')
    while True:
        if gv.actionTick != 0 and time.time() >= gv.actionTick:
           gv.actionTick  = 0
           if gv.action == 'enable':
              gv.lightEnable = True
           elif gv.action == 'disable':
              gv.lightEnable = False

        time.sleep(1)

if __name__ == '__main__':
     from flup.server.fcgi import WSGIServer
     thread.start_new_thread(main_loop, ())
     WSGIServer(myapp).run()
