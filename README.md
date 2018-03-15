ifm3d-ros
=========
ifm3d-ros is a wrapper around [ifm3d](https://github.com/lovepark/ifm3d)
enabling the usage of ifm pmd-based ToF cameras (including the new O3X) from
within [ROS](http://ros.org) software systems.

Software Compatibility Matrix
-----------------------------
<table>
  <tr>
    <th>ifm3d-ros version</th>
    <th>ifm3d version</th>
    <th>ROS distribution(s)</th>
  </tr>
  <tr>
    <td>0.1.0</td>
    <td>0.1.0</td>
    <td>Kinetic</td>
  </tr>
  <tr>
    <td>0.2.0</td>
    <td>0.2.0</td>
    <td>Kinetic, Indigo</td>
  </tr>
  <tr>
    <td>0.3.0</td>
    <td>0.2.0</td>
    <td>Kinetic, Indigo</td>
  </tr>
  <tr>
    <td>0.4.0</td>
    <td>0.2.0, 0.3.0, 0.3.1, 0.3.2</td>
    <td>Kinetic, Indigo</td>
  </tr>
  <tr>
    <td>0.4.1</td>
    <td>0.3.3, 0.4.0, 0.5.0, 0.6.0, 0.7.0, 0.8.1</td>
    <td>Kinetic, Indigo</td>
  </tr>
</table>

Prerequisites
-------------

(Recommended)

1. [Ubuntu 16.04 LTS](http://www.ubuntu.com)
2. [ROS Kinetic](http://www.ros.org/install) - we recommend `ros-kinetic-desktop-full`.
3. [ifm3d](https://github.com/lovepark/ifm3d)

(Acceptable)

1. [Ubuntu 14.04 LTS](http://www.ubuntu.com)
2. [ROS Indigo](http://wiki.ros.org/indigo/Installation) - we recommend `ros-indigo-desktop-full`.
3. [ifm3d](https://github.com/lovepark/ifm3d) (version >= 0.2.0)

Building and Installing the Software
------------------------------------
Step-by-step instructions on getting a fresh installation of Ubuntu and ROS
prepared for usage with `ifm3d-ros` is available at the following links:
* [Ubuntu 14.04 with ROS Indigo](doc/indigo.md)
* [Ubuntu 16.04 with ROS Kinetic](doc/kinetic.md)

Building and installing ifm3d-ros is accomplished by utilizing the ROS
[catkin](http://wiki.ros.org/catkin) tool. There are many tutorials and other
pieces of advice available on-line advising how to most effectively utilize
catkin. However, the basic idea is to provide a clean separation between your
source code repository and your build and runtime environments. The
instructions that now follow represent how we choose to use catkin to build and
_permanently install_ a ROS package from source.

First, we need to decide where we want our software to ultimately be
installed. For purposes of this document, we will assume that we will install
our ROS packages at `~/ros`. For convenience, we add the following to our
`~/.bash_profile`:

```
if [ -f /opt/ros/kinetic/setup.bash ]; then
  source /opt/ros/kinetic/setup.bash
fi

cd ${HOME}

export LPR_ROS=${HOME}/ros

if [ -d ${LPR_ROS} ]; then
    for i in $(ls ${LPR_ROS}); do
        if [ -d ${LPR_ROS}/${i} ]; then
            if [ -f ${LPR_ROS}/${i}/setup.bash ]; then
                source ${LPR_ROS}/${i}/setup.bash --extend
            fi
        fi
    done
fi
```

Next, we need to get the code from github. We assume we keep all of our git
repositories in `~/dev`.

```
$ cd ~/dev
$ git clone https://github.com/lovepark/ifm3d-ros.git
```

We now have the code in `~/dev/ifm3d-ros`. Next, we want to create a _catkin
workspace_ that we can use to build and install that code from. It is the
catkin philosophy that we do not do this directly in the source directory.

```
$ cd ~/catkin
$ mkdir ifm3d
$ cd ifm3d
$ mkdir src
$ cd src
$ catkin_init_workspace
$ ln -s ~/dev/ifm3d-ros ifm3d
```

So, you should have a catkin workspace set up to build the ifm3d-ros code that
looks basically like:

```
[ ~/catkin/ifm3d/src ]
tpanzarella@tuna: $ pwd
/home/tpanzarella/catkin/ifm3d/src

[ ~/catkin/ifm3d/src ]
tpanzarella@tuna: $ ls -l
total 0
lrwxrwxrwx 1 tpanzarella tpanzarella 50 Mar 26 15:16 CMakeLists.txt -> /opt/ros/kinetic/share/catkin/cmake/toplevel.cmake
lrwxrwxrwx 1 tpanzarella tpanzarella 31 Mar 26 15:16 ifm3d -> /home/tpanzarella/dev/ifm3d-ros
```

Now we are ready to build the code.

```
$ cd ~/catkin/ifm3d
$ catkin_make
$ catkin_make -DCMAKE_INSTALL_PREFIX=${LPR_ROS}/ifm3d install
```

The ROS package should now be installed in `~/ros/ifm3d`. To test everything
out you should open a fresh bash shell, and start up a ROS core:

    $ roscore

Open another shell and start the primary camera node:

    $ roslaunch ifm3d camera.launch

Open another shell and start the rviz node to visualize the data coming from
the camera:

    $ roslaunch ifm3d rviz.launch

At this point, you should see an rviz window that looks something like:

![rviz1](doc/figures/rviz_sample.png)

Congratulations! You can now utilize ifm3d-ros.

TODO
----

Please see the [Github Issues](https://github.com/lovepark/ifm3d-ros/issues).

LICENSE
-------

Please see the file called [LICENSE](LICENSE).

AUTHORS
-------

Tom Panzarella <tom@loveparkrobotics.com>
