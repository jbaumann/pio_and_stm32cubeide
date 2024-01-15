# The Automatic Script using PIO Libraries

Developing for STM32 until now provided 2 major and distinct paths: Either you use STM32CubeIDE with the manufacturer support or you use PlatformIO with its unique way of supporting developers.

The script provided here offers a middleground, using the source from the STM32CubeIDE combined with the CubeMX libraries provided by platformio. 

Warning: These are outdated and kept as a reference only.

# Steps to use the scripts

1. In STM32CubeIDE create a new project with the target and needed middleware. Configure your uC to your liking and let the IDE generate the source files. Use "Copy only necessary library files".
2. Change to the project directory and execute the following command (you can do this in your normal shell or the VSCode environment depending on your configuration).

`platformio init --board <your board config> --project-option "framework=stm32cube"`

3. PlatformIO creates additional folders most of which you probably can delete (include, lib, src, test...). I would keep them, they don't need that much space...
4. Open platformio.ini. Change the `src_dir` and the `include_dir` in the [platformio] section.
5. Copy one of the setup scripts to your project directory.
6. Add the script to your board environment. Either use the manual script or the automatic script with the following line (example contains the automatic script):

`extra_scripts = pre:setup_cubemx_env_auto.py`

For reference see the provided sample platformio.ini which you can use as the basis for your own.

# Further information

The manual script is heavily influenced by the following script: https://community.platformio.org/t/using-stm32cubemx-and-platformio/2611/57

Since this script has been tested only with a limited set of boards I would be very interested in your feedback, whether positive or negative.
