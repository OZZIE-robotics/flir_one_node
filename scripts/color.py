#!/usr/bin/env python3

import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

# Prevent OpenCV from interfacing with any display (disable GUI)
cv2.namedWindow = lambda *args, **kwargs: None
cv2.imshow = lambda *args, **kwargs: None

class ThermalImageProcessor:
    def __init__(self):
        rospy.init_node('thermal_image_processor', anonymous=True)

        # Subscribers and Publishers
        self.sub = rospy.Subscriber('/flir_one_node/ir_16b/image_raw', Image, self.callback)
        self.pub = rospy.Publisher('/flir_one_node/ir_rgb/image_raw', Image, queue_size=10)

        # CvBridge to convert between ROS and OpenCV images
        self.bridge = CvBridge()

    def callback(self, msg):
        try:
            # Convert the incoming ROS image to a numpy array
            thermal_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')

            # Normalize the image to 8-bit (0-255)
            normalized_image = cv2.normalize(thermal_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

            # Apply a colormap (e.g., COLORMAP_JET or COLORMAP_RAINBOW)
            color_mapped_image = cv2.applyColorMap(normalized_image, cv2.COLORMAP_JET)

            # Convert the OpenCV image back to a ROS Image message
            rgb_image_msg = self.bridge.cv2_to_imgmsg(color_mapped_image, encoding="bgr8")

            # Use the same header as the incoming message
            rgb_image_msg.header = msg.header

            # Publish the RGB image
            self.pub.publish(rgb_image_msg)

        except Exception as e:
            rospy.logerr(f"Error processing thermal image: {e}")

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    try:
        node = ThermalImageProcessor()
        node.run()
    except rospy.ROSInterruptException:
        pass
