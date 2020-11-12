# Author: Joachim Baumann
#
# This script is based on the script provided here:
# https://community.platformio.org/t/using-stm32cubemx-and-platformio/2611/57
# 
# and on the information for advanced scripting provided by platformio
# https://docs.platformio.org/en/latest/projectconf/advanced_scripting.html
#
# There are two distinct steps involved, first of all collect all directories
# that have to be included into the build. This part is generic and can be 
# used for every series
# Second, set up all the build and linker flags for compiler and linker. These
# flags are highly specific for every different series. The best way to derive
# them is by looking at the compiler and linker options configured for the
# STM32CubeIDE project in its settings.


# These are the additional directories needed for a successful compilation
# Do not add the Core directory here, this would lead to compilation problems
cubemx_directories = set()
cubemx_directories.add('Middlewares')
cubemx_directories.add('Drivers')


# These flags are specific for the STM32F4 series. The variable build_flags
# contains the flags that are provided to both compiler and linker, 
# cc_flags the flags that are only provided to the compiler (which then 
# will forward them if needed).
build_flags = [
    # we always choose thumb mode with STM32
    "-mthumb",
    "-mcpu=cortex-m4",
    "-mfloat-abi=hard",
    "-mfpu=fpv4-sp-d16",
]
# additional flags for the compiler only
#cc_only_flags = [
    # These are already set by platformio, see
    # PIO_FRAMEWORK_ARDUINO_STANDARD_LIB
    #"--specs=nano.specs",
    #"--specs=nosys.specs",
#]


####################################
# Here be dragons
####################################
from os import path, walk

Import("env")

# In these lists we collect our directories
src_dirs = set()
include_dirs = set()

for cubemx_dir in cubemx_directories:
    if not path.exists(cubemx_dir):
        # we ignore non-existing directories
        continue
    # For every source file we add its path to either src_dirs or include_dirs
    for dirpath, dirnames, filenames in walk(cubemx_dir, followlinks=True):
        for file in filenames:
            if file.endswith(('.c', '.cpp', '.s')):
                src_dirs.add(dirpath)
            if file.endswith(('.h', '.hpp')):
                include_dirs.add(dirpath)

# Build the src_filter
if not 'SRC_FILTER' in env:
    env['SRC_FILTER'] = []
# we explicitly add the Core files
env['SRC_FILTER'] += ['+<Core/Src/>']
# Now we add the collected source directories to the src_filter
env['SRC_FILTER'] += ['+<%s/>' % src_dir for src_dir in src_dirs]

# Create the list of all needed include directories that we have collected
if not 'BUILD_FLAGS' in env:
    env['BUILD_FLAGS'] = []
# Add the collected include directories to the build_flags
env['BUILD_FLAGS'] += ['-I' + include_dir for include_dir in include_dirs]

# Add the necessary build flags to compiler and linker flags. 
#env['BUILD_FLAGS'] += cc_only_flags
env['BUILD_FLAGS'] += build_flags
env["LINKFLAGS"] += build_flags
