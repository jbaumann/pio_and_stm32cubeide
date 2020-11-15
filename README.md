# Integration of PlatformIO and STM32CubeIDE

Developing for STM32 until now provided 2 major and distinct paths: Either you use STM32CubeIDE with the manufacturer support or you use PlatformIO with its unique way of supporting developers.

The scripts provided here change that. 

## Automatic CubeMX

This is the preferred way to build (mine anyways). The .project and .cproject file created by STM32CubeIDE and the board information provided in platformio.ini are used to create a build model that is then used by PlatformIO to build the project with the libraries provided by STM32CubeIDE. None of the PlatformIO libraries for CubeMX are used.

## Automatic PIO

This automatic script tries to derive the necessary information from the project's .cproject file, sets up everything and the lets Platformio build using the CubeMX libraries that it provides. These might be slightly outdated.

## Manual

This manual script is heavily influenced by the following script: https://community.platformio.org/t/using-stm32cubemx-and-platformio/2611/57

You configure everything from hand at the top of the script and the build is done using the CubeMX libraries that Platformio provides. These might be slightly outdated.
