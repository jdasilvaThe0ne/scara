from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch.actions import TimerAction # <--- Add this

def generate_launch_description():

    robot_description = Command([
        'xacro ',
        '/home/justinodasilva/arm/src/last_scara_arm/urdf/scara.urdf.xacro'
    ])
    

    # 1. Robot State Publisher
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description},
                    {'use_sim_time':True}
                    ],
    )
    #2 clock bridge
    node_gz_bridge=Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            #'/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/world/science_lab/model/world_camera/link/camera_link/sensor/camera_sensor/image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/world/science_lab/model/world_camera/link/camera_link/sensor/camera_sensor/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo'
            ],
            remappings=[
                ('/world/science_lab/model/world_camera/link/camera_link/sensor/camera_sensor/image', '/camera/image_raw'),
                ('/world/science_lab/model/world_camera/link/camera_link/sensor/camera_sensor/camera_info', '/camera/camera_info')
                ],

        output='screen'     
    )

    # 3. Spawn the robot into Gazebo
    node_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-entity', 'scara_robot', '-x','0.5','-z', '0.1'],
        output='screen'
    )

    # 3. Spawner (Delayed by 10 seconds)
    node_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['arm_controller','--ros-args','-p','use_sim_time:=true'],

    )
    node_jsb_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--ros-args', '-p', 'use_sim_time:=true'],
)


    return LaunchDescription([
        node_robot_state_publisher,
        node_spawn_entity,
        node_gz_bridge,
        
        # This wraps the spawner in a 10-second delay
        TimerAction(
            period=10.0,
            actions=[node_controller_spawner,node_jsb_spawner,],
        ),
    ])