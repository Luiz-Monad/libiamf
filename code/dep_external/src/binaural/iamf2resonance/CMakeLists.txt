cmake_minimum_required(VERSION 3.30.0)

project (iamf2resonance)

SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --std=c++11")
SET(CMAKE_POSITION_INDEPENDENT_CODE ON)

option(BUILD_SHARED_LIBS "Build shared library" ON)

set(EXTERNAL_LIB_DIR  "${CMAKE_CURRENT_SOURCE_DIR}/lib")
set(EXTERNAL_INCLUDE_DIR  "${CMAKE_CURRENT_SOURCE_DIR}/include")

find_package(ResonanceAudio REQUIRED)

if(BUILD_SHARED_LIBS)
  add_library(${PROJECT_NAME} SHARED iamf2resonance.cc)
  target_link_libraries (${PROJECT_NAME} ResonanceAudio::ResonanceAudioShared)
else()
  add_library(${PROJECT_NAME} STATIC iamf2resonance.cc)
  target_link_libraries (${PROJECT_NAME} ResonanceAudio::ResonanceAudioStatic)
endif()

# Create an alias target for namespaced usage
add_library(iamf2resonance::iamf2resonance ALIAS ${PROJECT_NAME})

set(IAMF2RESONANCE_PUBLIC_HEADER ${CMAKE_CURRENT_SOURCE_DIR}/iamf_resonance_api.h)
set_target_properties(${PROJECT_NAME} PROPERTIES PUBLIC_HEADER "${IAMF2RESONANCE_PUBLIC_HEADER}")

# Install targets with export
include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME}
  EXPORT iamf2resonance-targets
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# Export targets for find_package()
install(EXPORT iamf2resonance-targets
  FILE iamf2resonance-targets.cmake
  NAMESPACE iamf2resonance::
  DESTINATION ${CMAKE_INSTALL_PREFIX}/cmake
)

# Configure package config file
include(CMakePackageConfigHelpers)
configure_package_config_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/config.cmake.in
  ${CMAKE_CURRENT_BINARY_DIR}/iamf2resonance-config.cmake
  INSTALL_DESTINATION ${CMAKE_INSTALL_PREFIX}/cmake
)

write_basic_package_version_file(
  ${CMAKE_CURRENT_BINARY_DIR}/iamf2resonance-config-version.cmake
  VERSION 1.0.0
  COMPATIBILITY AnyNewerVersion
)

install(FILES
  ${CMAKE_CURRENT_BINARY_DIR}/iamf2resonance-config.cmake
  ${CMAKE_CURRENT_BINARY_DIR}/iamf2resonance-config-version.cmake
  DESTINATION ${CMAKE_INSTALL_PREFIX}/cmake
)
