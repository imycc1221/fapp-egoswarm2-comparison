# Docker setup for FAPP (ROS Noetic)
# Fast and Adaptive Perception and Planning for UAVs

FROM ros:noetic

# Build argument for cache-busting when using make build-clone
ARG DUMMY=unknown

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=noetic
ENV DISABLE_ROS1_EOL_WARNINGS=1

# Install system utilities
RUN apt-get update && apt-get install -y \
    git \
    wget \
    tmux \
    vim \
    python3 \
    python3-pip \
    ffmpeg \
    x11-utils \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install tmuxp for session automation
RUN pip3 install tmuxp

# Install ROS packages
RUN apt-get update && apt-get install -y \
    ros-noetic-cv-bridge \
    ros-noetic-image-transport \
    ros-noetic-pcl-ros \
    ros-noetic-pcl-conversions \
    ros-noetic-tf \
    ros-noetic-dynamic-reconfigure \
    ros-noetic-nodelet \
    ros-noetic-rviz \
    ros-noetic-message-filters \
    ros-noetic-cmake-modules \
    python3-catkin-tools \
    && rm -rf /var/lib/apt/lists/*

# Install C++ libraries
RUN apt-get update && apt-get install -y \
    libeigen3-dev \
    libopencv-dev \
    libpcl-dev \
    libarmadillo-dev \
    qtbase5-dev \
    libboost-filesystem-dev \
    libboost-system-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install numpy pyyaml

# Create workspace directory
RUN mkdir -p /root/fapp_ws/src

# Copy FAPP source into workspace
COPY FAPP /root/fapp_ws/src/FAPP

# Eigen symlink fix (some packages include <Eigen/...> instead of <eigen3/Eigen/...>)
RUN ln -sf /usr/include/eigen3/Eigen /usr/include/Eigen

# Python3 symlink
RUN ln -sf /usr/bin/python3 /usr/local/bin/python

# Build message packages first (obj_state_msgs, quadrotor_msgs)
RUN cd /root/fapp_ws && \
    /bin/bash -c "source /opt/ros/noetic/setup.bash && \
    catkin_make --only-pkg-with-deps obj_state_msgs quadrotor_msgs"

# Build the full workspace (clear whitelist from previous step)
RUN cd /root/fapp_ws && \
    /bin/bash -c "source /opt/ros/noetic/setup.bash && catkin_make -j3 -DCATKIN_WHITELIST_PACKAGES=''"

# Setup ROS environment in .bashrc
RUN echo "source /opt/ros/noetic/setup.bash" >> /root/.bashrc && \
    echo "source /root/fapp_ws/devel/setup.bash" >> /root/.bashrc && \
    echo "export ROS_MASTER_URI=http://localhost:11311" >> /root/.bashrc && \
    echo "export ROS_IP=127.0.0.1" >> /root/.bashrc && \
    echo "alias tks='tmux kill-session'" >> /root/.bashrc

# Set working directory
WORKDIR /root/fapp_ws

# Default command
CMD ["/bin/bash"]
