"""
This module is designed to allow you to
simulate celular autometa. You can lay out
grids of nodes and then apply a wide range of rules to them.
This module is produced by Donald Hobson.
Please report any bugs to donaldphobson@yahoo.co.uk.
This code was produced as part of a Nuffield Rescearch Project.
This code is supplied without any warranty. Any loss or dammage caused
by this code is your problem.

"""

import os.path
import random,time,math
from copy import *
try:
    import Tkinter as tk
except:
    import tkinter as tk
# use rule of form "1,4@1-1:3;2-3:#2."
class Link:
    """
    link type object,
    connects two nodes.
    """
    def __init__(self,nodes):
        """
        Create a new link object.
        Node is a a list or tuple of two node objects.
        Use like <<Link([node1,node2])>> 
        """
        assert len(nodes)==2,"Tried to form link with wrong number of nodes"
        assert nodes[0].board==nodes[1].board, "Tried to form link between nodes on diferent boards"

        self.board=nodes[0].board
        self.unid=self.board.nodeunid
        self.board.nodeunid+=1
        self.open=True
        self.nodes=nodes

        for node in self.nodes:
            
            node.active=True
            node.links.append(self)
        self.renderedObj=None
        if self.board.rendered:
            self.newObj()
        self.board.links.append(self)

    def __hash__(self):
        """
        returns unid.
        Use like <<hash(link)>>
        """
        return self.unid
    def __str__(self):
        if self.open:
            return "Link open uniqueID = "+str(self.unid)
        else:
            return "Link closed uniqueID = "+str(self.unid)
    def __iter__(self):
        """
        Allows looping on a list function.
        Use like <<for node in link:>>
        """
        for node in self.nodes:
            yield node
    def __contains__(self, value):
        """
        Allows containment testing.
        Use like <<node in link>>
        Returns True if link connects
        to node.
        """
        if value in self.nodes:
            return True
        return False
    def __and__(self,other):
        """
        Allows containment testing. 
        Use like <<link1 & link2>> 
        Returns node if both links 
        connect to the same node,
        None otherwise
        """
        for node in self:
            if node in other:
                return node
        return None
    def __eq__(self,other):
        """
        Equality tester. <<link1==link2>>
        """
        if type(self)!=type(other):
            return False
        return self.unid==other.unid and self.board.unid==other.board.unid and type(self)==type(other)
    def getOtherNode(self,node):
        """
        Allows nodes to find which other 
        Use like <<link.getOtherNode(node1)>> 
        Returns node2 if node1 and node2
        are  linked. None otherwise
        """
        if self.nodes[0]==node:
            return self.nodes[1]
        if self.nodes[1]==node:
            return self.nodes[0]
        return None

    def newObj(self):
        """
        Creates a new rendered image of an object on a preexisting board.
        """

        self.renderedObj=self.board.canvas.create_line(self.nodes[0].shadow[0],self.nodes[0].shadow[1],self.nodes[1].shadow[0],self.nodes[1].shadow[1],  tags=("L"),width=self.board.linkThickness)

    def reposition(self):
        """
        Repositions the rendered object.
        """

        self.board.canvas.coords(self.renderedObj,self.nodes[0].shadow[0],self.nodes[0].shadow[1],self.nodes[1].shadow[0],self.nodes[1].shadow[1])

    def deleteLink(self):
        """
        Gets rid of a link.
        Removes all connections and references to link.
        <<foo=Link(nodes)><
        foo.deleteLink()>>
        will create and then remove the link.
        foo will end up as a blank link object and
        will not affect the rest of the system
        in any way and has no attributes. As soon as foo
        is manually deleted or goes out of scope the
        garbadge colection in python will remove it entirely.

        """
        if self.board.rendered:
            self.board.canvas.delete(self.renderedObj)
        self.ActiveateNodes()
        for node in self:
            node.links.remove(self)
        self.board.links.remove(self)
        self.__dict__={}
    def setOpen(self,isOpen):
        if self.open!=isOpen:
            self.open=isOpen
            self.ActiveateNodes()
            if self.board.rendered:
                self.reColour()
    def reColour(self):
        if self.open:
            self.board.canvas.itemconfig(self.renderedObj,fill="black")
        else:
            self.board.canvas.itemconfig(self.renderedObj,fill="grey")
    def ActiveateNodes(self):
        
        for node in self:
                node.active=True
