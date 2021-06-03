# Author: Joachim Baumann
# Version: 1.0.2
#
# This script is based on the information for advanced scripting provided
# by platformio
# https://docs.platformio.org/en/latest/projectconf/advanced_scripting.html
#
# We try to get all needed information from the .cproject file, collect all
# source directories from that to create the src_filter and read platformio's
# own board definition to glean the cpu type.

import shutil
from os import mkdir, path, symlink, walk
import SCons.Errors
import xml.etree.ElementTree as ET
import re

Import("env")
project_dir = env["PROJECT_DIR"]
log_name = "SETUP_CUBEMX"
lib_directory = "lib/"

# The project option containing the directory in which CubeMX resides
# try:
#    repository_location = env.GetProjectOption("custom_repo_location")
# except:
#    repository_location = "~"
#    pass
#repository_location = path.expanduser(repository_location)
# print("%s: Using the following repository location: '%s'"
#      % (log_name, repository_location))

# set the project source dir
env["PROJECT_SRC_DIR"] = project_dir

# We simply take the first extra library dependency
try:
    linked_resources_dir = lib_directory + env.GetProjectOption("lib_deps")[0]
except:
    raise SCons.Errors.BuildError(
        errstr="%s Error: The option 'lib_deps' is not set"
        % log_name)

#################################################
# Open the .project file and parse it as XML
#################################################
try:
    project_root = ET.parse('.project').getroot()
except IOError as error:
    raise SCons.Errors.BuildError(
        errstr="%s Error: Cannot open project file .project in directory '%s'"
        % (log_name, project_dir))

# Delete the folder STLinkedResources
try:
    shutil.rmtree(linked_resources_dir)
except FileNotFoundError:
    pass

# now create the directory and link all the needed files
if not path.exists(lib_directory):
    print("%s: Warning - Directory '%s' doesn't exist. Did you initialize platformio?"
          % (log_name, lib_directory))
    mkdir(lib_directory)
mkdir(linked_resources_dir)

# Collect the virtual dirs so that we later know not to add them
virtual_dirs = []
for linked_resource in project_root.findall(".//linkedResources/link"):
    # Retrieve the complete link
    linkedName = linked_resource.find(".//name").text
    linkedURI = linked_resource.find(".//locationURI").text
    # It's a virtual folder?
    if linkedURI == "virtual:/virtual":
        # Add to virtual_dirs in case of virtual folder
        virtual_dirs.append(linkedName)
        continue
    # It's a relative path?
    m = re.match("PARENT-(\d+)-PROJECT_LOC(.*)$", linkedURI)
    if m is not None:
        parent_level = int(m.group(1))
        current_dir = project_dir + "/.." * parent_level
        resource = path.abspath(current_dir + m.group(2))
        # print(resource)
    else:
        # we have a path type that we haven't seen yet
        raise SCons.Errors.BuildError(
            errstr="%s Error: Unexpected relative path type '%s'"
            % (log_name, linkedURI))

    try:
        resource_name = path.basename(resource)
        link_name = linked_resources_dir + "/" + resource_name
        symlink(resource, link_name)
    except OSError:
        print(resource_name)
        raise SCons.Errors.BuildError(
            errstr="%s Error: Cannot create symlink in directory '%s'"
            % (log_name, linked_resources_dir))

#################################################
# Open the .cproject file and parse it as XML
#################################################
try:
    cproject_root = ET.parse('.cproject').getroot()
except IOError as error:
    raise SCons.Errors.BuildError(
        errstr="%s Error: Cannot open project file .cproject in directory '%s'"
        % (log_name, project_dir))

# In these lists we collect our directories
src_dirs = set()
include_dirs = []

#################################################
# read the source directories from .cproject
# and scan their subdirectories for source files
#################################################
cubemx_directories = set()
cubemx_directories.add("Core/Startup")

config = cproject_root.find(".//configuration[@name='Debug']")

for source_entry in config.findall("sourceEntries/entry"):
    directory = source_entry.get('name')
    if directory != "Core":
        # Add non-virtual folders
        if directory not in virtual_dirs:
            cubemx_directories.add(directory)
if cubemx_directories:
    print("%s: Using the following source directories: 'Core, %s'"
          % (log_name, ', '.join(cubemx_directories)))
else:
    raise SCons.Errors.BuildError(
        errstr="%s Error: Cannot read source directories from project file "
        ".cproject in directory '%s'" % (log_name, project_dir))


