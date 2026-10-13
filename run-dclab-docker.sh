#!/bin/bash

REPO="koniot/dclab_docker"
WORKSPACE="$HOME/demo_bot"

# Directory containing this script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ------------------------------------------------------------

# WSL2 Windows-drive relocation
#
# Windows drives (/mnt/c, /mnt/d, ...) are mounted with noexec under
# WSL2 by default - scripts and offline .tar loads work fine on paper
# but fail with "Permission denied" no matter what chmod says (Tested this on lyheng's),
# because the mount itself blocks execution, not the file's own permission
# bits. If this script is running from one of those mounts under WSL2,
# copy the whole folder into the Linux filesystem ($HOME) and re-launch
# itself from there automatically, instead of failing partway through.

# ------------------------------------------------------------

if grep -qi microsoft /proc/version 2>/dev/null \
    && [[ "$SCRIPT_DIR" =~ ^/mnt/[a-zA-Z](/|$) ]]; then

    NEW_DIR="$HOME/$(basename "$SCRIPT_DIR")"

    echo "Detected this script running from a Windows drive under WSL2:"
    echo "  $SCRIPT_DIR"
    echo
    echo "Windows drives are mounted noexec in WSL2, which breaks script"
    echo "and offline-image execution no matter what chmod says."
    echo
    echo "Copying this folder to the Linux filesystem:"
    echo "  $NEW_DIR"
    echo "and re-running from there..."
    echo

    mkdir -p "$NEW_DIR"
    cp -a "$SCRIPT_DIR/." "$NEW_DIR/"
    chmod +x "$NEW_DIR/$(basename "${BASH_SOURCE[0]}")"

    exec "$NEW_DIR/$(basename "${BASH_SOURCE[0]}")" "$@"
fi

# ------------------------------------------------------------

# Docker check

# ------------------------------------------------------------

if ! command -v docker &> /dev/null; then
echo "Error: Docker is not installed."
exit 1
fi

# ------------------------------------------------------------

# Detect architecture

# ------------------------------------------------------------

ARCH=$(uname -m)
OS_TYPE=$(uname -s)

case "$ARCH" in
x86_64)
PLATFORM="amd64"
;;
aarch64|arm64)
PLATFORM="arm64"
;;
*)
echo "Error: Unsupported architecture: $ARCH"
exit 1
;;
esac

# ------------------------------------------------------------

# Select DCLab Docker version

# ------------------------------------------------------------

echo
echo "========================================"
echo "       DCLab ROS 2 Docker Launcher"
echo "========================================"
echo
echo "Detected architecture: $PLATFORM"
echo
echo "Select Docker version:"
echo
echo "1) humble"
echo "   Ubuntu 22.04 + ROS 2 Humble + Rviz2 + Gazebo"
echo
echo "2) humble-lite"
echo "   Ubuntu 22.04 + ROS 2 Humble + Rviz2"
echo
echo "3) jazzy"
echo "   Ubuntu 24.04 + ROS 2 Jazzy + Rviz2 + Gazebo"
echo
echo "4) jazzy-lite"
echo "   Ubuntu 24.04 + ROS 2 Jazzy + Rviz2"
echo
echo "5) lyrical"
echo "   Ubuntu 26.04 + ROS 2 Lyrical + Rviz2 + Gazebo"
echo
echo "6) lyrical-lite"
echo "   Ubuntu 26.04 + ROS 2 Lyrical + Rviz2"
echo
while true; do
read -rp "Select version [1-6]: " VERSION_CHOICE

case "$VERSION_CHOICE" in
    1)
	TAG="humble"
        break
        ;;
    2)
	TAG="humble-lite"
        break
        ;;
    3)
	TAG="jazzy"
        break
        ;;
    4)
	TAG="jazzy-lite"
        break
        ;;
    5)
	TAG="lyrical"
	break
	;;
    6)
	TAG="lyrical-lite"
	break
	;;
    *)
        echo "Hort mes ಠ_ಠ ,  Please enter 1, 2, 3, 4, 5 or 6."
        ;;
esac

done

IMAGE="$REPO:$TAG"
TAR_FILE="$SCRIPT_DIR/dclab_docker_${TAG}_${PLATFORM}.tar"

# ------------------------------------------------------------

# Workspace setup

# ------------------------------------------------------------

if [ ! -d "$WORKSPACE" ]; then
    echo "Cloning demo_bot workspace..."
    git clone https://github.com/c-lydia/demo_bot.git "$WORKSPACE"
else
    echo "demo_bot workspace already exists"
fi

# ------------------------------------------------------------

# Check whether selected image already exists

# ------------------------------------------------------------

if docker image inspect "$IMAGE" &> /dev/null; then

echo
echo "DCLab Docker image found locally."
echo "Using: $IMAGE"


