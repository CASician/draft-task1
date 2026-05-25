# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32 


class BatteryMonitor(Node):

    # def __init__(self):
        # super().__init__('battery_monitor')
        # self.subscription = self.create_subscription(
            # Float32,
            # 'drone_1/battery', # can I add the other topics here? 
            # self.listener_callback,
            # 10)
        # self.subscription  # prevent unused variable warning

    def __init__(self):
        super().__init__('battery_monitor')

        # an array of 4 elements: ss[0] is empty; 1,2,3 are the last status of the drones. 
        self.swarm_state = [0, 0, 0, 0]
        self.swarm_leader = 0
    
        # List of drones you want to monitor
        drones = [1, 2, 3]
        self.drone_subs= [] # Keep references alive

        for nr in drones:
            topic_name = f'drone_{nr}/battery'
        
            sub = self.create_subscription(
                Float32,
                topic_name,
                # We use a lambda so the callback knows WHICH drone sent the message
                lambda msg, drone_id=nr: self.listener_callback(msg, drone_id),
                10
            )
            self.drone_subs.append(sub)

    def listener_callback(self, msg, drone_id):
        CLR_GREEN = '\033[92m'
        CLR_YELLOW = '\033[93m'
        CLR_RED = '\033[91m'
        CLR_RESET = '\033[0m'


        battery = msg.data
        self.swarm_state[drone_id] = battery
        self.swarm_leader = self.swarm_state.index(max(self.swarm_state))
        self.get_logger().info(f"Swarm Leader: drone_{self.swarm_leader}")

        # Initialize an empty list to hold the formatted string for each drone
        formatted_drones = []

        # Loop through our 3 drones (Indices 1, 2, and 3 in your swarm_state array)
        for i in range(1, 4):
            battery = self.swarm_state[i]
        
            # Determine the color based on individual battery level
            if battery > 30.0:
                color = ""  # Default terminal color (or CLR_GREEN if you want)
            elif 15.0 < battery <= 30.0:
                color = CLR_YELLOW
            else:
                color = CLR_RED
            
            # Format this specific drone and wrap it safely with RESET
            drone_str = f"{color}d{i}: {battery}{CLR_RESET if color else ''}"
            formatted_drones.append(drone_str)

        # Combine them all into one nice, clean log statement
        # This automatically matches whatever combination of Green/Yellow/Red currently exists
        self.get_logger().info(", ".join(formatted_drones)) 


def main(args=None):
    rclpy.init(args=args)

    battery_monitor = BatteryMonitor()

    rclpy.spin(battery_monitor)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    battery_monitor.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