for cubemx_dir in cubemx_directories:
    if not path.exists(cubemx_dir):
        # we ignore non-existing directories
        continue
    # For every source file we add its path to either src_dirs or include_dirs
    for dirpath, dirnames, filenames in walk(cubemx_dir, followlinks=True):
        for file in filenames:
            if file.endswith(('.c', '.cpp', '.s', '.S')):
                src_dirs.add('+<%s/>' % dirpath)
                if file.endswith('.s'):
                    print("%s: file '%s/%s'" % (log_name, dirpath, file))
                    print(" - lower case ending for assembler file might lead"
                          " to error \"unrecognized option '-x'\"")

#################################################
# now read the include dirs from .cproject
#################################################
tool_chain = config.find("./folderInfo/toolChain")

ws_replacement = re.escape(project_dir) + '/\\1'

for include_entry in tool_chain.findall(".//option[@superClass='com.st.stm32cube.ide.mcu.gnu.managedbuild.tool.c.compiler.option.includepaths']/listOptionValue"):
    inc_dir = include_entry.get('value')
    # add project-related paths e.g., Middleware-directores
    inc_dir = re.sub(
        '"\$\{workspace_loc:/\$\{ProjName\}(.*)}"', ws_replacement, inc_dir)
    # Fix references to Core
    inc_dir = inc_dir.replace("../", "", 1)
    # print(inc_dir)
    inc_dir = "-I" + inc_dir
    include_dirs.append(inc_dir)
if not include_dirs:
    raise SCons.Errors.BuildError(
        errstr="%s Error: Cannot read include directories from project file "
        ".cproject in directory '%s'" % (log_name, project_dir))

#################################################
# We now try to extract the uC-specific build
# flags and add the ones we know are needed.
# We differentiate between flags for both
# compiler and linke (build_flags) and flags
# for the compiler only (cc_only_flags)
#################################################
build_flags = [
    # we always choose thumb mode with STM32
    "-mthumb",
]
# additional flags for the compiler only
cc_only_flags = [
    # These are set by platformio, see
    # PIO_FRAMEWORK_ARDUINO_STANDARD_LIB
    # additional ones can be added using build flags
]

# additional flags for the linker only
ld_only_flags = [
]

# extract the cpu type from the board
board_config = env.BoardConfig()
cpu = board_config._manifest["build"]["cpu"]
m_flags = ['-mcpu=%s' % cpu]

# extract other flags from the .cproject file
option_mapping = {
    "floatabi": "float-abi",
}
cc_only_option_mapping = {
    "runtimelibrary_c"
}

for option in tool_chain.findall("option[@valueType='enumerated']"):
    superClass = option.get("superClass")
    value = option.get("value").replace(superClass + ".value.", "")
    m_flag = superClass.replace(
        "com.st.stm32cube.ide.mcu.gnu.managedbuild.option.", "")
    # If the eclipse notation of the flag differs we correct that
    if m_flag in option_mapping:
        m_flag = option_mapping[m_flag]
    # Add the flag to the list of flags
    if m_flag in cc_only_option_mapping:
        print("Removing %s=%s" % (mflag, value))
    else:
        m_flags += ['-m%s=%s' % (m_flag, value)]

build_flags += m_flags
print("%s: Adding the following build flags: '%s'"
      % (log_name, ', '.join(build_flags)))


#################################################
# Get the ld script from .cproject
#################################################
ld_script_entry = tool_chain.find(
    "tool[@name='MCU GCC Linker']/option").get("value")

ld_script = re.search(
    '\$\{workspace_loc:/\$\{ProjName\}/(.+)\}', ld_script_entry)
if ld_script != None:
    ld_script = ld_script.group(1)
else:
    # How do I send a warning to platformio?
    print("%s: Warning, ld script not found in directory in project configuration" % log_name)
    print("%s: Using the ld script provided by platformio" % log_name)

#################################################
# Now we create the needed entries
# in the environment
#################################################

# Build the src_filter
if not 'SRC_FILTER' in env:
    env['SRC_FILTER'] = []
# we explicitly add the Core files at the beginning
env['SRC_FILTER'] += ['+<Core/Src/>']
# Now we add the collected source directories to the src_filter
env['SRC_FILTER'] += src_dirs
# Create the list of all needed include directories that we have collected
if not 'BUILD_FLAGS' in env:
    env['BUILD_FLAGS'] = []
# Add the collected include directories to the build_flags
env['BUILD_FLAGS'] += include_dirs
# Add the necessary build flags to compiler and linker flags.
env['BUILD_FLAGS'] += cc_only_flags
env['BUILD_FLAGS'] += build_flags
env["LINKFLAGS"] += build_flags
env["LINKFLAGS"] += ld_only_flags

# Add the correct ld_script from the project dir
if ld_script != None:
    env["LDSCRIPT_PATH"] = ld_script

# Remove the framwork from the environment
del env['PIOFRAMEWORK']