else

echo
echo "========================================"
echo "      DCLab Docker Image Source"
echo "========================================"
echo
echo "Selected image: $IMAGE"
echo "Architecture:   $PLATFORM"
echo
echo "1) Pull image from Docker Hub"
echo "2) Load matching offline .tar file"
echo

while true; do
    read -rp "Select image source [1/2]: " IMAGE_SOURCE

    case "$IMAGE_SOURCE" in

        1)
            echo
            echo "Pulling $IMAGE from Docker Hub..."
            echo

            if ! docker pull "$IMAGE"; then
                echo
                echo "Error: Failed to pull $IMAGE from Docker Hub."
                exit 1
            fi

            break
            ;;

        2)
            echo

            if [ ! -f "$TAR_FILE" ]; then
                echo "Error: Matching offline image not found:"
                echo
                echo "  $TAR_FILE"
                echo
                echo "Expected filename:"
                echo "  dclab_docker_${TAG}_${PLATFORM}.tar"
                echo
                echo "Make sure the correct .tar file is in the"
                echo "same directory as this script."
                exit 1
            fi

            TAR_SIZE=$(du -h "$TAR_FILE" | cut -f1)

            echo "Loading DCLab Docker image from:"
            echo "  $TAR_FILE"
            echo "  Size: $TAR_SIZE"
            echo

            # Check for pv
            if command -v pv &> /dev/null; then

                echo "Loading image..."
                echo

                if ! pv "$TAR_FILE" | docker load; then
                    echo
                    echo "Error: Failed to load the Docker image."
                    exit 1
                fi

            else

                echo "Loading image..."
                echo

                if ! docker load -i "$TAR_FILE"; then
                    echo
                    echo "Error: Failed to load the Docker image."
                    exit 1
                fi

            fi

            echo
            echo "Docker image loaded successfully."
            break
            ;;

        *)
            echo "Invalid choice. Please enter 1 or 2."
            ;;
    esac
done

fi

# ------------------------------------------------------------

# X11 / XWayland setup

# ------------------------------------------------------------

echo
echo "Setting up X11 access..."

if [ "$OS_TYPE" = "Darwin" ]; then
    # macOS has no built-in X server or xhost. XQuartz provides both, but
    # ships its own xhost at /opt/X11/bin - add it to PATH for this run
    # in case it's not already there.
    export PATH="/opt/X11/bin:$PATH"

    if ! command -v xhost &> /dev/null; then
        echo "xhost not found - XQuartz doesn't appear to be installed."
        echo
        echo "Install it with:"
        echo "  brew install --cask xquartz"
        echo "then log out and back in (XQuartz only takes effect after a"
        echo "fresh login), open XQuartz once, go to XQuartz > Settings >"
        echo "Security, and enable 'Allow connections from network clients'."
        echo "Re-run this script after that."
        exit 1
    fi

    # macOS doesn't export DISPLAY the way Linux does - default to :0
    # (XQuartz's default) if nothing is set.
    if [ -z "$DISPLAY" ]; then
        export DISPLAY=:0
    fi

    # No shared local X11 socket across the Docker Desktop VM boundary,
    # so "local:" grants (used on native Linux) don't apply here - grant
    # access from the container's view of the host loopback instead.
    xhost + 127.0.0.1 &> /dev/null
    XHOST_ENABLED=true
    echo "X11 access granted for 127.0.0.1. DISPLAY=$DISPLAY"
    echo "(Container will connect back to XQuartz via host.docker.internal)"

else

if ! command -v xhost &> /dev/null; then
echo "xhost not found."
echo

if command -v apt-get &> /dev/null; then
    echo "Installing x11-xserver-utils..."
    sudo apt-get update
    sudo apt-get install -y x11-xserver-utils

elif command -v pacman &> /dev/null; then
    echo "Installing xorg-xhost..."
    sudo pacman -S --noconfirm xorg-xhost

else
    echo "Warning: Could not determine package manager."
fi


fi

if command -v xhost &> /dev/null; then
xhost +local:
XHOST_ENABLED=true
echo "X11 access granted. DISPLAY=$DISPLAY"
else
echo "Warning: xhost is not available."
echo "RViz2/Gazebo display access may fail."
XHOST_ENABLED=false
fi

fi

# ------------------------------------------------------------

# Cleanup X11 permission

# ------------------------------------------------------------

cleanup() {
if [ "$XHOST_ENABLED" = true ]; then
if [ "$OS_TYPE" = "Darwin" ]; then
    xhost - 127.0.0.1 &> /dev/null
else
    xhost -local:docker &> /dev/null
fi
fi
if [ -n "$VNCVIEWER_PID" ]; then
kill "$VNCVIEWER_PID" &> /dev/null
fi
}

