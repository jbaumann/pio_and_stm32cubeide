<will be changed>
  
# The Automatic Script using the CubeMX Libraries

This script reads the .project and .cproject file created by STM32CubeIDE and the platformio.ini file to create a build model that can be provided to platformio for building without using the libraries provided by PlatformIO. This should provide a build result comparable to that in STM32CubeIDE.

# Caveats

The script does quite a few things to ensure that platformio behaves. It tries to gather as much information as possible without manual configuration and using this information forces platformio into following a working compilation path. A very few things have to be added to the platformio.ini to allow for that. This is done only once and then the script does its work.

# Steps to use the Script

1. In STM32CubeIDE create a new project with the target and needed middleware. Configure your uC to your liking and let the IDE generate the source files. Use 
`"Add necessary files as reference in the toolchain project configuration file"`. 
This is extremely important because this is the only way that the script can derive the used library files (this data is stored in the .project file).

2. Change to the project directory and execute the following command (you can do this in your normal shell or the VSCode environment depending on your configuration).

`platformio init --board <your board config> --project-option "framework=stm32cube"`


3. PlatformIO creates additional folders most of which you probably can delete (include, lib, src, test...). I would keep them, they don't need that much space...
4. Open platformio.ini. Change the `src_dir` and the `include_dir` in the [platformio] section according to the example provided.
5. In the environment section for your board add the following

`extra_scripts = pre:setup_cubemx_env_auto.py`

`; The name of the library directory in which the linked resources will`

`; be placed`

`lib_deps = STLinkedResources`

6. Copy script `setup_cubemx_env_auto.py` to your project directory.

7. Rename any assembler files having a lower-case '.s' ending to upper-case '.S'. Otherwise you get an error "unrecognized option -x". The script points out the paths to any files that you have not yet renamed. STM32CubeIDE has no problems with this simple renaming.

9. Decide on the C library you want to use. If you choose Nano, then everything is setup already. Other possible libraries can be chosen by setting build variables. You can find the details [here](https://docs.platformio.org/en/latest/platforms/ststm32.html#stm32duino-configuration-system).

For reference see the provided sample platformio.ini which you can use as the basis for your own.

# Details

Here are a few unordered details that might help you understand the inner workings of the script.

It doesn't really matter which framework you select because one of the steps to ensure that no Platformio libraries are used is to remove the framework from the build model before handing over to Platformio's build script.

The directory provided in lib_deps is created anew with each build. Here the script collects actual links to every "linked resource" found in the .project file by STM32CubeIDE. This is why it is important to choose the option "Add necessary files as reference in the toolchain project configuration file".

You actually do not have to call "platformio init". Instead you can simply copy the provided platformio.ini, correct the board definition and create the lib directory. Even the lib directory doesn't have to be created. If the lib directory is not found the script prints a warning and creates the directory anyway.

If you forgot to select `"Add necessary files as reference in the toolchain project configuration file"` when creating your project (or when working on an already existing project) you can change this setting in the project's `.ioc` file. Go to the `Project Manager` tab, select `Code Generator` on the left side, and there you have the opportunity to select this option on a project that has so far been configured differently.

You can check that the linked resources have been added either by examining the .project file or by opening the project properties (right click on the project, menu entry at the bottom), then `Linked Resources->Linked Resoures`. There all the linked library files should be listed.

# Performance Considerations

The script changes a lot of information in platformio, but it reads only two files that it parses as XML and creates the links to the library files needed. Comparing this to the LDF which parses each source file to determine needed include files this is not much. And since we can assume that after the links are created, they are staying in the filesystem cache for a while, the following execution of the LDF will be that much faster, so in fact we won't lose much time at all through the link creation.

What remains is parsing the two project files which are typically both less than 100KB. The time to parse these and build the XML object tree should be negligible. If we assume a doubling in size when creating the xml object tree, we are still shy of 500KB in-mem representation. This might sound like quite a lot, but since we run the script on the machine on which we build the project we can assume that this should be no problem.

TLDR; Running the script should not have a relevant influence on the overall build time.

# Further information

Since this script has been tested only with a limited set of boards I would be very interested in your feedback, whether positive or negative.
