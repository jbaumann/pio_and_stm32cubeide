<will be changed>
  
# The Automatic Script using the CubeMX Libraries

This script reads the .project and .cproject file created by STM32CubeIDE and the platformio.ini file to create a build model that can be provided to platformio for building without using the libraries provided by PlatformIO. This should provide a build result comparable to that in STM32CubeIDE.

# Caveats

The script does quite a few things to ensure that platformio behaves. It tries to gather as much information as possible without manual configuration and using this information forces platformio into following a working compilation path. A very few things have to be added to the platformio.ini to allow for that. This is done only once and then the script does its work.

# Steps to use the Script

1. In STM32CubeIDE create a new project with the target and needed middleware. Configure your uC to your liking and let the IDE generate the source files. Use "Add necessary files as reference in the toolchain project configuration file". This is extremely important because this is the only way that the script can derivce the used library files (this data is stored in the .project file).

2. Change to the project directory and execute the following command (you can do this in your normal shell or the VSCode environment depending on your configuration).

`platformio init --board <your board config> --project-option "framework=stm32cube"`


3. PlatformIO creates additional folders most of which you probably can delete (include, lib, src, test...). I would keep them, they don't need that much space...
4. Open platformio.ini. Change the `src_dir` and the `include_dir` in the [platformio] section according to the example provided.
5. In the environment section for your board add the following

`extra_scripts = pre:setup_cubemx_env_auto.py`

`;The project option containing the directory in which CubeMX resides`

`custom_repo_location = ~`

`; The name of the library directory in which the linked resources will`

`; be placed`

`lib_deps = STLinkedResources`

6. Copy script `setup_cubemx_env_auto.py` to your project directory.

For reference see the provided sample platformio.ini which you can use as the basis for your own.

# Details

framework is deleted
.s to .S
linked resources 

You actually can skip this step and simply place the platformio.ini file into the directory and create the lib directory.


# Further information

Since this script has been tested only with a limited set of boards I would be very interested in your feedback, whether positive or negative.
