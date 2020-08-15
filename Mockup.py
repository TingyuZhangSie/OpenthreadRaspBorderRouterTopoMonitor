#!/usr/bin/env python3
import tkinter
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

import asyncio
import logging
import threading
import datetime
import time
import os
import logging
import aiocoap.resource
import aiocoap
from aiocoap import *


def thread_it(func, *args):
    t = threading.Thread(target=func, args=args) 
    t.setDaemon(True) 
    t.start()
    # t.join()

def unused():
    print('pass')
    pass
##====================CLASS TopologyGUI=======================================##
##========================BEGIN===============================================##
class TopologyGUI():

    def __init__(self):
        self.routertable=[]

        self.childNum=0
        self.routerNum=0
        self.childList=[]
        self.G = nx.Graph()
        
        self.fig=plt.figure(1)

        self.root = tkinter.Toplevel()#Tk()
        self.root.wm_title("Embedding in Tk")
        
        #Graphic symbol
        print(os.getcwd())
        self.image_file=tkinter.PhotoImage(file='/home/pi/Desktop/1.png')
        self.ll=Label(self.root,image=self.image_file)
        self.ll.grid(row=0,column=21)

        #Topology Display
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0,column=0,rowspan=20,columnspan=20)

        self.counter=1

        #Menubar
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.title('Commissioner RaspberryPi Mock Up')
        self.menubar = tkinter.Menu(self.root)
        self.filemenu = tkinter.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Thread', menu=self.filemenu)
        self.filemenu.add_command(label='Start Thread Network', command=lambda:thread_it(self.StartThreadNetwork))
        self.filemenu.add_separator()
        self.filemenu.add_command(label='Leave Thread Network', command=self.LeaveThreadNetwork)
        self.editmenu = tkinter.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Commission', menu=self.editmenu)
        self.editmenu.add_command(label='Start Commissioner', command=lambda:thread_it(self.StartCommissioner))
        self.sysmenu = tkinter.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='System', menu=self.sysmenu)
        self.sysmenu.add_command(label='Shutdown System', command=self.PowerOffSystem)
        self.sysmenu.add_command(label='Reboot System', command=self.RebootSystem)
        self.sysmenu.add_separator()
        self.sysmenu.add_command(label='About this tool', command=self.VerWinObject)
#        self.sysmenu.add_command(label='Lable', command=self.renewLabel)
#        self.sysmenu.add_command(label='Deletenode', command=self.deleteNode)
        self.root.config(menu=self.menubar)

        #Time display frame
        Label(self.root, text='Time:   ').grid(row=1,column=21,sticky=W)
        self.BRstateText=StringVar()
        self.BRstateText.set('00:00:00')
        self.BRstateLabel=Label(self.root, text=self.BRstateText.get(),bg='white',width=16)
        self.BRstateLabel.grid(row=2,column=21,sticky=W)
        
        Label(self.root, text=' ').grid(row=3,column=21,sticky=W)
        Label(self.root, text='Commissioner:').grid(row=4,column=21,sticky=W)
        self.ChildNumLabel=Label(self.root, text='disabled',bg='white',width=16)
        self.ChildNumLabel.grid(row=5,column=21,sticky=W)
        Label(self.root, text=' ').grid(row=6,column=21,sticky=E)
        
        #RadioButton
        self.rbvalue=IntVar()
        self.rbvalue.set(1)
        self.rbrloc=tkinter.Radiobutton(self.root,text='RLOC',variable=self.rbvalue,value=1)
        self.rbrloc.grid(row=7,column=21,sticky='W')
        self.rbtemp=tkinter.Radiobutton(self.root,text='Temperature',variable=self.rbvalue,value=2)
        self.rbtemp.grid(row=8,column=21,sticky='W')
        self.rbhumidity=tkinter.Radiobutton(self.root,text='Humidity',variable=self.rbvalue,value=3)
        self.rbhumidity.grid(row=9,column=21,sticky='W')
        self.rbAll=tkinter.Radiobutton(self.root,text='ALL',variable=self.rbvalue,value=4)
        self.rbAll.grid(row=10,column=21,sticky='W')

        #Cmd display on the bottom
        Button(self.root,text='Clear',command=self.clearCmdDis).grid(row=21, column=21,columnspan=1,sticky="WS")
        global DisplayCmdList
        DisplayCmdList=Listbox(self.root, width=70,height=3)
        DisplayCmdList.grid(row=21, column=0,rowspan=2,columnspan=20,sticky="nsew")

        scr1 = Scrollbar(self.root)
        DisplayCmdList.configure(yscrollcommand = scr1.set)
        scr1['command']=DisplayCmdList.yview
        scr1.grid(row=21,column=16,sticky="nsew")
        
        self.renewgraph()
        #self.StartThreadNetwork()
        
    def mainloopGUI(self):
        self.clock()
        self.root.mainloop()