class Node(object):

    """
    Basic node object. 

    """


    #def __init__(self,links:"list",state:"int",location:"None"):
    def __init__(self,board,links,state,fixed=False,goalStates=[],location=None):


        """
        Create a new node,

        Use Node(links, state, location) to create a new node.
        E.G Node([0,2,3],1,[100,100]) would create a new node with
        connections to nodes of index 0,2,3 a state of 1 and a position of 100,100
        in 2D space. Raises error
        Function returns created nodes index.
        """

        if location!=None and len(location)!=board.dimensions:
            raise ValueError("Invalid Dimentionality")
        self.unid=board.nodeunid

        board.nodeunid+=1
        self.board=board
        self.state=state
        self.newState=None
        self.location=location
        self.fixed=fixed
        self.active=True
        self.goal=goalStates
        self.shadow=[0,0,0]
        if self.board.rendered:
            self.newObj()


        self.links=[]


        for node in links:
            Link((self,node))
            
        board.nodes.append(self)
        assert state<self.board.noStates,"node set to state out of range"
 
        assert self.state!=None
        if self.board.interactive:
            self.bindNextState()
    def __str__(self):
        return "Node state = "+str(self.state)+" location"
    def bindNextState(self):
        self.board.canvas.tag_bind(self.renderedObj, '<ButtonPress-1>', self.nextState)

    def deleteNode(self):
        """
        Gets rid of a node.
        Removes all connections and references to the node.
        <<foo=Node(args)><
        foo.deleteNode()>>
        will create and then remove the node.
        foo will end up as a blank node object and
        will not affect the rest of the system
        in any way and has no attributes. As soon as foo
        is manually deleted or goes out of scope the
        garbadge colection in python will remove it entirely.

        """
        if self.board.rendered:
            self.board.canvas.delete(self.renderedObj)

        for link in self.links:
            link.deleteLink()
        self.board.nodes.remove(self)
        self.__dict__={}

    def __iter__(self):
        
        for link in self.links:
            if link.open:
                yield link.getOtherNode(self)
    def __contains__(self, value):
        if value in self.links:
            return True
        return False
    def __and__(self,other):
        for link in self.links:
            if link in other:
                return link
        return None
    def __eq__(self,other):
        """
        Equality tester. <<node1==node2>>
        """
        if type(self)!=type(other):
            return False
        return self.unid==other.unid and self.board.unid==other.board.unid
    def __invert__(self):
        return self.state
    def metGoal(self):
        return self.state in self.goal
    def __boul__(self):
        self.metGoal()
    def __nonzero__(self):
        self.metGoal()
    def __hash__(self):
        """
        returns unid.
        Use like <<hash(node)>>
        """
        return self.unid
    def nextState(self,event):
        self.setState((self.state+1)%self.board.noStates)
    def newObj(self):

        self.findShadow()
        nodeSize=self.board.nodeSize
        self.renderedObj=self.board.canvas.create_oval(self.shadow[0]-nodeSize,self.shadow[1]-nodeSize,self.shadow[0]+nodeSize,self.shadow[1]+nodeSize,fill=self.board.colours[self.state],tags=("N"))
    def findShadow(self):
        self.shadow=self.board.translate[:]
        assert self.shadow!=None
        assert self.location!=None
        for ind,pair in enumerate(self.board.mapping):
            for index,scaleFac in enumerate(pair):
                self.shadow[index]+=self.location[ind]*scaleFac

    def reposition(self):
        self.findShadow()
        nodeSize=self.board.nodeSize
        self.board.canvas.coords(self.renderedObj,self.shadow[0]-nodeSize,self.shadow[1]-nodeSize,self.shadow[0]+nodeSize,self.shadow[1]+nodeSize)
        for link in self.links:
            link.reposition()
    def reColour(self):
        assert self.state!=None
        
        self.board.canvas.itemconfig(self.renderedObj,fill=self.board.colours[self.state])
    def setState(self,state):
        assert state<self.board.noStates,"node set to state out of range"

        if state==self.state:
            return
        if state==None:
            return
        if self.fixed:
            return

        self.state=state
        self.ActiveateNeighbours()
        assert self.board.rendered
        if self.board.rendered:
            self.reColour()
    def ActiveateNeighbours(self):
        self.active=True
        for neighbour in self:
                neighbour.active=True

        

