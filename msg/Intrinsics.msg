#
# fx, fy, mx, my are in pixels, all other parameters dimensionless
# fx, fy correspond to the focal length
# mx, my are the principal point components (i.e. cx, cy)
# alpha is the skew parameter
# k1, k2, k5 are radial distortion parameters
# k3, k4 are tangential distortion parameters
#
std_msgs/Header header
float32 fx
float32 fy
float32 mx
float32 my
float32 alpha
float32 k1
float32 k2
float32 k5
float32 k3
float32 k4
