import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import time

class PetriDishMover(Node):
    def __init__(self):
        super().__init__('petri_dish_mover')
        # Create a publisher to the same topic your Bash script used
        self.publisher_ = self.create_publisher(Float64MultiArray, '/arm_controller/commands', 10)
        #wait for subscriber
        self.get_logger().info('Waiting for arm_controller to become available...')
        #while self.publisher_.get_subscription_count()==0:
       #      rclpy.spin_once(self,timeout_sec=0.1)
        self.get_logger().info('Controller conected! Starting Sequence...')
        # Defining the sequence of coordinates [J1, J2, J3, Right_F, Left_F, Tool]
        self.sequence = [
            [0.699, 0, 0.1, 0, 0, 0], # Approach
            [0.699, 0, 0.26, 0, 0, 0], # Lower
            [0.699, 0.13, 0.26, 0, 0, 0], # Grip
            [0.699, 0.15, 0.26, 0, 0.018, 0], # Lift & Center
            [0.699, 0.15, 0.26, 0, 0.018, -0.012], # Place Position
            [0.699, 0, 0.26, 0, 0.018, -0.012],  # Releas
            [-0.699, 0, 0.26, 0, 0.018, -0.012],
            [-0.699, 0.13, 0.26, 0, 0.018, -0.012],
            [-0.699, 0, 0.26, 0, 0, 0],
            [0, 0, 0.1, 0, 0, 0]
        ]
        '''self.step_index=0
        self.timer=self.create_timer(0.1,self.timer_callback)
    def timer_callback(self):
        if self.step_index >= len(self.sequence):
            self.get_logger().info('Sequence complete.')
            self.timer.cancel()
            return

        msg = Float64MultiArray()
        msg.data = self.sequence[self.step_index]

        self.get_logger().info(f'Sending command {self.step_index}: {msg.data}')
        self.publisher_.publish(msg)

        self.step_index += 1'''

    def execute_sequence(self):
        count=1
        msg = Float64MultiArray()
        for step_data in self.sequence:
            msg.data = step_data
            self.get_logger().info(f'Sending Command: {step_data}')
            while self.publisher_.get_subscription_count()==0:
             rclpy.spin_once(self,timeout_sec=1)

            self.publisher_.publish(msg)
            
            # This sleep replaces your "Enter" key press. 
            # In the future, we will replace this with a 'Success' check.
            if count==7:
                time.sleep(7.0)
            else:
                time.sleep(3) 
            count=count+1

def main(args=None):
    rclpy.init(args=args)
    mover = PetriDishMover()
    mover.execute_sequence()
    mover.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