class Condition:
    """
    Basic node object
    do not refference directly
    if using module
    """
    #def __init__( self , states:list , mod:int , minstate:int , maxstate:int ):
    def __init__( self ,rule, states , mod , minstate , maxstate ):
        self.rule=rule
        self.rule.conditions.append(self)
        self.states=states
        self.mod=mod
        self.min=minstate
        self.max=maxstate
        
    def test(self, stateCount):
        validstateCount=0

        for state in self.states:
            validstateCount+=stateCount[state]

        if self.mod!=None:
            validstateCount%=self.mod
        if self.min!=None:
            if validstateCount<self.min:
                return False
        if self.max!=None:
            if validstateCount>self.max :
                return False
        return True
class Rule:
    """
    Basic line object
    do not refference directly
    if using module
    """
    #def __init__( self , oldStates:list , conditions:list , output:int ):
    def __init__( self , board,oldStates , conditions , output ):
        self.oldStates=set(oldStates)
        self.conditions=conditions
        
        self.output=output
        self.board=board
        self.board.rules.append(self)
    def conditionFromString(self,string):
        intOrNone=self.board.intOrNone
        if string=="":
            return
        statesMod,MinMax=string.split("-")
        


        statesMod=statesMod.split("%")
        if len(statesMod)==1:
            statesMod.append("")
        
        assert len(statesMod)<=2,"Each condition must contain at most  one \"%\". Please use getHelp() for help."

        MinMax=MinMax.split(":")
        if len(MinMax)==1:
            MinMax.append(MinMax[0])
        assert len(MinMax)<=2,"Each condition must contain exactly one \":\". Please use getHelp() for help."

        states=statesMod[0].split(",")
        states=[intOrNone(i) for i in states]

        Condition(self,states,intOrNone(statesMod[1],False),intOrNone(MinMax[0],False),intOrNone(MinMax[1],False))
        
    def test(self, stateCount,oldState):
        if oldState not in self.oldStates:
            
            return None

        for condition in self.conditions:
            if not condition.test(stateCount):
                return None

        return self.output
