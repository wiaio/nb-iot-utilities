"""
Copyright (C) 2018 Wia (team@wia.io)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import getopt
import os
import serial
import time
import json

# Remote port  of destination Server
remote_port = "5683"
remote_ip = "52.17.209.228"

apname = os.getenv("apn", "nb.inetd.gdsp")
NBAND = 20
solicited = "1"
# Number used to register with a network operator
network_operator = os.getenv("network_operator","27201")

# Serial port of device. e.g. com4 on Windows, /dev/ttyACM0 on Linux
serial_name = os.getenv("serial_name", "/dev/ttyUSB0")

#acces token is your Device secret key found in the Wia dashboard
data = {"accessToken": os.getenv("accessToken", "d_sk_wia_testing"), "name": "nb-iot", "data": "Vodafone"}

class bcolours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def ok():
        return bcolours.OKGREEN + " OK " + bcolours.ENDC

def main(argv):
    command_help =  "  nb-iot.py full list of commands \n\t \
-a : AT command \n\t \
-v : Check device version and configuration (AT+CGMR + AT+NCONFIG?)\n\t \
-k : Reboot the Module (AT+NRB)\n\t \
-c : Check connection strength (AT+CSQ) \n\t \
-m : Checking if you are attached to the network (AT+CGATT?) \n\t \
-i : Get IP address (AT+CGPADDR=1) \n\t \
-p : Ping remote IP address (AT#ping=<remote_ip>) \n\t \
-q : Ping Google DNS (AT#ping=8.8.8.8) \n\t \
-t : Create socket and send message respectively  \n\t \
     AT+NSOCR=DGRAM,17,<port>)  (AT+NSOST=<socketId>, <remote-ip>, <remote-port>, <data-length>, <data> (hex)\n\t \
-s : Create socket and send message respectively \n\t \
    (AT+NSOCR=DGRAM,17,<port>)  (AT+NSOST=<socketId>, <remote-ip>, <remote-port>, <data-length>, <data> (hex)\n\t \
     and wait for a response \n\t \
-n : Registration and Context Activation"
    try:
        serialport = serial.Serial(serial_name, 9600, timeout=0.5)
    except IOError as e:
        print e
        print "\n Check if board connected and Serial port is correct \n"
        exit(0)
    try:
        opts, args = getopt.getopt(argv, "havekncimpdtqs")
    except getopt.GetoptError:
        print command_help
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print command_help
            exit(0)


        elif opt == '-a':
            print "Inspecting whether communication with the NB-IoT module is working"
            serialport.write("AT\r")
            response = serialport.readlines(None)
            if 'OK' in str(response):
                print bcolours.OKGREEN, "NB-IoT module working", bcolours.ENDC, "\n"
            else:
                print bcolours.FAIL, "NB-IoT module not working", bcolours.ENDC, "\n"
                exit(0)


        elif opt == '-v':
            print bcolours.BOLD + "Check for device firmware version and configuration", bcolours.ENDC
            serialport.write("AT+CGMR\r")
            response = serialport.readlines(None)
            print "Firmware verision:", response[1].replace('\r\n', ''), "\n"
            serialport.write("AT+NCONFIG?\r")
            response = serialport.readlines(None)
            print "Configuration"
            for config in response:
                print config.replace('\r\n', '')


        elif opt == '-k':
            serialport.write("AT+CFUN=1\r")
            time.sleep(5)
            response = serialport.readlines(None)
            if "OK" not in str(response):
                print str(response).replace('\r\n', '')
            else:
                print bcolours.ok()
            time.sleep(2)
            serialport.write("AT+NBAND=20\r")
            response = serialport.readlines(None)
            serialport.write("AT+NCONFIG=AUTOCONNECT,FALSE\r")
            response = serialport.readlines(None)
            #if "OK" in str(response):
            #    print bcolours.ok()
            #else:
            print str(response).replace('\r\n', '')
            time.sleep(2)
            print "Rebooting the NB-IoT module..."
            # Reset
            serialport.write("AT+NRB\r")
            time.sleep(5)
            response = serialport.readlines(None)
            if "OK" not in str(response):
                print  str(response).replace('\r\n', '')
                exit(0)
            else:
                print bcolours.OKGREEN, "REBOOTING OK", bcolours.ENDC + "\n"


        elif opt in ("-n"):
            serialport.write("AT+NBAND=?\r")
            response = serialport.readlines(None)
            print str(response).replace('\r\n', '')
            time.sleep(2)
            print bcolours.BOLD + "Registration and Context Activation",bcolours.ENDC
            print "\n", "Setting the presentation of network registration to show registration information and location"
            serialport.write("AT+CEREG=2\r")
            response = serialport.readlines(None)
            if "OK" in str(response):
                print bcolours.ok()
            else:
                print str(response).replace('\r\n', '')
            time.sleep(2)

            print "Setting module to maximum functionality"
            serialport.write("AT+CFUN=1\r")
            time.sleep(5)
            response = serialport.readlines(None)
            if "OK" not in str(response):
                print str(response).replace('\r\n', '')
            else:
                print bcolours.ok()
            time.sleep(2)
            print "Setting the Packet Data Protocol to IP with the APN {}".format(apname)
            serialport.write("AT+CGDCONT=0,\"IP\",\"" + apname + "\"\r")
            response = serialport.readlines(None)
            if "OK" not in str(response):
                print str(response).replace('\r\n', '')
            else:
                print bcolours.ok()

            print "Forcing to register with network operator: ", str(network_operator), "Mode manual"
            serialport.write("AT+COPS=1,2,\"27201\",7\r")
            response = serialport.readlines(None)
            if "OK" in str(response):
                print bcolours.ok()
            else:
                print str(response).replace('\r\n', '')
                print "Trying again"
            time.sleep(3)
            print "\n","Checking network registration status (May take up to a minute)"
            print "\n", "Response: \n\t +CEREG:< (2) Data-presentation set earlier>,\n\t <status: 1=Not registered, 2=Searching, 5=Registered>,\n\t <tracking code>,\n\t <cell-id>,\n\t (7) specifies the System Information messages which give the information about whether the serving cell supports EGPRS\n"
            attempts = 10000
            while attempts:
                time.sleep(3)
                serialport.write("AT+CEREG?\r")
                response = serialport.readlines(None)
                print response[1].replace('\r\n', '')
                if '+CEREG:2,5' in str(response):
                    break
                attempts-=1
                if attempts == 0:
                    print"\n", bcolours.FAIL, "Network not registered, try again with just -n as the argument. \n If still not connecting, check your signal strength python nb-iot.py -c (response rssi should > 9)", bcolours.ENDC
                    exit(0)
            print "\n","Pinging google DNS (IP: 8.8.8.8) within 10 seconds to keep connection open (expected NB-iot behaviour)"
            serialport.write("AT+NPING=8.8.8.8\r")
            response = serialport.readlines(None)
            if "OK" in str(response):
                print bcolours.ok()
            else:
                print str(response).replace('\r\n', '')

        elif opt in ("-c",):
            print bcolours.BOLD,"Checking connection strength and quality", bcolours.ENDC
            print "Returns +CSQ: Signal Strength Indication (RSSI) <rssi> and <quality> from the Mobile Terminal"
            serialport.write("AT+CSQ\r")
            response = serialport.readlines(None)
            print response[1].replace('\r\n', '')


        elif opt in ("-e",):
            print "Checking cops configuration"
            serialport.write("AT+COPS?\r")
            response = serialport.readlines(None)
            print str(response).replace('\r\n', '')

        elif opt in ("-m",):
            print bcolours.BOLD,"Checking if you are attached to the network", bcolours.BOLD
            serialport.write("AT+CGATT?\r")
            response = serialport.readlines(None)
            if "1" in response[1]:
                print "You are attached to the Network"
            else:
                print "You are not attached to the network"

        elif opt in ("-i",):
            print "Getting IP address"
            serialport.write("AT+CGPADDR\r")
            response = serialport.readlines(None)
            print response[1].replace('\r\n', '')
            time.sleep(10)
            response = serialport.readlines(None)
            print response


        elif opt in ("-p",):
            ping_number = 1
            print "Pinging IP address: {0}".format(remote_ip)
            serialport.write("AT+NPING={0}\r".format(remote_ip))
            response = serialport.readlines(None)
            if "OK" in str(response):
                print bcolours.ok()
            else:
                print str(response).replace('\r\n', '')
                exit(0)
            print "Waiting for response: +NPING:{0},<ttl>,<rtt>".format(remote_ip)

            while(ping_number):
                time.sleep(10)
                response = serialport.readlines(None)
                if "+NPINGERR:1" in str(response):
                    print bcolours.FAIL,  "Can't reach IP address: {0}".format(remote_ip), bcolours.ENDC
                else:
                    print response[1]
                ping_number -= 1

        elif opt in ("-q",):
            print
            "pinging Gooogle's dns (8.8.8.8)"
            serialport.write("AT+NPING=8.8.8.8\r")  # .format(remote_ip))
            response = serialport.readlines(None)
            if "OK" in str(response):
                print bcolours.ok()
            else:
                print str(response).replace('\r\n', '')

        elif opt in ("-d",):
            print "Connection Status {0}".format(remote_ip)
            serialport.write("AT+CSCON?\r")
            response = serialport.readlines(None)
            print response[1].replace('\r\n', '')

        elif opt in ("-t"):
            print "\n", bcolours.BOLD + "Creating socket and sending message", bcolours.ENDC
            # Create Socket
            sock = "AT+NSOCR=DGRAM,17,16667," + solicited + "\r"
            serialport.write(sock)
            time.sleep(3)
            response = serialport.readlines(None)
            socket = 0
            if "OK" in str(response):
                socket = response[1].replace('\r\n', '')
                print bcolours.OKGREEN, "Created socket: ", response[1].replace('\r\n', ''), bcolours.ENDC , "\n"
            coap_packet = "40020000b66576656e7473ff"
            data_json = json.dumps(data)
            data_len = str((len(data_json.encode("hex")) + len(coap_packet))/2)
            print "Sending message: "
            send = "AT+NSOST={0},".format(socket) + remote_ip + "," +remote_port + "," + data_len + "," + coap_packet + data_json.encode("hex") + "\r"
            print send, "\n"
            serialport.write(send)
            time.sleep(5)
            response = serialport.readlines(20)
            if "OK" in str(response):
                print bcolours.OKGREEN, "Sent message: ", response[1].replace('\r\n', ''), "With socket: {0}".format(socket), "Message size: {0}".format(data_len), bcolours.ENDC, "\n"
            else:
                print bcolours.FAIL, "Failed to send message", bcolours.ENDC, "\n"
            sock = "AT+NSOCL={0}\r".format(socket)
            serialport.write(sock)
            response = serialport.readlines(None)
            print "Closing socket"
            if "OK" in str(response):
                print bcolours.OKGREEN, "Closed socket: ", socket, bcolours.ENDC
            else:
                print bcolours.OKGREEN, "Failed to close socket", bcolours.ENDC


        elif opt in ("-s"):
            print "\n", "Creating socket and sending message"
            print
            sock = "AT+NSOCR=DGRAM,17,16667," + solicited + "\r"
            serialport.write(sock)
            time.sleep(3)
            response = serialport.readlines(None)
            socket = 0
            if "OK" in str(response):
                socket = response[1].replace('\r\n', '')
                print "Created socket: ", response[1].replace('\r\n', '')
            data_json = json.dumps(data)
            data_len = str(len(data_json.encode("hex"))/2)
            print "Sending message: "
            send = "AT+NSOST={0},".format(socket) + remote_ip + "," +remote_port+ "," + data_len + "," + data_json.encode("hex") + "\r"
            print send
            serialport.write(send)
            time.sleep(5)
            response = serialport.readlines(20)
            if "OK" in str(response):
                print "Sent message: ", response[1], "With socket: {0}".format(socket), "Message size: {0}".format(data_len)
            else:
                print "Failed to send message"
            print response
            # Read data
            if len(response) == 6:
                if "+NSONMI:" in response[5]:
                    rlength = response[5].replace('\r\n', '')
                    read = "AT+NSORF=0," + rlength.split(',')[1] + "\r"
                    serialport.write(read)
                    response = serialport.readlines(None)
                    rdata = response[1].split(',')[4]
                    print "Attempt to read: ", rdata.decode("hex")
            sock = "AT+NSOCL=" + socket + "\r"
            serialport.write(sock)
            response = serialport.readlines(None)




if __name__ == "__main__":
    main(sys.argv[1:])
