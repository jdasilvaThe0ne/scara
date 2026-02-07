import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, JointState
from std_msgs.msg import Float64MultiArray
from cv_bridge import CvBridge
import cv2
import numpy as np

class VisionMover(Node):
    def __init__(self):
        super().__init__('vision_mover')
        
        # Publishers & Subscribers
        self.cmd_pub = self.create_publisher(Float64MultiArray, '/arm_controller/commands', 10)
        self.img_sub = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)
        self.js_sub = self.create_subscription(JointState, '/joint_states', self.joint_state_callback, 10)
        
        self.bridge = CvBridge()
        self.current_joints = None
        self.latest_image = None
        
        self.get_logger().info('Vision Mover Node Started. Searching for Petri Dish...')

    def joint_state_callback(self, msg):
        # We need the positions to check if we've arrived at targets
        self.current_joints = msg.position

    def image_callback(self, msg):
        # Just store the frame; we will process it when we are ready to move
        self.latest_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

    def wait_for_reach(self, target, tolerance=0.02):
        """Monitors joint states until the error is within tolerance."""
        if self.current_joints is None: return
        
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.05)
            # Compare first 4 joints (J1, J2, J3, J4)
            current = np.array(self.current_joints[:4])
            goal = np.array(target[:4])
            error = np.linalg.norm(current - goal)
            
            if error < tolerance:
                break

    def get_petri_world_coords(self):
        """Processes the image to find the Petri dish and converts to X, Y."""
        if self.latest_image is None:
            return None

        # 1. Color Masking (Targeting your blue-ish Petri dish)
        hsv = cv2.cvtColor(self.latest_image, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([95, 80, 80])
        upper_blue = np.array([110, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # 2. Find Center
        M = cv2.moments(mask)
        if M["m00"] > 0:
            u = int(M["m10"] / M["m00"]) # Horizontal pixel
            v = int(M["m01"] / M["m00"]) # Vertical pixel
            
            # 3. Coordinate Transform
            # Camera @ (0.5, 0, 2.5), Resolution 640x480
            scale = 0.0038  # Meters per pixel based on your FOV and height
            world_x = 0.5 - ((v - 240) * scale)
            world_y = 0.0 - ((u - 320) * scale)
            
            return world_x, world_y
        return None

    def calculate_ik(self, x, y):
        """Calculates J1 and J3 based on your specific SCARA chain."""
        # Angle of the base rotation
        j1 = np.arctan2(y, x)
        
        # Distance from base (0,0,0) to target
        dist = np.sqrt(x**2 + y**2)
        
        # Prismatic extension (Total reach - fixed base offset 0.21)
        j3 = dist - 0.21
        j3 = np.clip(j3, 0.0, 0.39) # Apply URDF limits
        
        # Sequence: [J1, J2, J3, J4, Right_F, Left_F]
        # J2=0 and J4=0 keeps the arm level for the approach
        return [j1, 0.0, j3, 0.0, 0.0, 0.0]

    def run_automation(self):
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
            
            coords = self.get_petri_world_coords()
            if coords:
                wx, wy = coords
                self.get_logger().info(f'Detected Dish at World: X={wx:.3f}, Y={wy:.3f}')
                
                # 1. Approach over Dish
                target = self.calculate_ik(wx, wy)
                msg = Float64MultiArray()
                msg.data = target
                self.cmd_pub.publish(msg)
                self.wait_for_reach(target)

                # 2. Lower Z (Joint 2 or 4 could be used, or Joint 3 depending on orientation)
                # For your robot, let's pitch Joint 2 down to 0.5 to grab
                target[1] = 0.5 
                msg.data = target
                self.cmd_pub.publish(msg)
                self.wait_for_reach(target)
                
                self.get_logger().info('At Petri Dish! Sequence complete.')
                break

def main():
    rclpy.init()
    node = VisionMover()
    try:
        node.run_automation()
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()