
import network as nw


gridSize=[10,10]
repeat=200


main=nw.Board(dimensions=len(gridSize),rendered=True,canvasXWidth=1000,canvasYWidth=1000,nodeSize=4)
main.newRulesFromString("0@1-1:#1.3")

main.colours=["black","blue","grey"]
main.gridNodes(gridSize,[[0,-1],[-1,0]],0)

main.setStateByLocation(0,1,1,fix=True)
main.setGoalByLocation(0,gridSize[0]-2,[1],False)

for i in range(repeat):
        print(main.fullLinkDataRun(0,False,1000))
        main.nodesToState(0)
print("done")