trap cleanup EXIT

# ------------------------------------------------------------

# Docker run arguments

# ------------------------------------------------------------

if [ "$OS_TYPE" = "Darwin" ]; then
    # Docker Desktop for Mac runs containers inside a hidden Linux VM -
    # there's no shared host network namespace to join, so --network host
    # doesn't behave the same way it does on native Linux. DISPLAY points
    # at host.docker.internal instead of the host's own $DISPLAY, since
    # the container needs to reach XQuartz through the VM boundary rather
    # than a local socket.
    DOCKER_ARGS=(
    -it
    --rm
    --name dclab_docker
    --hostname dclab-ros2
    --ipc host

    -e DISPLAY=host.docker.internal:0
    -e XDG_RUNTIME_DIR=/tmp/runtime-dclab
    -e QT_X11_NO_MITSHM=1

    -v "$WORKSPACE:/home/dclab_docker/ros2_ws"
    )

    # No --network host on macOS, so the container's internal VNC and SSH
    # ports need to be explicitly published to reach them from the Mac side.
    DOCKER_ARGS+=(-p 127.0.0.1:5900:5900 -p 127.0.0.1:2222:2222)
else
DOCKER_ARGS=(
-it
--rm
--name dclab_docker
--hostname dclab-ros2
--ipc host

-e DISPLAY="$DISPLAY"
-e XDG_RUNTIME_DIR=/tmp/runtime-dclab
-e QT_X11_NO_MITSHM=1

-v /tmp/.X11-unix:/tmp/.X11-unix:rw
-v "$WORKSPACE:/home/dclab_docker/ros2_ws"
-p 127.0.0.1:5900:5900
-p 127.0.0.1:2222:2222
)
fi

# ------------------------------------------------------------

# GPU device
#
# Native Linux:
# /dev/dri exists and is passed to the container.
#
# WSL2 / Jetson-Tegra:
# /dev/dri normally does not exist, so it is skipped, and any
# NVIDIA runtime GPU args below are also skipped for this run -
# mixing NVIDIA's GLVND libraries with forced software rendering
# causes GLX FBConfig failures instead of falling back cleanly.
# Don't know how this would behave on macOS yet ;-;

# ------------------------------------------------------------

if [ -e /dev/dri ]; then
echo "Detected /dev/dri - enabling GPU device."
DOCKER_ARGS+=(--device /dev/dri)
NEEDS_SOFTWARE_GL=false
else
echo "No /dev/dri detected - continuing without it."
echo "Forcing software (CPU) OpenGL rendering for RViz2/Qt, since"
echo "hardware GLX passthrough (e.g. on Jetson/Tegra) isn't available"
echo "in this image. Rendering will be slower but should work."
DOCKER_ARGS+=(
    -e LIBGL_ALWAYS_SOFTWARE=1
    -e GALLIUM_DRIVER=llvmpipe
    -e MESA_GL_VERSION_OVERRIDE=4.5
    -e MESA_GLSL_VERSION_OVERRIDE=450
    -e __GLX_VENDOR_LIBRARY_NAME=mesa
    -e OGRE_RTT_MODE=Copy
    -e QSG_RENDER_LOOP=basic
)
NEEDS_SOFTWARE_GL=true
fi

# ------------------------------------------------------------

# NVIDIA GPU support
#
# Skipped entirely when NEEDS_SOFTWARE_GL is true:
# ------------------------------------------------------------

if [ "$NEEDS_SOFTWARE_GL" = false ] && docker info 2>/dev/null | grep -q "nvidia"; then
echo "NVIDIA Docker runtime detected."
if command -v nvidia-smi &> /dev/null; then
GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -n1)
if [ -n "$GPU_NAME" ]; then
    echo "GPU: $GPU_NAME"
fi
fi
DOCKER_ARGS+=(
--gpus all
-e NVIDIA_VISIBLE_DEVICES=all
-e NVIDIA_DRIVER_CAPABILITIES=all
)
else
echo "NVIDIA Docker runtime not used for this run."
fi

# ------------------------------------------------------------

# Start container

# ------------------------------------------------------------

echo
echo "========================================"
echo "Starting DCLab Docker container"
echo "========================================"
echo
echo "Image:        $IMAGE"
echo "Architecture: $PLATFORM"
echo "Workspace:    $WORKSPACE"
echo
echo "SSH will be started automatically inside the container (port 2222)."
echo "Connect with: ssh dclab_docker@localhost -p 2222  (password: 123)"
echo

