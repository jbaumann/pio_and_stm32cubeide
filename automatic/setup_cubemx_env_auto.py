# Author: Joachim Baumann
#
# This script is based on the information for advanced scripting provided 
# by platformio
# https://docs.platformio.org/en/latest/projectconf/advanced_scripting.html
#
# We try to get all needed information from the .cproject file, collect all
# source directories from that to create the src_filter and read platformio's
# own board definition to glean the cpu type.

from os import path, walk
import SCons.Errors
import xml.etree.ElementTree as ET
import re

Import("env")
project_dir = env["PROJECT_DIR"]
log_name = "SETUP_CUBEMX"

# Open the .cproject file and parse it as XML
try:
	root = ET.parse('.cproject').getroot()
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

config = root.find(".//configuration[@name='Debug']")

for source_entry in config.findall("sourceEntries/entry"):
	directory = source_entry.get('name')
	if directory != "Core":
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
            if file.endswith(('.c', '.cpp', '.s')):
                src_dirs.add('+<%s/>' % dirpath)

#################################################
# now read the include dirs from .cproject
#################################################
tool_chain = config.find("./folderInfo/toolChain")

for include_entry in tool_chain.findall(".//option[@superClass='com.st.stm32cube.ide.mcu.gnu.managedbuild.tool.c.compiler.option.includepaths']/listOptionValue"):
	inc_dir = include_entry.get('value')
	if inc_dir != "../Core/Inc":
		inc_dir = inc_dir.replace("../", "-I", 1)
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

# extract the cpu type from the board 
board_config = env.BoardConfig()
cpu = board_config._manifest["build"]["cpu"]
m_flags = ['-mcpu=%s' % cpu]

# extract other flags from the .cproject file
option_mapping = {
	"floatabi": "float-abi",
}
for option in tool_chain.findall("option[@valueType='enumerated']"):
	superClass = option.get("superClass")
	value = option.get("value").replace(superClass + ".value.", "")
	m_flag = superClass.replace(
		"com.st.stm32cube.ide.mcu.gnu.managedbuild.option.", "")
	if m_flag in option_mapping:
		m_flag = option_mapping[m_flag]
	m_flags += ['-m%s=%s' % (m_flag, value)]

build_flags += m_flags
print("%s: Using the following build flags: '%s'"
        % (log_name, ', '.join(build_flags)))

# additional flags for the compiler only
#cc_only_flags = [
    # These are already set by platformio, see 
	# PIO_FRAMEWORK_ARDUINO_STANDARD_LIB
    #"--specs=nano.specs",
    #"--specs=nosys.specs",
#]

# additional flags for the linker only
#ld_only_flags = [
#]

#################################################
# Get the ld script from .cproject
#################################################
ld_script_entry = tool_chain.find("tool[@name='MCU GCC Linker']/option").get("value")

ld_script = re.search('\$\{workspace_loc:/\$\{ProjName\}/(.+)\}', ld_script_entry)
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
#env['BUILD_FLAGS'] += cc_only_flags
env['BUILD_FLAGS'] += build_flags
env["LINKFLAGS"] += build_flags
#env["LINKFLAGS"] += ld_only_flags

# Add the correct ld_script from the project dir
if ld_script != None:
	env["LDSCRIPT_PATH"] = ld_script
