# Integration of PlatformIO and STM32CubeIDE

Developing for STM32 until now provided 2 major and distinct paths: Either you use STM32CubeIDE with the manufacturer support or you use PlatformIO with its unique way of supporting developers.

The scripts provided here change that. One script is configured manually, and you have the full control over the compiled sources, the other is collecting everything automatically from the project configuration files that both PlatformIO and STM32CubeIDE provide.

# Steps to use the scripts

1. In STM32CubeIDE create a new project with the target and needed middleware. Configure your uC to your liking and let the IDE generate the source files. Use "Copy only necessary library files".
2. Change to the project directory and execute the following command (you can do this in your normal shell or the VSCode environment depending on your configuration).

`pio init --<your board config> --project-option "framework=stm32cube"`

3. PlatformIO creates additional folders which you can delete.
4. Open platformio.ini. Change the `src_dir` and the `include_dir` in the [platformio] section.
5. Copy one of the setup scripts to your project directory.
6. Add the script to your board environment. Either use the manual script or the automatic script with the following line (example contains the automatic script):

`extra_scripts = pre:setup_cubemx_env_auto.py`

6. If you use the automatic script you are done and can run your first compilation. If you use the manual script, then you have to edit it and adjust the directories that the STM32CubeIDE has created and adjust the build flags. You can find the build flags in the project configuration tab in the STM32CubeIDE.

For reference see the provided sample platformio.ini which you can use as the basis for your own.

# Further information

The manual script is heavily influenced by the following script: https://community.platformio.org/t/using-stm32cubemx-and-platformio/2611/57

Since this script has been tested only with a limited set of boards I would be very interested in your feedback, whether positive or negative.