class Board:
    """
    Board object
    Contains all action
    """
    #def __init__( self , oldStates:list , conditions:list , output:int ):
    boardunid=0
    def reset(self,dimensions=2,rendered=False,rotateWithMouse=False,interactive=False,nodeSize=10,linkThickness=1,mapping=[[18,0,0],[0,18,0]],translate=[20,20,0],stateCycle=None,resetFunc=0):

        self.unid=Board.boardunid
        Board.boardunid+=1
        self.nodes=[]
        self.links=[]
        self.dimensions=dimensions
        self.nodeunid=0
        self.linkunid=0
        self.noStates=1
        self.largestrulestate=0
        self.largestNodeState=0
        self.windowSize=None
        self.colours=["black","red","orange","yellow","green","blue","purple","white"]
        self.rules=[]
        self.rulestring="1,4@1-1:3,2-3:#2."
        self.dimensions=dimensions
        self.master=None
        self.canvas=None
        self.interactive=interactive
        self.rendered=rendered
        self.mapping=mapping
        self.translate=translate
        self.resetFunc=resetFunc
        
        self.nodeSize=nodeSize
        self.linkThickness=linkThickness
    def __init__(self,dimensions=2,rendered=False ,canvasXWidth=600,canvasYWidth=600,title="Network Graphic",rotateWithMouse=False,interactive=False,nodeSize=10,linkThickness=1,mapping=[[18,0,0],[0,18,0]],translate=[20,20,0],stateCycle=None,resetFunc=0):

        self.reset(dimensions=dimensions,rendered=rendered,rotateWithMouse=rotateWithMouse,interactive=interactive,nodeSize=nodeSize,linkThickness=linkThickness,mapping=mapping,translate=translate,stateCycle=stateCycle,resetFunc=resetFunc)
        if self.rendered:
            self.setupCanvas(canvasXWidth,canvasYWidth,title,rotateWithMouse,interactive)



    def setupCanvas(self,canvasXWidth=600,canvasYWidth=600,title="Network Graphic",rotateWithMouse=False,interactive=False):

        self.rendered=True
        self.windowSize=(canvasXWidth,canvasYWidth)
        self.master = tk.Tk()
#        self.master.overrideredirect(True)
#        self.master.geometry("{0}x{1}+0+0".format(self.master.winfo_screenwidth(), self.master.winfo_screenheight()))
        self.master.title(title)
        if interactive:
            self.buttonFrame=tk.Frame(self.master, height=100)
            self.applyRulesButton=tk.Button(self.buttonFrame, width=12, height=2,text="Apply Rules" ,command=self.boundApplyRules).pack(side=tk.LEFT)
            self.repeatRulesButton=tk.Button(self.buttonFrame, width=12, height=2,text="Repeat Rules",command=self.boundGoOrStop).pack(side=tk.LEFT)
            self.resetButton=tk.Button(self.buttonFrame, width=12, height=2,text="Reset",command=self.boundReset).pack(side=tk.LEFT)
            self.buttonFrame.pack()
            self.paused=True

        self.canvas= tk.Canvas(self.master, width=canvasXWidth, height=canvasYWidth)

        if rotateWithMouse:
            self.canvas.bind("<Button-1>", self.changeView)

        self.canvas.pack()
        for node in self.nodes:
            node.newObj()
        for link in self.links:
            link.newObj()
        self.refresh()
    def boundGoOrStop(self,event=None):
        self.paused=not self.paused
        if not self.paused:
            self.boundRepeatRules()
    def boundApplyRules(self,event=None):
        self.applyRules()
    def boundRepeatRules(self, event=None):

        if self.paused:
            return
        if self.applyRules()==0:
            self.paused=True
            return



        self.master.after(100, self.boundRepeatRules)                  

    def boundReset(self,event=None):
        self.paused=True
        if type(self.resetFunc)==int:
            self.nodesToState(self.resetFunc)
        else:
            self.randomizeStates(self.resetFunc)
    def refresh(self):

        self.master.update()

    def nodesToFront(self):
        self.nodes.sort(key=lambda i:i.shadow[2])
        for node in self.nodes:
            self.canvas.lift(node.renderedObj)


    def newRulesFromString(self,rulesStr,stateCycle=None):
        rulesStr=rulesStr.split(".")
        self.noStates=int(rulesStr.pop())
        for ruleStr in rulesStr:
            self.newRuleFromString(ruleStr)
        if stateCycle==None:
            stateCycle=list(range(1,self.noStates))
            stateCycle.append(0)
        self.stateCycle=stateCycle
    def newRuleFromString(self,ruleStr):
        intOrNone=self.intOrNone
        assert ruleStr!="","Two consecutive fullstops were found in the rule string. This is not valid syntax. Please use getHelp() for help."
        oldStates,ruleStr=ruleStr.split("@")
        oldStates=oldStates.split(",")
        oldStates=[int(i) for i in oldStates]
        
        conditions,output=ruleStr.split("#")
        rule=Rule(self,oldStates,[],intOrNone(output))

        conditions=conditions.split(";")
        for condition in conditions:
            rule.conditionFromString(condition)
    def newRuleFromFile(self,ruleName):
        full_path = os.path.realpath(__file__)
        with open(os.path.dirname(full_path)+"/networkRules.txt" ,mode='r' )as rules:
            lines=rules.read().splitlines()
        names=lines[::2]
        pos=names.index(ruleName.lower())
        return self.newRulesFromString(lines[pos*2+1])
    def applyRules(self):
        updatedCount=0
        

        for node in self.nodes:
            node.newState=None
            if (not node.active) or node.fixed:
                continue
            node.active=False
            stateCount=[0]*self.noStates
            for neighbours in node:

                stateCount[neighbours.state]+=1
            for rule in self.rules:
                result=rule.test(stateCount,node.state)
                if result !=None:
                    node.newState=result
                    break
                
        for node in self.nodes:
            if node.newState ==None:
                continue
            if node.newState ==node.state:
                continue
            updatedCount+=1
            node.setState(node.newState)
            node.newState=None
        if self.rendered:
            
            self.refresh()
        return updatedCount
        
    def deleteRandomLinks(self,probability=0.5):
        for link in self.links:
            if random.random()<probability:
                link.deleteLink()

