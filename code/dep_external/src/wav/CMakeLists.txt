cmake_minimum_required(VERSION 3.30.0)

project (wavwriter)

SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --std=c++11")
SET(CMAKE_POSITION_INDEPENDENT_CODE ON)

option(BUILD_SHARED_LIBS "Build shared library" ON)

set(EXTERNAL_LIB_DIR  "${CMAKE_CURRENT_SOURCE_DIR}/lib")
set(EXTERNAL_INCLUDE_DIR  "${CMAKE_CURRENT_SOURCE_DIR}/include")

if(BUILD_SHARED_LIBS)
  add_library(${PROJECT_NAME} SHARED dep_wavwriter.c)
else()
  add_library(${PROJECT_NAME} STATIC dep_wavwriter.c)
endif()

# Create an alias target for namespaced usage
add_library(wavwriter::wavwriter ALIAS ${PROJECT_NAME})

set(WAVWRITER_PUBLIC_HEADER ${CMAKE_CURRENT_SOURCE_DIR}/dep_wavwriter.h)
set_target_properties(${PROJECT_NAME} PROPERTIES PUBLIC_HEADER "${WAVWRITER_PUBLIC_HEADER}")

# Install targets with export
include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME}
  EXPORT wavwriter-targets
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# Export targets for find_package()
install(EXPORT wavwriter-targets
  FILE wavwriter-targets.cmake
  NAMESPACE wavwriter::
  DESTINATION ${CMAKE_INSTALL_PREFIX}/cmake
)

# Configure package config file
include(CMakePackageConfigHelpers)
configure_package_config_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/config.cmake.in
  ${CMAKE_CURRENT_BINARY_DIR}/wavwriter-config.cmake
  INSTALL_DESTINATION ${CMAKE_INSTALL_PREFIX}/cmake
)

write_basic_package_version_file(
  ${CMAKE_CURRENT_BINARY_DIR}/wavwriter-config-version.cmake
  VERSION 1.0.0
  COMPATIBILITY AnyNewerVersion
)

install(FILES
  ${CMAKE_CURRENT_BINARY_DIR}/wavwriter-config.cmake
  ${CMAKE_CURRENT_BINARY_DIR}/wavwriter-config-version.cmake
  DESTINATION ${CMAKE_INSTALL_PREFIX}/cmake
)
