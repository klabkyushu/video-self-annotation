from setuptools import setup, find_packages

setup(
    name='video-self-annotation',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'ninja',
        'yacs',
        'cython',
        'matplotlib',
        'tqdm',
        'opencv-python',
        'opencv-contrib-python',
        'scipy',
        'scikit-learn==0.22.2',
        'easydict',
        'shapely',
        'tensorboardX',
        'tensorboard',
        'tensorboard_logger',
        'future',
        'visdom'
    ],
    entry_points='''
        [console_scripts]
        annotate=cli:root_cmd
    ''',
)