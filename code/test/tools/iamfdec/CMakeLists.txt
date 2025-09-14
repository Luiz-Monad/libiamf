cmake_minimum_required(VERSION 3.31.0)
project(iamfdec)

message(STATUS "+++++++++++ iamfdec +++++++++++++")

# Build options for the test app
option(MULTICHANNEL_BINAURALIZER "Enable multichannel binaural rendering" OFF)
option(HOA_BINAURALIZER "Enable HOA binaural rendering" OFF)
option(SUPPORT_VERIFIER "Output vlogging file" OFF)

# Compiler warnings
if(MSVC)
    add_compile_options(/we4101 /we4189)
else()
    add_compile_options(-O3 -Werror=unused-variable)
endif()

# Optional defines
if(MULTICHANNEL_BINAURALIZER)
  message(STATUS "Enable multichannel binaural rendering in test app")
  add_definitions(-DENABLE_MULTICHANNEL_TO_BINAURAL=1)
endif()

if(HOA_BINAURALIZER)
  message(STATUS "Enable HOA binaural rendering in test app")
  add_definitions(-DENABLE_HOA_TO_BINAURAL=1)
endif()

if(SUPPORT_VERIFIER)
  message(STATUS "Output vlogging file")
  add_definitions(-DSUPPORT_VERIFIER=1)
endif()

# Sources
include_directories(include)
aux_source_directory(src DIR_IAMFDEC_SRC)

# Executable
add_executable(iamfdec ${DIR_IAMFDEC_SRC})

# Use the iamf package
find_package(iamf REQUIRED)
target_link_libraries(${PROJECT_NAME} PUBLIC iamf::iamf)

# Extra system libs if needed
if(NOT MSVC)
    target_link_libraries(${PROJECT_NAME} PRIVATE z)
endif()

# --- Install binary ---
include(GNUInstallDirs)
install(TARGETS iamfdec
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