#-----#Execute every 1s
    def clock(self):
        self.routertable=routertable
        time = datetime.datetime.now()
        #if time.second%2==0:
        routerlist=[router.rloc16 for router in self.routertable]
        rloclist=[item.rloc16 for item in (self.routertable+[child for router in self.routertable for child in router.childtable])]
        if self.childNum!=len(rloclist) or self.routerNum!=len(routerlist): #topology has changed
            if self.childNum>len(rloclist):
                self.print2Dis('Node Lost')
            elif self.childNum<len(rloclist):
                self.print2Dis('New Node Detected')
            self.childNum=len(rloclist)
            self.routerNum=len(routerlist)
            self.renewgraph()
        else:
            try:
                self.renewgraph(topologyChangeBit=False)
            except:
                self.renewgraph()
        self.BRstateLabel.config(text=time.strftime("%H:%M:%S"))
        self.ChildNumLabel.config(text=os.popen('wpanctl getprop Commissioner:state').read()[22:-2])
        self.root.after(700, self.clock) # run itself again after 700 ms

#-----Diagram Display function-----#
#    def addNode(self):
#        pass
#    def deleteNode(self):
#        pass
#    def renewLabel(self):
#        pass
    def VerWinObject(self):
        top = tkinter.Toplevel(self.root, width=300, height=200)
        top.title("Version")
        top.attributes('-topmost', 1)
        label1 = tkinter.Label(top, text="Version 1.0.0")
        label2 = tkinter.Label(top, text="Auther: zhangtingyu_zty@qq.com")
        label3 = tkinter.Label(top, text="Git: https://github.com/TingyuZhangSie/OpenthreadRaspBorderRouterTopoMonitor")
        label1.grid(row=0, column=0, sticky='w')
        label2.grid(row=1, column=0, sticky='w')
        label3.grid(row=2, column=0, sticky='w')
    
    def renewgraph(self,topologyChangeBit=True):
        plt.cla()
        
        self.BRrloc=os.popen('wpanctl getprop Thread:RLOC16').read()[-5:-1]
        #self.BRstate=os.popen('wpanctl getprop network:nodetype').read()
        self.G = nx.Graph()
        self.node_labels={}
        for node in self.routertable:
            #add this router
            self.G.add_node(node.rloc16)
            self.node_labels[node.rloc16]=node.rloc16
            #add link between routers
            for item in [router.rloc16 for router in self.routertable[:self.routertable.index(node)]]:
                self.G.add_edge(item,node.rloc16)
            for child in node.childtable:
                self.G.add_node(child.rloc16)
                self.G.add_edge(node.rloc16,child.rloc16)
                if self.rbvalue.get()==2:
                    self.node_labels[child.rloc16]='T:\n'+str(child.temperature)+'℃'
                elif self.rbvalue.get()==3:
                    self.node_labels[child.rloc16]='H:\n'+str(child.humidity)+'%'
                elif self.rbvalue.get()==4:
                    self.node_labels[child.rloc16]=child.rloc16 +'\nT:'+str(child.temperature)+'℃' +'\nH:'+str(child.humidity)+'%'
                else:
                    self.node_labels[child.rloc16]=child.rloc16
        if topologyChangeBit==True:
            self.pos = nx.spring_layout(self.G)
        else:
            pass
        if self.BRrloc.lower() in [router.rloc16 for router in self.routertable]:
            nx.draw_networkx_nodes(self.G, self.pos, nodelist=[router.rloc16 for router in self.routertable if router.rloc16==self.BRrloc.lower()],node_color='#c0f57a',node_size=800,node_shape='p',alpha=1)
            nx.draw_networkx_nodes(self.G, self.pos, nodelist=[router.rloc16 for router in self.routertable if router.rloc16!=self.BRrloc.lower()],node_color='#aaccff',node_size=800,node_shape='p',alpha=1)
        else:
            nx.draw_networkx_nodes(self.G, self.pos, nodelist=[router.rloc16 for router in self.routertable],node_color='#aaccff',node_size=800,node_shape='p',alpha=1)
        for router in self.routertable:
            nx.draw_networkx_nodes(self.G, self.pos, nodelist=[child.rloc16 for child in router.childtable if child.rloc16==self.BRrloc.lower()],node_color='y',node_shape='o',node_size=600,alpha=0.8)
            nx.draw_networkx_nodes(self.G, self.pos, nodelist=[child.rloc16 for child in router.childtable if child.rloc16!=self.BRrloc.lower()],node_color='#A0CBE2',node_shape='o',node_size=600,alpha=0.8)
        nx.draw_networkx_edges(self.G, self.pos,edgelist=self.G.edges, width=1, alpha=0.1)
        nx.draw_networkx_labels(self.G, self.pos, labels=self.node_labels,font_size=8)

        self.fig=plt.figure(1)
        self.canvas.draw()

