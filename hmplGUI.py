# Warning: This "gui app" is mainly for test play.
# Do "normal things" or the behavior is undefined.

import tkinter as tk
from tkinter import messagebox
import MCTS

MCTS.loadEngine(1,"./RNG64.tf")
nsu,fpun,fpur,wtt=50,1.6,1.2,1.0
MCTS.setNumSimul(nsu)
MCTS.setFPU(fpun,fpur)
MCTS.valueWt=wtt*MCTS.num_simul

root=tk.Tk(className='AzG')
boolvar=tk.IntVar()
dxwidget=90
dx=34
pce=int(dx/2.3)
sar=int(dx/10)
hdx=dx//2
barcenter=int(dx*19.5)
barlength=int(dx*1.25)
gameover=0
isfree=True

mvlst=[]
nblst=[]
pllst=[]
evlst=[]
brlst=[]
filled=[[0 for _ in range(15)] for __ in range(15)]

root.geometry("%dx%d"%(18*dx+30,21*dx+60))
canvas=tk.Canvas(root,width=18*dx,height=21*dx,bg="gold")
canvas.place(x=10,y=40)

def redrawEval():
    global brlst
    for brs in brlst:
        canvas.delete(brs)
    nbs=len(evlst)
    brlst=[]
    if(nbs==0):
        return
    brwd=min(dx//2,dx*14//nbs)
    for ii in range(nbs):
        ddy=((evlst[ii]-0.5)*2*barlength) if ii%2==0 else ((0.5-evlst[ii])*2*barlength)
        if(ddy>=1 or ddy<= -1):
            brlst.append(canvas.create_rectangle(dx*2+brwd*ii,barcenter,dx*2+brwd*(ii+1),barcenter-ddy,fill="gray35" if ddy>0 else "gray70"))
        else:
            brlst.append(canvas.create_line(dx*2+brwd*ii,barcenter,dx*2+brwd*(ii+1),barcenter,fill="black"))

def takeBack():
    global gameover
    if(len(mvlst)<1):
        print("Cannot take back!")
        return
    canvas.delete(mvlst[-1])
    canvas.delete(nblst[-1])
    filled[pllst[-1][0]][pllst[-1][1]]=0
    mvlst.pop()
    pllst.pop()
    nblst.pop()
    evlst.pop()
    redrawEval()
    if(gameover):
        canvas.bind("<Button-1>",playStone)
        btmEval.config(state='normal')
        gameover=0
    MCTS.takeBack()
    MCTS.printBoard(MCTS.board)
    print("%d to move; %3d moves played."%(MCTS.side2move,MCTS.move_count))

def newGame():
    global gameover,evlst,nblst,pllst,mvlst,filled
    if(len(mvlst)<1):
        print("Cannot take back!")
        return
    for obj in mvlst:
        canvas.delete(obj)
    for obj in nblst:
        canvas.delete(obj)
    filled=[[0 for _ in range(15)] for __ in range(15)]
    mvlst=[]
    pllst=[]
    nblst=[]
    evlst=[]
    redrawEval()
    if(gameover):
        canvas.bind("<Button-1>",playStone)
        btmEval.config(state='normal')
        gameover=0
    MCTS.side2move=0
    MCTS.move_count=0
    MCTS.board*=0
    MCTS.printBoard(MCTS.board)
    print("%d to move; %3d moves played."%(MCTS.side2move,MCTS.move_count))

def playStoneXY(px,py,evalu=0.5):
    global gameover
    if(px<0 or px>14 or py<0 or py>14):
        return
    print("play",px,py)
    if(filled[px][py]):
        print("Non empty!")
        return 1
    else:
        filled[px][py]=1
        mvlst.append(canvas.create_oval(dx*(py+2)-pce,dx*(px+2)-pce,dx*(py+2)+pce,dx*(px+2)+pce,width=2,fill="white" if MCTS.move_count%2==1 else "black"))
        nblst.append(canvas.create_text(dx*(py+2),dx*(px+2),text=str(MCTS.move_count+1),fill="red" if MCTS.move_count%2==1 else "cyan"))
        pllst.append([px,py])
        evlst.append(evalu)
        redrawEval()
        MCTS.applyMove(px*15+py)
        MCTS.printBoard(MCTS.board)
        print("%d to move; %3d moves played."%(MCTS.side2move,MCTS.move_count))
        if(MCTS.winLossDraw()!=-1):
            print("game over!")
            root.update()
            messagebox.showinfo(master=root,message="Game Over!")
            gameover=1
            canvas.unbind("<Button-1>")
            btmEval.config(state='disabled')
            return 1
    return 0

def ComputerMove():
    print("Computer thinking...")
    MCTS.timeReset()
    mv,dpt=MCTS.run_mcts(MCTS.evaluatePositionA,False)
    if(MCTS.side2move==1):
        print("%3d X %2d %2d %.3f, d %2d"%(MCTS.move_count,mv[0]//15,mv[0]%15,mv[2],dpt))
    else:
        print("%3d O %2d %2d %.3f, d %2d"%(MCTS.move_count,mv[0]//15,mv[0]%15,mv[2],dpt))
    MCTS.printTime()
    playStoneXY(mv[0]//15,mv[0]%15,mv[2])

def playStone(event):
    global isfree
    if(not isfree): 
        print("Do not pre-move!")
        return
    isfree=False
    px,py=(event.y+hdx)//dx-2, (event.x+hdx)//dx-2
    if(playStoneXY(px,py)==0):
        if(boolvar.get()):
            root.update()
            ComputerMove()
    isfree=True

def changeNNode(xx1):
    global nsu,fpun,fpur,wtt
    lstt=xx1.split()
    try:
        nsu=int(lstt[0])
    except:
        print("Bad cmd!")
    if(nsu>0):
        MCTS.setNumSimul(nsu)
    else:
        print("Illegal number of nodes!")

    try:
        fpun,fpur=float(lstt[1]),float(lstt[2])
    except:
        print("Bad cmd!")
    if(fpun>=0.5 and fpun<=2.0 and fpur>=0.5 and fpur<=2.0):
        MCTS.setFPU(fpun,fpur)
    else:
        print("Illegal FPU!")

    try:
        wtt=float(lstt[3])
    except:
        print("Bad cmd!")
    if(wtt>0):
        MCTS.valueWt=wtt*MCTS.num_simul
        print("value weight set to",wtt)
    else:
        print("Illegal number!")

btmEval=tk.Button(root,text="Comp Play",command=ComputerMove)
btmEval.place(x=10,y=10)
autoPlay=tk.Checkbutton(root,text="auto play",variable=boolvar)
autoPlay.place(x=dxwidget+10,y=10)
autoPlay.toggle()
btmBack=tk.Button(root,text="Take Back",command=takeBack)
btmBack.place(x=dxwidget*2+10,y=10)
btmNew=tk.Button(root,text="New Game",command=newGame)
btmNew.place(x=dxwidget*5.6+10,y=10)
entNod=tk.Entry(root,width=12)
entNod.place(x=dxwidget*4+10,y=10)
entNod.insert(0,"%d %.1f %.1f %.1f"%(nsu,fpun,fpur,wtt))
btmSnd=tk.Button(root,text="Set Param.",command=lambda:changeNNode(entNod.get()))
btmSnd.place(x=dxwidget*3+10,y=10)



canvas.bind("<Button-1>",playStone)

for i in range(15):
    canvas.create_line(dx*2,dx*(i+2),dx*16,dx*(i+2))
    canvas.create_line(dx*(i+2),dx*2,dx*(i+2),dx*16)
    canvas.create_text(dx,dx*(i+2),text=str(i))
    canvas.create_text(dx*17,dx*(i+2),text=str(i))
    canvas.create_text(dx*(i+2),dx,text=str(i))
    canvas.create_text(dx*(i+2),dx*17,text=str(i))
canvas.create_rectangle(dx*(7 +2)-sar,dx*(7 +2)-sar,dx*(7 +2)+sar,dx*(7 +2)+sar,fill="black")
canvas.create_rectangle(dx*(3 +2)-sar,dx*(3 +2)-sar,dx*(3 +2)+sar,dx*(3 +2)+sar,fill="black")
canvas.create_rectangle(dx*(3 +2)-sar,dx*(11+2)-sar,dx*(3 +2)+sar,dx*(11+2)+sar,fill="black")
canvas.create_rectangle(dx*(11+2)-sar,dx*(3 +2)-sar,dx*(11+2)+sar,dx*(3 +2)+sar,fill="black")
canvas.create_rectangle(dx*(11+2)-sar,dx*(11+2)-sar,dx*(11+2)+sar,dx*(11+2)+sar,fill="black")
for i in [-1,1]:
    canvas.create_line(dx*2,barcenter+i*barlength,dx*16,barcenter+i*barlength,fill="black")
root.mainloop() 