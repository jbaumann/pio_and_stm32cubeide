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

7. Rename any assembler files having a lower-case '.s' ending to upper-case '.S'. Otherwise you get an error "unrecognized option -x". The script points out the paths to any files that you have not yet renamed. STM32CubeIDE has no problems with this simple renaming.

For reference see the provided sample platformio.ini which you can use as the basis for your own.

# Details

Here are a few unordered details that might help you understand the inner workings of the script.

It doesn't really matter which framework you select because one of the steps to ensure that no Platformio libraries are used is to remove the framework from the build model before handing over to Platformio's build script.

The directory provided in lib_deps is created anew with each build. Here the script collects actual links to every "linked resource" found in the .project file by STM32CubeIDE. This is why it is important to choose the option "Add necessary files as reference in the toolchain project configuration file".

You actually do not have to call "platformio init". Instead you can simply copy the provided platformio.ini, correct the board definition and create the lib directory. Even the lib directory doesn't have to be created. If the lib directory is not found the script prints a warning and creates the directory anyway.

# Further information

Since this script has been tested only with a limited set of boards I would be very interested in your feedback, whether positive or negative.
