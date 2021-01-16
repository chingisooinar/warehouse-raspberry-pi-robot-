#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 10:12:41 2020

@author: nuvilabs
"""
import cv2
import numpy as np
class Link(object):
    def __init__(self,node1,node2,color):
        super( Link,self).__init__()
        self.links=[node1,node2]
        self.color=color
        self.HSV_RANGES = {

        # yellow is a minor color
        'yellow': [
            {
                'lower': np.array([21, 40, 40]),
                'upper': np.array([40, 255, 255])
            }
        ],
        # red is a major color
        'green': [
            {
                'lower': np.array([41, 39, 64]),
                'upper': np.array([80, 255, 255])
            }
        ],

        # blue is a major color
        'blue': [
            {
                'lower': np.array([90, 39, 64]),
                'upper': np.array([135, 255, 255])
            }
        ],
        # pink is a minor color
        'purple': [
            {
                'lower': np.array([135, 39, 40]),
                'upper': np.array([170, 255, 255])
            }
        ]
    }
    def __call__(self,img_hsv):
        mask=None
        if self.color=='red':
            lower_red = np.array([0,50,50])
            upper_red = np.array([10,255,255])
            mask0 = cv2.inRange(img_hsv, lower_red, upper_red)
            
            # upper mask (170-180)
            lower_red = np.array([175,50,50])
            upper_red = np.array([180,255,255])
            mask1 = cv2.inRange(img_hsv, lower_red, upper_red)
            
            # join my masks
            mask = mask0+mask1
        else:
            lower= self.HSV_RANGES[self.color][0]['lower']
            upper =self.HSV_RANGES[self.color][0]['upper']
            mask= cv2.inRange(img_hsv, lower, upper)
            

        return mask
        
        
class LookUp(object):
    def __init__(self):
        super( LookUp,self).__init__()
        link01=Link(0,1,'yellow')
        link07=Link(0,7,'blue')
        link05=Link(0,5,'red')
        
        link12=Link(1,2,'blue')
        link17=Link(1,7,'red')
        
        link23=Link(2,3,'red')
        link27=Link(2,7,'yellow')
        
        link34=Link(3,4,'blue')
        link36=Link(3,6,'yellow')
        
        link45=Link(4,5,'yellow')
        #link46=Link(4,6,'red')
        
        link56=Link(5,6,'blue')
        self.deadlink=Link(-1,-1,'purple')
        self.graph={0:[1,7,5],
                    1:[2,7,0],
                    2:[3,7,1],
                    3:[4,6,2],
                    4:[5,3],
                    5:[0,6,4],
                    6:[3,5],
                    7:[0,1,2]
                        
            
        }
        self.directions={0:[link01,link05,link07],1:[link01,link12,link17],2:[link12,link23,link27],3:[link23,link34,link36],4:[link34,link45],5:[link05,link45,link56],6:[link36,link56],7:[link07,link17,link27]}
    def get_rotation_link(self,src,dst):
        link_lists=self.directions[src]
        for link in link_lists:
            if src in link.links and dst in link.links:
                return link
    def get_stopping_link(self,src,dst):
        if( (src in [6,7] and dst in [0,1,2,3,5,7]) or (src == 1 and dst == 7)):
            return self.deadlink, 'purple'
        if src == 0 and dst == 7:
            return self.get_rotation_link(7,2), 'yellow'
        if src == 4 and dst == 5:
            return self.get_rotation_link(0,5), 'red'
        if src == 1 and dst == 0:
            return self.get_rotation_link(0,5), 'red'
        
        if src > dst: 
            link=self.get_rotation_link(src,dst)
            for i in range(len(self.directions[dst])):
                if(self.directions[dst][i]==link):
                    #print(self.directions[dst][i-1].color)
                    return self.directions[dst][i-1],self.directions[dst][i-1].color
        else:
            link=self.get_rotation_link(src,dst)
            for i in range(len(self.directions[dst])):
                if(self.directions[dst][i]==link):
                    #print(self.directions[dst][(i+1)%len(self.directions[dst])].color)
                    return self.directions[dst][(i+1)%len(self.directions[dst])],self.directions[dst][(i+1)%len(self.directions[dst])].color
    def get_command(self,src,dst,color):
        head = -1
        for i in self.directions[src]:
            if i.color == color:
                if i.links[0] != src:
                    head = i.links[0]
                else:
                    head = i.links[1]
        if head ==  -1:
            if self.graph[src][0] == dst:
                return 'right'
            elif self.graph[src][2] == dst:
                return 'left'
            else:
                return 'right'
        if head == dst: 
            return 'forward'
        if self.graph[src].index(head) == 0 or (self.graph[src].index(head) == 1 and self.graph[src][len(self.graph[src])-1] == dst):
            return 'right'
        if self.graph[src].index(head) == len(self.graph[src])-1  or (self.graph[src].index(head) == 1 and self.graph[src][0] == dst):
            return 'left'
                
            
                
            
        
        
                
                
        
        