#-----System function-----#
    def print2Dis(self,arg):
        DisplayCmdList.insert(0,datetime.datetime.now().strftime('%H:%M:%S')+' >>> '+str(arg))
    def clearCmdDis(self):
        DisplayCmdList.delete(0,END)
    def StartThreadNetwork(self):
        self.LeaveThreadNetwork()
        os.system('wpanctl form -c 14 -p 0x1111 -k 00112233445566778899aabbccddeeff -x 1111111122222222 SensorThreadDEMO')
        os.system('wpanctl add-prefix -o fd11:22:: -s -r -a')
        self.print2Dis('Start New Thread Network')
    def StartCommissioner(self):
        try:
            os.system('wpanctl commissioner start')
            self.print2Dis('Start Commissioner')
        except:
            self.print2Dis('Commissioner Already Started')
        time.sleep(1)
        try:
            os.system('wpanctl commissioner joiner-add "*" 300 SENSOR')
            self.print2Dis('commissioner joiner add * SENSOR')
            time.sleep(1)
            self.print2Dis('timeout:300s')
        except:
            pass
        time.sleep(300)
        self.print2Dis('Commissioning Session Ends after 300s')
    def LeaveThreadNetwork(self):
        os.system('wpanctl leave')
        self.print2Dis('Abandon Previous Thread Network')
    def RebootSystem(self):
        os.system('reboot')
    def PowerOffSystem(self):
        os.system('poweroff')
        
#-----private functions
    def __getBorderRouterState(self):
        try:
            return (os.popen('wpanctl getprop network:nodetype').read()[20:-2])
        except:
            return 'Error'

##====================class TopologyGUI=======================================##
##=========================END================================================##
def print2Dis(arg):
    DisplayCmdList.insert(0,datetime.datetime.now().strftime('%H:%M:%S')+' >>> '+str(arg))

class routernode():
    def __init__(self,rloc16):
        self.childtable=[]
        self.rloc16=rloc16
        self.description='router'
    
class childnode():
    def __init__(self,rloc16):
        self.rloc16=rloc16
        self.description='child'
        self.temperature=-1
        self.humidity=-1
        self.CO2=-1

class TimeResource(aiocoap.resource.ObservableResource):
    """Example resource that can be observed. The `notify` method keeps
    scheduling itself, and calles `update_state` to trigger sending
    notifications."""

    def __init__(self):
        super().__init__()

        self.handle = None

    def notify(self):
        self.updated_state()
        self.reschedule()

    def reschedule(self):
        self.handle = asyncio.get_event_loop().call_later(5, self.notify)

    def update_observation_count(self, count):
        if count and self.handle is None:
            print("Starting the clock")
            self.reschedule()
        if count == 0 and self.handle:
            print("Stopping the clock")
            self.handle.cancel()
            self.handle = None

    async def render_get(self, request):
        payload = datetime.datetime.now().\
                strftime("%Y-%m-%d %H:%M").encode('ascii')
        return aiocoap.Message(payload=payload)
class CoapLightFunc(resource.Resource):

    async def render_get(self, request):
        await asyncio.sleep(1)
        #print2Dis(str(request.payload))
        payload = 'get light'.encode('ascii')
        return aiocoap.Message(payload=payload)

    async def render_put(self, request):
        clientrloc16=(request.remote.hostinfo[request.remote.hostinfo.rindex(':')+1:-1]).zfill(4)
        for router in routertable:
            for child in router.childtable:
                if child.rloc16==clientrloc16:
                    #try:
                    child.temperature=(request.payload[0]*256+request.payload[1]) / 100
                    child.humidity=(request.payload[2]*256+request.payload[3]) / 100
                    print2Dis('Sensor  Value from RLOC '+child.rloc16+' Temperature:'+str(child.temperature)+'℃ Humidity:'+str(child.humidity)+'%'  )
                    #except:
                        #pass
                    #print('Rloc:'+clientrloc16+': Temperature:'+str(request.payload[0]*256+request.payload[1])+',')
        payload = bytes([0xff])#'01'.encode('ascii')
        return aiocoap.Message(payload=payload, mtype=1)

def renewNodetable(Nodetable, newNodelist, nodetype='child'):
    for rloc16 in newNodelist:
        if rloc16 not in [node.rloc16 for node in Nodetable]:
            Nodetable.append(childnode(rloc16))
    for node in Nodetable:
        if node.rloc16 not in newNodelist:
            Nodetable.remove(node)

