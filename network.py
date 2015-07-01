nodes=[]
nostates=6
largestrulestate=0
largestnodestate=0
windowSize={"x":600, "y":600,}
colours=["black","red","orange","yellow","green","blue","purple","white"]
#rule=[{"oldstates":[1,4],"condition":[{"val":[1],"mod":5,"min":1,"max":3},{"val":[0],"mod":None,"min":3,"max":None}], "output":2}]
rule=[]
rulestring="1,4@1-1:3,2-3:#2."


import random
# use rule of form "1,4@1-1:3,2-3:#2."

class Node:
    def __init__(self,contacts:list, state:int,geomPosition=None):
        self.contacts=contacts
        self.state=state
        self.geom=geomPosition
        self.active=True
def newNode(contacts:list, state:int,geomPosition=None):

    global nodes
    global largestnodestate
    
    newcontacts=[]
    

    for item in contacts:
        nodes[item].active=True
        if item<len(nodes):
            newcontacts.append(item)
            nodes[item].contacts.append(len(nodes))
    #nodes.append({"contacts":newcontacts,"state":state,"geom":geomPosition})
    nodes.append(Node(newcontacts,state,geomPosition))
    if largestnodestate<state:
            largestnodestate=state
        
    return len(nodes)-1

def deleteNode(index):
    global nodes
    for neighbour in nodes[index].contacts:
        nodes[neighbour].contacts.remove(index)
        nodes[neighbour].active=True
    lastPos=len(nodes)-1
    nodes[index]=nodes.pop()
    for neighbour in nodes[index].contacts:
        nodes[neighbour].contacts[nodes[neighbour].contacts.index(lastPos)]=index


def newLink(start,end):
    global nodes
    if start<len(nodes)and end<len(nodes):
        nodes[start].contacts.append( end )
        nodes[start].active=True
        nodes[ end ].contacts.append(start)
        nodes[ end ].active=True
def deleteLink(start,end):
    global nodes
    nodes[start].contacts.remove(end)
    nodes[start].active=True
    nodes[end].contacts.remove(start)
    nodes[ end ].active=True




def deleteRandomLinks(probability=0.5):
    for nodepos in range(len(nodes)):
        for neighbour in nodes[nodepos].contacts:
            if neighbour >= nodepos:
                if random.random()<probability:
                    deleteLink(nodepos, neighbour)

def gridNodes(xSize:int,ySize:int,state:int):
    for xNo in range (xSize):
        for yNo in range (ySize):
            conts=[]
            if xNo!=0:
                conts.append((xNo-1)*ySize+yNo)
            if yNo!=0:
                conts.append(xNo*ySize+yNo-1)
            newNode(conts,state,((xNo+1)/(xSize+2)*windowSize["x"],(yNo+1)/(ySize+2)*windowSize["y"]))
def randomizeStates(relitivePropabilities):
    global nodes
    global largestnodestate
    if largestnodestate<len(relitivePropabilities):
            largestnodestate=len(relitivePropabilities)
    total=0
    runingTotals=[]
    for val in relitivePropabilities:
        total+=val
        runingTotals.append(total)
    
    for val in range(len(relitivePropabilities)):
        runingTotals[val]/=total
    for node in nodes:
        randomval=random.random()
        outstate=0
        for prob in range(len(runingTotals)):
            if randomval<runingTotals[prob]:
                outstate=prob
                break
        node.state=outstate

def getnoStates():
    return nostates
def getNodeCount():
    return len(nodes)
def getNode(position):
    return nodes[position]
def setNodeState(position,state):
    global nodes
    global largestNodeState
    largestNodeState=max(largestNodeState,state)
    nodes[position].state=state

