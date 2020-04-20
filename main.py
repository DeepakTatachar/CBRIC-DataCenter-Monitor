"""
@author: Deepak Ravikumar Tatachar, Sangamesh Kodge
@copyright: Nanoelectronics Research Laboratory
"""

import paramiko
from multiprocessing import Array, Value, Process
import numpy as np
import re
import getpass
import time
  
username = getpass.getuser() 
print("Username:", username)
try: 
    password = getpass.getpass()  
except Exception as error: 
    print('ERROR', error)    
        
base_name = 'cbric-gpu'
num_servers = 13
num_cards_per_server = 4

class SSHClient():
    PORT = 22
    NBYTES = 4096
    def __init__(self, hostname, username, password):
        self.client = paramiko.Transport((hostname, SSHClient.PORT))
        self.client.connect(username=username, password=password)
        self.session = self.client.open_channel(kind='session')

    def execute_command(self, command):
        stdout_data = []
        stderr_data = []
        self.session.exec_command(command)
        while True:
            if self.session.recv_ready():
                stdout_data.append(self.session.recv(SSHClient.NBYTES))
            if self.session.recv_stderr_ready():
                stderr_data.append(self.session.recv_stderr(SSHClient.NBYTES))
            if self.session.exit_status_ready():
                break

        exit_status = self.session.recv_exit_status()
        self.session.close()
        self.client.close()
        return stdout_data, stderr_data, exit_status

space = np.zeros((num_servers, num_cards_per_server, 3))
data = Array('f', space.flatten())
stop = Array('i', [0])

def multiprocess_work(data, stop, server):
    space_process = np.zeros((num_cards_per_server, 3))
    update_index = (server-1) * (num_cards_per_server * 3)
    final_index = update_index + (num_cards_per_server * 3)
    while(stop[0] == 0):
        card = server
        hostname = base_name + str(card)
        if(card == 9 or card == 12):
            continue

        ssh = SSHClient(hostname, username, password)
        out, err, exit_status = ssh.execute_command('nvidia-smi')
        string_out = str(out).split('\\n')

        index = 8
        if(card < 11):
            num_cards = 4
        else:
            num_cards = 3

        for j in range(num_cards):
            try:
                gpu_mem = string_out[index].split("|")[2].strip()
                gpu_usage = string_out[index].split("|")[3].split()[0]
                gpu_mem_usage = gpu_mem.split('/')[0]
                gpu_max_mem = gpu_mem.split('/')[1]
                
                mem_usage = int(re.search(r'\d+', gpu_mem_usage).group())
                max_mem = int(re.search(r'\d+', gpu_max_mem).group())
                usage = int(re.search(r'\d+', gpu_usage).group())
            
                space_process[j][0] = mem_usage
                space_process[j][1] = max_mem
                space_process[j][2] = usage
            except:
                pass
            
            index += 3

        data[update_index:final_index] = space_process.flatten()
        time.sleep(0.05)

try:
    from tkinter import * 
except ImportError:
    from Tkinter import *

process = []

for i in range(num_servers):
    p = Process(target=multiprocess_work, args=[data, stop, i+1])
    p.start()
    process.append(p)

def onClosing():
    global stop
    stop[0] = 1
    for i in range(num_servers):
        p.join()
    root.destroy()

root = Tk()
root.wm_title("GPU Monitor")
root.protocol("WM_DELETE_WINDOW", onClosing)
rows = 0
while rows < 16:
    root.rowconfigure(rows, weight=1)
    root.columnconfigure(rows,weight=1)
    rows += 1

for j in range(5): #Columns
    if(j == 0):
        text = "Server Name "
    else:
        text = "GPU "+ str(j) +" Usage"
    f = Frame(root, height=20, width=100, borderwidth=2, relief="groove")
    f.pack_propagate(0) # don't shrink
    b = Label(f, text=text)
    b.pack()
    f.grid(row=0, column=j)
ui_elemets = []
for i in range(1,14): #Rows
    row_ui_elemts = []
    for j in range(5): #Columns
        if(j == 0):
            text = "CBRIC GPU " + str(i)
        else:
            text = ""
        var = StringVar()
        var.set(text)
        f = Frame(root, height=20, width=100, borderwidth=2, relief="groove")
        f.pack_propagate(0) # don't shrink
        b = Label(f, textvariable = var)
        b.pack()
        if(j != 0):
            row_ui_elemts.append(var)
        f.grid(row=i, column=j)
    ui_elemets.append(row_ui_elemts)

def updateUI():
    global data
    np_data = np.array(data[:]).reshape((num_servers, num_cards_per_server, 3))
    for i in range(13): #Rows
        for j in range(4): #Columns
            b = ui_elemets[i][j]
            mem_usage = np_data[i,j,0]
            max_mem = np_data[i,j,1]
            usage = np_data[i,j,2]
            text =  str(usage) + "%"
            b.set(text)

    root.after(1000, updateUI)

updateUI()
mainloop()