async def GetNetDiagResp(ip):
    router=ip[-4:]
    protocol = await Context.create_client_context()
    
    request = Message(code=POST, mtype=0, uri=('coap://['+str(ip)+']:61631/d/dg'),payload=bytes([0x12,1,16]))
    response=None

    try:
        #response = await protocol.request(request).response
        response = await asyncio.wait_for(protocol.request(request).response, timeout=1)
    except Exception as e:
        #print('Failed to get diagnostic response:')
        print(e)
    else:
        #print('Result: %s\n%r'%(response.code, response.payload))
        pass
    if response == None:
        return None
    else:
        if response.payload==b'\x10\x00':
            return([])
        else:
            childlist=[router[:2]+str(response.payload[i+2]).zfill(2) for i in range(1,len(response.payload[2:2+response.payload[1]]),3)]
        return (childlist)


async def UpdateNetworkTopology(routertable):
    while(1):
        try:
            leaderIPaddress=os.popen('wpanctl getprop Thread:Leader:Address').read()[25:-2]
            rxraw=os.popen('wpanctl getprop Thread:RouterTable').read()
            rx=rxraw.splitlines()
            if len(rx)<2:
                #print('Nothin in Router Table')
                try:
                    routertable.pop()
                except:
                    pass
                await asyncio.sleep(3)
                continue
            else: #get routerlist from thread router table
                routerlist = [line[line.find('RLOC16:')+7:line.find('RLOC16:')+11] for line in rx[1:-1]]
                
            #pop out node if not in thread router table
            for router in routertable:
                if router.rloc16 not in routerlist:
                    #print(router.rloc16)
                    routertable.remove(router)
                    del(router)
           
            for rloc16 in routerlist:
                childlist= await (GetNetDiagResp((leaderIPaddress[:leaderIPaddress.rindex(':')+1]+rloc16)))
                #print([rloc16,childlist])

                if childlist == None: #connection lost
                    for router in routertable:
                        if router.rloc16==rloc16:
                            routertable.remove(router) #pop out this rloc16 in routertable
                            del(router)
                else:
                    #rloc not in routertable, create new to routertable
                    if rloc16 not in [router.rloc16 for router in routertable]:
                        newrouter=routernode(rloc16) #creat router
                        renewNodetable(newrouter.childtable, childlist) #add childlist to router
                        routertable.append(newrouter) #append router to routertable
                    else: #rloc in router table, check childtable
                        for router in routertable:
                            if router.rloc16 == rloc16:
                                renewNodetable(router.childtable, childlist)
            print([[router.rloc16,[child.rloc16 for child in router.childtable] ]for router in routertable])
            await asyncio.sleep(2)
        except:
            print('router table update exception')
            await asyncio.sleep(2)


def CoapServer():
    # Resource tree creation
    logging.basicConfig(level=logging.INFO)
    root = aiocoap.resource.Site()

    root.add_resource(['.well-known', 'core'],
            aiocoap.resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(['time'], TimeResource())
    root.add_resource(['light'], CoapLightFunc())
    
    return (aiocoap.Context.create_server_context(root))

routertable=[]
#CoapOverAllLoop(1)

def useless():
    while(1):
        time.sleep(3)
        print([[router.rloc16,[child.rloc16 for child in router.childtable] ]for router in routertable])

def CoapOverAllLoop(loop):
    logging.basicConfig(level=logging.INFO)
    #logging.getLogger("coap-server").setLevel(logging.DEBUG)
    
    asyncio.set_event_loop(loop)

    a=asyncio.Task(CoapServer())
    b=asyncio.Task(UpdateNetworkTopology(routertable))#('fd11:1111:1122::ff:fe00:1c01'))
    asyncio.get_event_loop().run_forever()



logging.basicConfig(level=logging.INFO)

routertable=[]

#routertable=[routernode('2200'),routernode('3300'),routernode('4400'),routernode('5500'),routernode('6600')]
#routertable[0].childtable=[childnode('2201'),childnode('2202')]
#routertable[1].childtable=[childnode('3301'),childnode('3302')]
#routertable[2].childtable=[childnode('4401')]
#routertable[3].childtable=[childnode('5501'),childnode('5502'),childnode('5503 ')]
#routertable[4].childtable=[childnode('6602')]
    
a=TopologyGUI()
#a.mainloopGUI()


thread_loop = asyncio.new_event_loop() 
t = threading.Thread(target=CoapOverAllLoop, args=(thread_loop,))
t.daemon = True
t.start()

main_loop = asyncio.get_event_loop()
async def main_work():
    a.mainloopGUI()
main_loop.run_until_complete(main_work()) 
 