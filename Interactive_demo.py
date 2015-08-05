import network as nw

main=nw.Board(dimensions=2,rendered=True,interactive=True,canvasXWidth=500,canvasYWidth=500,nodeSize=10,linkThickness=3,mapping=[[0,20,0],[20,0,0]],resetFunc=[3,0,2])
gridSize=20
main.newRuleFromFile("life")
main.colours=["black","blue","grey"]
main.gridNodes([gridSize,gridSize],[[0,-1],[-1,0]],1)
main.setStateByLocation(0,1,1,fix=True)
main.boundReset()
main.master.mainloop()
