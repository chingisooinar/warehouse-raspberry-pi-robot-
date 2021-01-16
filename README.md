# Warehouse Robot

I present a Raspberry Pi robot that imitates the path navigation functionality of the modern warehouse robots used in various huge companies, such as Amazon. As it can be seen from the figure supplies, there are some marks, in the form of black lines, using which robots are able to orientate and travel around a warehouse. Thus, we provide a simplified model of the system where a robot is able to follow a path obtained using Dijkstra’s algorithm. With the help of socket programming (as we learnt from class), we managed to connect the robot to a device that is on the same network.

Simulation:

URL: [https://www.youtube.com/watch?v=hosR-X85148&feature=youtu.be](https://www.youtube.com/watch?v=hosR-X85148&feature=youtu.be)

[https://www.youtube.com/watch?v=hosR-X85148&feature=youtu.be](https://www.youtube.com/watch?v=hosR-X85148&feature=youtu.be)

# MAP : How To Use

![Warehouse%20Robot%2097e8fae5dc9f476eabe829ce6a09e38f/Untitled.png](Warehouse%20Robot%2097e8fae5dc9f476eabe829ce6a09e38f/Untitled.png)

As it can be seen, there are 8 different nodes labeled from ‘a’ to ‘h’. Another aspect to mention is that there are colorful stripes, which are red, blue, yellow and purple. The details on how the robot utilizes them in order to navigate are provided in the section below. Finally, as it can be noticed there are various weights assigned to each link, hence the Dijkstra's algorithm mentioned above is used in order to compute the most efficient path. 

```python
init_HEAD = {0:'blue',1:'red',2:'yellow',3:'yellow',4:'yellow',5:'blue',6:'blue',7:'yellow'}
```

- If you want to place the robot at any node, you need to adjust its head looking at a corresponding color. Note that 0 - 7 corresponds to the nodes labeled 'a' - 'h'

![Warehouse%20Robot%2097e8fae5dc9f476eabe829ce6a09e38f/Untitled%201.png](Warehouse%20Robot%2097e8fae5dc9f476eabe829ce6a09e38f/Untitled%201.png)

# How To Use?

> We assume that you use AlphaBot2 and all the requirements to run and work with the robot are installed properly.  User Manual: [https://www.mouser.com/pdfdocs/Alphabot2-user-manual-en.pdf](https://www.mouser.com/pdfdocs/Alphabot2-user-manual-en.pdf)

- First copy and paste [Alphabot2.py](http://alphabot2.py), [Combined.py](http://combined.py), look_up.py and [TRSensors.py](http://trsensors.py) to the robot's environment.
- Put the robot on the line and run [Combined.py](http://combined.py), and wait until it is calibrated after which you need to adjust its head to look at a certain color (mentioned above).
- Run client code on your device and wait until you receive "New connection made!" from the robot. This means you are ready to go.

# Tests

First, you need to input a source and a destination node after which the shortest path is computed.

![Warehouse%20Robot%2097e8fae5dc9f476eabe829ce6a09e38f/Untitled%202.png](Warehouse%20Robot%2097e8fae5dc9f476eabe829ce6a09e38f/Untitled%202.png)

It displays the total weight as well as the full path itself

![Warehouse%20Robot%2097e8fae5dc9f476eabe829ce6a09e38f/Untitled%203.png](Warehouse%20Robot%2097e8fae5dc9f476eabe829ce6a09e38f/Untitled%203.png)

As it can be seen, the robot keeps sending messages until it reaches its goal. 

![Warehouse%20Robot%2097e8fae5dc9f476eabe829ce6a09e38f/Untitled%204.png](Warehouse%20Robot%2097e8fae5dc9f476eabe829ce6a09e38f/Untitled%204.png)

- More simulation runs can be watched via:

> [https://drive.google.com/file/d/1sCQIOdQQDlSydPigWDXhU9KBcOJo9ejK/view?usp=sharing](https://drive.google.com/drive/folders/1gqLJgCHsYqLssFw8ywZ6Iexk-e91L4gy?usp=sharing)

# Requirements

```python
RPi.GPIO==0.7.0
opencv-python==4.4.0.44
opencv-python-headless==4.4.0.44
numpy @ file:///tmp/build/80754af9/numpy_and_numpy_base_1603570489231/work
scikit-learn==0.23.2
sklearn==0.0
socket
```
