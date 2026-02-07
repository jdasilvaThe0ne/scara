import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import math

class ScaraActionNode(Node):
    def __init__(self):
        super().__init__('scara_action_node')
        self.publisher = self.create_publisher(Float64MultiArray, '/arm_controller/commands', 10)
        
        # Picking State Machine
        self.timer = self.create_timer(2.0, self.picking_sequence) # Move every 2 seconds
        self.step = 0
        
        # Test Tube Target (Relative to Robot at X=0.6, so 1.0 - 0.6 = 0.4)
        self.target_x = 0.4
        self.target_y = 0.42
        self.target_z = 0.45 

    def calculate_ik(self, x, y, z):
        # Your specific SCARA dimensions
        shoulder_z = 0.6 
        
        # Joint 1: Rotation
        theta1 = math.atan2(y, x)
        
        # Joint 2 & 3: Tilt and Extend
        dist_horizontal = math.sqrt(x**2 + y**2)
        dist_vertical = z - shoulder_z
        
        total_reach = math.sqrt(dist_horizontal**2 + dist_vertical**2)
        theta2 = math.atan2(dist_vertical, dist_horizontal)
        
        # Extension (Slider) - accounting for the 0.21m fixed part of main_arm
        extension = total_reach - 0.21
        extension = max(0.0, min(0.39, extension))
        
        return theta1, theta2, extension

    def picking_sequence(self):
        msg = Float64MultiArray()
        # [joint1, joint2, joint3, joint4, right_finger, left_finger]
        
        if self.step == 0:
            # 1. HOVER: Move above the tube (Z + 0.1)
            t1, t2, ext = self.calculate_ik(self.target_x, self.target_y, self.target_z + 0.1)
            msg.data = [t1, t2, ext, 0.0, 0.025, 0.025] # Fingers open
            self.get_logger().info("Stepping to: HOVER")

        elif self.step == 1:
            # 2. LOWER: Move to the exact tube height
            t1, t2, ext = self.calculate_ik(self.target_x, self.target_y, self.target_z)
            msg.data = [t1, t2, ext, 0.0, 0.025, 0.025]
            self.get_logger().info("Stepping to: LOWER")

        elif self.step == 2:
            # 3. GRASP: Close the fingers
            t1, t2, ext = self.calculate_ik(self.target_x, self.target_y, self.target_z)
            msg.data = [t1, t2, ext, 0.0, 0.0, 0.0] # Fingers closed (approx 0.0)
            self.get_logger().info("Stepping to: GRASP")

        elif self.step == 3:
            # 4. LIFT: Raise back up with the tube
            t1, t2, ext = self.calculate_ik(self.target_x, self.target_y, self.target_z + 0.2)
            msg.data = [t1, t2, ext, 0.0, 0.0, 0.0]
            self.get_logger().info("Stepping to: LIFT")
            self.timer.cancel() # Stop the sequence

        self.publisher.publish(msg)
        self.step += 1

def main():
    rclpy.init()
    node = ScaraActionNode()
    rclpy.spin(node)
    rclpy.shutdown()