if [ "$NEEDS_SOFTWARE_GL" = true ]; then
    echo "No working host GLX passthrough for this display - using a"
    echo "self-contained virtual display + VNC instead."
    echo
    echo "Once the container starts, connect a VNC viewer to:"
    echo "  localhost:5900"
    echo "(if viewing from another machine, use an SSH tunnel:"
    echo "  ssh -L 5900:localhost:5900 <user>@<this-host>"
    echo "then point your VNC viewer at localhost:5900 there instead)"
    echo
    if [ "$OS_TYPE" = "Darwin" ]; then
        echo "Will launch a VNC viewer automatically once the VNC server is ready"
        echo "(may take a bit longer on first run, while packages install)..."
        (
            for i in $(seq 1 90); do
                if (exec 3<>/dev/tcp/127.0.0.1/5900) &> /dev/null; then
                    exec 3>&- 3<&-
                    if ! open "vnc://localhost:5900" >/tmp/vncviewer.log 2>&1; then
                        echo "Screen Sharing auto-launch failed - falling back to TigerVNC." >> /tmp/vncviewer.log
                        if ! command -v vncviewer &> /dev/null; then
                            if command -v brew &> /dev/null; then
                                echo "Installing TigerVNC viewer..." >> /tmp/vncviewer.log
                                brew install --cask tigervnc-viewer >> /tmp/vncviewer.log 2>&1
                            else
                                echo "Homebrew not found - install TigerVNC manually:" >> /tmp/vncviewer.log
                                echo "  brew install --cask tigervnc-viewer" >> /tmp/vncviewer.log
                                echo "or connect any VNC client to localhost:5900." >> /tmp/vncviewer.log
                            fi
                        fi
                        if command -v vncviewer &> /dev/null; then
                            vncviewer localhost:5900 >> /tmp/vncviewer.log 2>&1
                        fi
                    fi
                    break
                fi
                sleep 1
            done
        ) &
        VNCVIEWER_PID=$!
    elif command -v vncviewer &> /dev/null; then
        echo "Will launch vncviewer automatically once the VNC server is ready"
        echo "(may take a bit longer on first run, while packages install)..."
        (
            for i in $(seq 1 90); do
                if (exec 3<>/dev/tcp/127.0.0.1/5900) &> /dev/null; then
                    exec 3>&- 3<&-
                    vncviewer localhost:5900 >/tmp/vncviewer.log 2>&1
                    break
                fi
                sleep 1
            done
        ) &
        VNCVIEWER_PID=$!
    else
        echo "vncviewer not found - install it once with:"
        echo "  sudo apt install tigervnc-viewer"
        echo "then run 'vncviewer localhost:5900' manually after the container starts."
    fi

    docker run "${DOCKER_ARGS[@]}" --user root "$IMAGE" bash -c '
        if ! dpkg -s xvfb x11vnc fluxbox >/dev/null 2>&1; then
            echo "Installing virtual display packages (xvfb, x11vnc, fluxbox, mesa)..."
            apt-get update -qq && apt-get install -y -qq \
                xvfb x11vnc fluxbox mesa-utils libgl1-mesa-dri libglx-mesa0
        fi
	rm -f /tmp/.X*-lock /tmp/.X11-unix/X* 2>/dev/null || true
	mkdir -p /tmp/.X11-unix
	chmod 1777 /tmp/.X11-unix
	echo "Starting Xvfb on :99..."
        Xvfb :99 -screen 0 1280x800x24 -ac +extension GLX +render -noreset > /tmp/Xvfb.log 2>&1 &
        sleep 2
        export DISPLAY=:99
	echo "Starting fluxbox..."
        fluxbox >/tmp/fluxbox.log 2>&1 &
	echo "Starting x11vnc on port 5900..."
        x11vnc -display :99 -forever -shared -nopw -rfbport 5900 >/tmp/x11vnc.log
	echo "Starting SSH..."
        mkdir -p /run/sshd
        service ssh start >/tmp/sshd.log 2>&1
	echo "======================================================"
	echo "VNC should now be available on localhost:5900"
	echo "SSH: ssh dclab_docker@localhost -p 2222 (password: 123)"
	echo "======================================================"
        exec su dclab_docker
    '
else
    # mesa-utils (glxinfo, glxgears) isn't in the base image (TO BE FIXED LATERRR) but is handy
    # for quickly checking GPU passthrough/rendering if something looks
    # wrong later. Installed once as root if missing, then hands off to
    # the normal dclab_docker user shell.
    docker run "${DOCKER_ARGS[@]}" --user root "$IMAGE" bash -c "
        if ! dpkg -s mesa-utils >/dev/null 2>&1; then
            echo 'Installing mesa-utils (glxinfo, glxgears) for GPU diagnostics...'
            apt-get update -qq && apt-get install -y -qq mesa-utils
        fi
        mkdir -p /run/sshd
        service ssh start >/tmp/sshd.log 2>&1
        exec su dclab_docker
    "
fi