#def gridNodes(xSize:int,ySize:int,sizes,state:int):
    def gridNodes(self,sizes,contactDirections,state):
        """contactDirections must contain a -ve after all +ve in all positions
        """
        assert len(sizes)==self.dimensions
        
        revSizes=sizes[:]
        revSizes.reverse()
        nodeArray=[None]*revSizes[0]
        for size in revSizes[1:]:
            l=[None]*size
            for i in range (size):
                l[i]=deepcopy(nodeArray)
            nodeArray=l

        position=[0]*self.dimensions
        doLoop=True
        while doLoop:
            nodeContacts=[]
            for contactDirection in contactDirections:
                assert len(contactDirection)==self.dimensions
                validPos=True
                linkToPos=[0]*self.dimensions

                for i in range(self.dimensions):
                    linkToPos[i]=position[i]+contactDirection[i]
                    if linkToPos[i]<0 or linkToPos[i]>=sizes[i]:
                        validPos=False
                        break
                if validPos:
                    
                    linkedToNode=nodeArray
                    for i in range(self.dimensions):
                        linkedToNode=linkedToNode[linkToPos[i]]
                        
                    if linkedToNode!=None:
                        #return nodeArray[0][0]
                        nodeContacts.append(linkedToNode)
            node=Node(self,nodeContacts,state,location=position[:])

            nodeWhere=nodeArray
            for i in position[:-1]:

                nodeWhere=nodeWhere[i]
                    
            nodeWhere[position[-1]]=node


            doLoop=False
            for i in range(self.dimensions):
                position[i]+=1
                if position[i]==sizes[i]:
                    position[i]=0
                else:

                    doLoop=True
                    break
        if self.rendered:
            self.nodesToFront()

    def distanceConnectedNode(self,state,location,minDist,connectDist,minConnects=0):

        connectToNodes=[]
        minDistSq=minDist**2
        connectDistSq=connectDist**2
        for node in self.nodes:
            totalDist=0
            for dimention,position in enumerate(node.location):
                totalDist+=(position-location[dimention])**2
            if totalDist<minDistSq:
                return False
            elif totalDist<connectDist:
                connectToNodes.append(node)

        if len(connectToNodes)<minConnects:
            return False

        Node(self,connectToNodes,state,location=location)
        return True

    def randomConnectedNodes(self,state,maxLocation,minDist,connectDist,repeat=1,minConnects=0):
        for count in range(repeat):
            location=[0]*len(maxLocation)
            for pos,loc in enumerate(maxLocation):
                location[pos]=random.uniform(0,loc)
            self.distanceConnectedNode(state,location,minDist,connectDist,minConnects)
        if self.rendered:
            self.nodesToFront()
        
    def randomizeStates(self,relitivePropabilities):

        total=0
        runingTotals=[]

        for val in relitivePropabilities:
            #in 2.7
            val=float(val)
            #
            total+=val
            runingTotals.append(total)

        for val in range(len(relitivePropabilities)):
            runingTotals[val]/=total

        for node in self.nodes:
            randomval=random.random()

            outstate=0
            for prob in range(len(runingTotals)):

                if randomval<runingTotals[prob]:
                    
                    outstate=prob
                    break
            node.setState(outstate)

    def getnoStates(self):
        return self.noStates
    def getNodeCount(self):
        return len(self.nodes)
    def intOrNone(self,stringin,isstate=True):

        if stringin=="":
            stringin=None
        else:
            stringin=int(stringin)
            if isstate:
                assert stringin< self.noStates,"The rules made reference to a state larger than the largest state arround"

        return stringin
