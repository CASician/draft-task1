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
        # This branch prints the swarm leader and logs when drones battery is lower than 30. 

        battery = msg.data
        self.swarm_state[drone_id] = battery
        self.swarm_leader = self.swarm_state.index(max(self.swarm_state))
        self.get_logger().info(f"Swarm Leader: drone_{self.swarm_leader}")

        # if( battery > 30 ):
            # self.get_logger().info(f"Drone {drone_id} battery level is: {battery}%")
        if( battery <= 30 and battery > 15 ):
            self.get_logger().warn(f"Drone {drone_id} battery level is: {battery}%")
        if( battery <= 15 ):
            self.get_logger().error(f"Drone {drone_id} battery level is: {battery}%")

    # def listener_callback(self, msg):
        # self.get_logger().info('I heard: "%s"' % msg.data)


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