def update():
    #Number of states 
    global largestnodestate
    global nostates
    nostates=max(largestnodestate,largestrulestate)+1
    largestnodestate=0
    
    newStates=[]
    newActive=[]
    for node in nodes:
        if largestnodestate<node.state:
            largestnodestate=node.state
        
        oldstate=node.state
        
        neighbourcount=[]
        for addstate in range (nostates):
            neighbourcount.append(0)
        
        for link in node.contacts:
            j=nodes[link].state
            if j>=nostates:
                raise SyntaxError(str(j)+"nostates too small")
            neighbourcount[j]+=1
        
        output=None
        for line in rule:
            validline=True
            if line["oldstates"]!=None:
                validline=False
                if line["oldstates"]==[None]:
                    validline=True
                else:
                    for statecheck in line["oldstates"]:
                        if statecheck==oldstate:
                            validline=True
                            break
            if validline:
                for condition in line["condition"]:
                    
                    neighbourvaluecount=0
                    
                    for validstate in condition["val"]:
                        neighbourvaluecount+=neighbourcount[validstate]
                    
                    if condition["mod"]!=None:
                        neighbourvaluecount%=condition["mod"]
                    if condition["min"]!=None:
                        if neighbourvaluecount<condition["min"] :
                            validline=False
                            break
                    if condition["max"]!=None:
                        if neighbourvaluecount>condition["max"] :
                            validline=False
                            break
            if validline:
                output=line["output"]
                break
        if output!=None:
            newStates.append(output)
            newActive.append(True)
        else:
            newStates.append(oldstate)
            newActive.append(True)
    for nodeval in range(len(nodes)):
        nodes[nodeval].state=newstates[nodeval]
    
##
def newRule(inputstring):
    global largestrulestate
    largestrulestate=0
    inputstring=inputstring.replace(" ","")
    rulestring=inputstring
    newrule=[]
    def intornone(stringin,isstate=True):
        global largestrulestate
        if stringin=="":
            stringin=None
        else:
            stringin=int(stringin)
            if isstate and stringin> largestrulestate:
                largestrulestate=stringin
        return stringin

    lines=inputstring.split(".")
    if lines.pop() !="":
        raise SyntaxError("The rule string must end in a fullstop to indicate that it has finished. This was not found. Please use getHelp() for help.")
    for line in lines:
        if line=="":
            raise SyntaxError("Two consecutive fullstops were found in the rule string. This is not valid syntax. Please use getHelp() for help.")
        splitline=line.split("@")
        if len(splitline)!=2:
            raise SyntaxError("Each line must contain exactly one \"@\". Please use getHelp() for help.")
        partsplitline=splitline[1].split("#")
        if len(partsplitline)!=2:
            raise SyntaxError("Each line must contain exactly one \"#\". Please use getHelp() for help.")
        splitline[1]=partsplitline[0]
        splitline.append(partsplitline[1])
        currentline={"oldstates":[],"condition":[],"output":intornone(splitline[2]),}
        oldstates=splitline[0].split(",")
        for oldstatevalues in oldstates:
            currentline["oldstates"].append(intornone(oldstatevalues))
            
        conditions=splitline[1].split(";")
        if conditions==[""]:
            conditions=[]
        for condition in conditions:

            if condition=="":
                raise SyntaxError("Two consecutive \";\" were found in the rule string. This is not valid syntax. Please use getHelp() for help.")
            splitcondition=condition.split("-")
            if len(splitcondition)!=2:
                raise SyntaxError("Each condition must contain exactly one \"-\". Please use getHelp() for help.")
            partsplitcondition=splitcondition[1].split(":")
            if len(partsplitcondition)==1:
                partsplitcondition.append(partsplitcondition[0])
            if len(partsplitcondition)>2:
                raise SyntaxError("Each condition must contain exactly one \":\". Please use getHelp() for help.")
            
            otherpartsplitcondition=splitcondition[0].split("%")
            if len(otherpartsplitcondition)==1:
                otherpartsplitcondition.append("")
            if len(otherpartsplitcondition)>2:
                raise SyntaxError("Each condition must contain at most  one \"%\". Please use getHelp() for help.")
            splitcondition=otherpartsplitcondition
            splitcondition.extend(partsplitcondition)

            subsplitline=otherpartsplitcondition[0].split(",")
            subsplitasint=[]
            for subsplitvalue in subsplitline:
                subsplitasint.append(intornone(subsplitvalue))
            currentcondition={"val":subsplitasint,"mod":intornone(splitcondition[1]),"min":intornone(splitcondition[2],False),"max":intornone(splitcondition[3],False),}
            currentline["condition"].append(currentcondition)

        newrule.append(currentline)

    global rule
    rule=newrule

            

    

    return rule
help="""
Use newNode(contacts, state) to create a new node.
E.G newNode([0,2,3],1) would create a new node with
connections to nodes 0,2,3 and a state of 1.
Function returns created nodes index.

Use getNode(position) to get the properties of a
node from its index. Properties returned as an
object with state and contacts attributes."""
def getHelp():
    return help