#def nodesInStates(nodesTested:list, statesTested:list, allNodes:bool ):
    def nodesInGoal(self):

        nodesInGoal=0
        nodesNotInGoal=0
        for node in self.nodes:
            if node.goal ==[]:
                continue
            elif node.state in node.goal:
                nodesInGoal+=1
            else:
                nodesNotInGoal+=1
        return (nodesInGoal,nodesNotInGoal)
    def setStateByLocation(self,dimention, dist, state,lessThan=True,fix=False):

        for node in self.nodes:
            if lessThan and node.location[dimention]<dist:
                node.setState(state)
                node.fixed=fix
            if (not lessThan) and node.location[dimention]>dist:
                node.setState(state)
                node.fixed=fix
    def setGoalByLocation(self,dimention, dist, goal,lessThan=True):
        for node in self.nodes:
            if lessThan and node.location[dimention]<dist:
                node.goal=goal
            if (not lessThan) and node.location[dimention]>dist:
                node.goal=goal


    def nodesToState(self,state):
        for node in self.nodes:
            node.setState(state)

    def updateTillNodesInGoal(self, allNodes, checkVal=1000,pause=None):
        count=0
        while True:
            if pause!=None:
                time.sleep(pause)
            if self.applyRules()==0:
                return False
            if checkVal<=count:
                return False
            goalMet=self.nodesInGoal()
            if allNodes:
                if goalMet[1]==0:
                    return True
            else:
                if goalMet[0]!=0:
                    return True

            count+=1
    def countSteps(self,  checkVal=1000,pause=None):
        percT=0
        nperced=True
        for count in range(1,checkVal):
            if pause!=None:
                time.sleep(pause)

            if nperced:
                goalMet=self.nodesInGoal()

                if goalMet[0]!=0 :
                    nperced=False
                    percT=count
            if self.applyRules()==0:
                return (percT,count)
        raise BaseException
    def fullNodeDataRun(self,setTo,allNodes, checkVal=1000,pause=None):
        order=copy(self.nodes)
        random.shuffle(order)
        for count,node in enumerate(order):
            if self.updateTillNodesInGoal(allNodes, checkVal,pause):
                return count
            node.setState(setTo)
        return len(self.nodes)+1
    def fullLinkDataRun(self,setTo,allNodes, checkVal=1000,pause=None):
        for link in self.links:
            link.setOpen(False)
        order=copy(self.links)
        random.shuffle(order)
        for count,link in enumerate(order):
            if self.updateTillNodesInGoal(allNodes, checkVal,pause):
                return count
            link.setOpen(True)

    def changeView(self,event):
        xRot=(event.x-300.)/250.
        yRot=(event.y-300.)/250.
        scaleF=40
        self.canvas.coords(self.nodes[95].renderedObj,0,0,10,10)
        self.mapping=[[math.cos(xRot)*scaleF,0,0],[0,math.cos(xRot)*scaleF,0],[math.sin(xRot)*scaleF,math.sin(yRot)*scaleF,0]]
        for node in self.nodes:
            node.reposition()

