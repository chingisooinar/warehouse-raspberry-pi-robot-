import socket
import time

graph = {'a':{'b':6, 'f':4 ,'h':3},
            'b':{'a':6, 'c':1, 'h':2},
            'c':{'b':1, 'd':3, 'h':5},
            'd':{'c':3, 'e':1, 'g':2},
            'e':{'d':1, 'f':1},
            'f':{'a':4, 'e':1, 'g':3},
            'g':{'d':2, 'f':3},
            'h':{'a':3, 'b':2, 'c':5}}

def dijkstra(start,goal):
    
    shortest_distance = {}
    predecessor = {}
    unseenNodes = graph
    infinity = 9999999
    path = []
    for node in unseenNodes:
        shortest_distance[node] = infinity
    shortest_distance[start] = 0
    while unseenNodes:
        minNode = None
        for node in unseenNodes:
            if minNode is None:
                minNode = node
            elif shortest_distance[node] < shortest_distance[minNode]:
                minNode = node
        for childNode, weight in graph[minNode].items():
            if weight + shortest_distance[minNode] < shortest_distance[childNode]:
                shortest_distance[childNode] = weight + shortest_distance[minNode]
                predecessor[childNode] = minNode
        unseenNodes.pop(minNode)
    currentNode = goal
    while currentNode != start:
        try:
            path.insert(0,currentNode)
            currentNode = predecessor[currentNode]
        except KeyError:
            print('Path not reachable')
            break
    path.insert(0,start)
    if shortest_distance[goal] != infinity:
        print('Weight cost: ' + str(shortest_distance[goal]))
        print('Shortest Path: ' + str(path))
        result_dict = dict()
        result_dict['weight'] = shortest_distance[goal]
        result_dict['shortest_path'] = path
        return result_dict
print('')
print('Welcome to the Socket Programming with Pi Robot')
print('This program will take start and goal nodes as the input')
print('to calculate the optimal route with the given graph using')
print("Dijkstra's algorithm and send the route to the robot")
print(',which will follow the route as received')
print('')
print('The Graph:')
print('')
print(f"A node connects to: {graph['a']}")
print(f"B node connects to: {graph['b']}")
print(f"C node connects to: {graph['c']}")
print(f"D node connects to: {graph['d']}")
print(f"E node connects to: {graph['e']}")
print(f"F node connects to: {graph['f']}")
print(f"G node connects to: {graph['g']}")
print(f"H node connects to: {graph['h']}")
print('')
print('Please insert the Start Node and Goal Node')

# Socket

s = socket.socket()

hostname = '192.168.219.106' #Server IP/Hostname
port = 8001 #Server Port

s.connect((hostname,port)) #Connects to server
msg = s.recv(1024).decode()
if msg:
    print('Message received from PI: ' + msg)
print('')
print('Enter the Start Node:')

start_node = input()
print('Enter Goal Node:')
goal_node = input()

context = dijkstra(start_node,goal_node)
# Socket

x = str(context['shortest_path']) #Gets the message to be sent
s.send(x.encode()) #Encodes and sends message (x)
start = time.time()
while True:
    msg = s.recv(1024).decode() #Gets the incomming message
    if msg:
        print('')
        print("Message received from PI: "+msg)
        if msg == 'Finished!':
            print(f'The optimal route has been visited at all the nodes. It took the robot {time.time() - start} seconds')
            s.close()
            break
    if msg:
        msg = s.recv(1024).decode()
        print('')
        print("Message received from PI: "+msg)