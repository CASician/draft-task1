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
import sys
from rclpy.node import Node

from std_msgs.msg import Float32 


class BatteryPublisher(Node):

    def __init__(self, args):
        super().__init__('battery_publisher')
        drone_nr = args[0] # number: 1, 2 or 3
        discharge_law = args[1]

        self.topic = f"drone_{drone_nr}/battery"
        self.publisher_ = self.create_publisher(Float32, self.topic, 10)

        self.battery_level = 100.00 # full battery
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, lambda: self.timer_callback(discharge_law))

    def timer_callback(self, discharge_law):
        msg = Float32()
        msg.data = self.battery_level
        self.publisher_.publish(msg) # This one sends the message to the listeners.

        if (self.battery_level > 30.00 ):
            self.get_logger().info('Publishing: "%s"' % msg.data) # This one logs what it has done. Specifically in the CMD.

        if (self.battery_level <= 30.00 and self.battery_level > 15.00 ):
            self.get_logger().warn('Publishing: "%s"' % msg.data) # This one logs what it has done. Specifically in the CMD.

        if (self.battery_level <= 15.00): 
            self.get_logger().error('Publishing: "%s"' % msg.data) # This one logs what it has done. Specifically in the CMD.
        
        if discharge_law == "e": self.exponential_discharge()
        elif discharge_law == "p": self.piecewise_discharge()
        elif discharge_law == "l": self.linear_discharge()
        else: self.linear_discharge()


    def linear_discharge(self):
        if(self.battery_level > 0):
            self.battery_level -= 1 # discharge law

    def exponential_discharge(self):
        if(self.battery_level > 0):
            self.battery_level *= 0.9
    
    def piecewise_discharge(self):
        if self.battery_level > 90.0:
            drain_amount = 1  # Initial surface charge drains relatively slowly
        elif self.battery_level > 15.0:
            drain_amount = 0.5  # The stable "sweet spot" where the battery lasts the longest
        else:
            drain_amount = 1.2  # The final cliff where the capacity plummets rapidly

        # Apply the drain, ensuring it doesn't drop below 0
        self.battery_level = max(0.0, self.battery_level - drain_amount)


def main(args=None):
    rclpy.init(args=args)

    custom_args = sys.argv[1:]
    battery_publisher =BatteryPublisher(custom_args)

    rclpy.spin(battery_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    battery_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
