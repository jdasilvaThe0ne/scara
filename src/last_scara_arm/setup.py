from setuptools import find_packages, setup
import os
from glob import glob


package_name = 'last_scara_arm'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share',package_name,'urdf'),glob('urdf/*')),
        (os.path.join('share',package_name,'world'),glob('world/*.sdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='justinodasilva',
    maintainer_email='jdasilvaThe0ne@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'movePetri = last_scara_arm.movePetri:main',
            'petriDishMover = last_scara_arm.petriDishMover:main',
            'movingaparatus = last_scara_arm.movingaparatus:main',
        ],
    },
)
