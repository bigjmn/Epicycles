import math

class Node():
    def __init__(self,center,arm_length,angle,w):
        self.center = center
        self.arm_length = arm_length
        self.angle = angle
        self.w = w
        self.pos = None

    def get_pos(self):
        x_pos = self.center[0] + self.arm_length*math.cos(self.angle)
        y_pos = self.center[1] + self.arm_length*math.sin(self.angle)
        return (x_pos,y_pos)

    def timestep(self,rate):
        self.angle += self.w*rate

class Ladder():
    def __init__(self,node_config,null_center):
        self.ladder = [Node(null_center,0,0,0)]
        for i in range(len(node_config)):
            new_node_stats = node_config[i]
            previous_node = self.ladder[i]
            new_center = previous_node.get_pos()
            new_arm_length = new_node_stats[0]
            new_angle = new_node_stats[1]
            new_w = new_node_stats[2]

            new_node = Node(new_center,new_arm_length,new_angle,new_w)
            self.ladder.append(new_node)

    def get_tip(self):
        lastnode = self.ladder[-1]
        tip = lastnode.get_pos()
        return tip
    def ladderstep(self,rate):
        i = 1
        while i < len(self.ladder):
            self.ladder[i].center = self.ladder[i-1].get_pos()
            self.ladder[i].timestep(rate)
            i += 1

    def node_movement(self,rate,runtime):
        while self.t < runtime:
            self.ladderstep(rate)
            self.t += rate
