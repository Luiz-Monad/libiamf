cmake_minimum_required(VERSION 3.30.0)
project(iamf)

message(STATUS "Start build iamf")

# Compiler options
if(MSVC)
    add_compile_options(/we4101 /we4189)
else()
    add_compile_options(-O3 -Werror=unused-variable)
endif()
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

option(BUILD_SHARED_LIBS "Build shared library" ON)
option(SUPPORT_VERIFIER "Output vlogging file" OFF)
option(CODEC_CAP "Codec capability check" ON)
option(MULTICHANNEL_BINAURALIZER "Enable multichannel binaural rendering" OFF)
option(HOA_BINAURALIZER "Enable HOA binaural rendering" OFF)

# External codec dirs
set(CODEC_LIB_DIR     "${PROJECT_SOURCE_DIR}/dep_codecs/lib")
set(CODEC_INCLUDE_DIR "${PROJECT_SOURCE_DIR}/dep_codecs/include")

if(SUPPORT_VERIFIER)
  message(STATUS "Output vlogging file")
  add_definitions(-DSUPPORT_VERIFIER=1)
endif()

# Debug define
if(CMAKE_BUILD_TYPE)
  string(TOLOWER ${CMAKE_BUILD_TYPE} BUILD_TYPE)
  if(BUILD_TYPE STREQUAL "debug")
    add_definitions(-DIA_DBG)
    message(STATUS "Debug mode enabled")
  endif()
endif()

# Optional binauralizers
if(MULTICHANNEL_BINAURALIZER)
  message(STATUS "Enable multichannel binaural rendering")
  add_definitions(-DENABLE_MULTICHANNEL_TO_BINAURAL=1)
endif()
if(HOA_BINAURALIZER)
  message(STATUS "Enable HOA binaural rendering")
  add_definitions(-DENABLE_HOA_TO_BINAURAL=1)
endif()

# Codec detection
if(CODEC_CAP)
  find_library(find_opus NAMES opus PATHS ${CODEC_LIB_DIR} NO_DEFAULT_PATH)
  if(NOT find_opus)
    message(WARNING "Opus library not found")
  else()
    add_definitions(-DCONFIG_OPUS_CODEC)
  endif()

  find_library(find_aac NAMES fdk-aac PATHS ${CODEC_LIB_DIR} NO_DEFAULT_PATH)
  if(NOT find_aac)
    message(WARNING "fdk-aac library not found")
  else()
    add_definitions(-DCONFIG_AAC_CODEC)
  endif()

  find_library(find_flac NAMES FLAC PATHS ${CODEC_LIB_DIR} NO_DEFAULT_PATH)
  if(NOT find_flac)
    message(WARNING "FLAC library not found")
  else()
    add_definitions(-DCONFIG_FLAC_CODEC)
    if(WIN32)
      add_definitions(-DFLAC__NO_DLL)
    endif()
  endif()
endif()

# Sources
include_directories(include)
aux_source_directory(dep_external/src/wav DIR_DEP_EXTERNAL_WAV)
aux_source_directory(src/common DIR_IAMF_COMMON)
aux_source_directory(src/iamf_dec DIR_IAMF_DEC)
aux_source_directory(src/iamf_dec/arch DIR_IAMF_DEC_ARCH)
aux_source_directory(src/iamf_dec/arch/arm DIR_IAMF_DEC_ARCH_ARM)
aux_source_directory(src/iamf_dec/arch/x86 DIR_IAMF_DEC_ARCH_X86)
if(find_opus)
  aux_source_directory(src/iamf_dec/opus DIR_IAMF_DEC_OPUS)
endif()
if(find_aac)
  aux_source_directory(src/iamf_dec/aac DIR_IAMF_DEC_AAC)
endif()
if(find_flac)
  aux_source_directory(src/iamf_dec/flac DIR_IAMF_DEC_FLAC)
endif()
aux_source_directory(src/iamf_dec/pcm DIR_IAMF_DEC_PCM)

include_directories(
  ${CODEC_INCLUDE_DIR}
  ${PROJECT_SOURCE_DIR}/src/common
  ${PROJECT_SOURCE_DIR}/src/iamf_dec
  ${PROJECT_SOURCE_DIR}/src/iamf_dec/arch
  ${PROJECT_SOURCE_DIR}/src/iamf_dec/arch/arm
  ${PROJECT_SOURCE_DIR}/src/iamf_dec/arch/x86
)

# Build library
add_library(${PROJECT_NAME}
  ${DIR_DEP_EXTERNAL_WAV} ${DIR_IAMF_COMMON}
  ${DIR_IAMF_DEC_OPUS} ${DIR_IAMF_DEC_AAC} ${DIR_IAMF_DEC_FLAC} ${DIR_IAMF_DEC_PCM}
  ${DIR_IAMF_DEC} ${DIR_IAMF_DEC_ARCH} ${DIR_IAMF_DEC_ARCH_ARM} ${DIR_IAMF_DEC_ARCH_X86}
)

# Namespaced alias
add_library(${PROJECT_NAME}::${PROJECT_NAME} ALIAS ${PROJECT_NAME})

# Link codecs
if(find_opus)
  target_link_libraries(${PROJECT_NAME} PRIVATE ${find_opus})
endif()
if(find_aac)
  target_link_libraries(${PROJECT_NAME} PRIVATE ${find_aac})
endif()
if(find_flac)
  target_link_libraries(${PROJECT_NAME} PRIVATE ${find_flac})
endif()

# Always link math lib on Unix
if(UNIX)
  target_link_libraries(${PROJECT_NAME} PRIVATE m)
endif()

# Optional deps
if(MULTICHANNEL_BINAURALIZER)
  find_package(iamf2resonance REQUIRED)
  target_link_libraries(${PROJECT_NAME} PUBLIC iamf2resonance::iamf2resonance)
endif()
if(HOA_BINAURALIZER)
  find_package(iamf2bear REQUIRED)
  target_link_libraries(${PROJECT_NAME} PUBLIC iamf2bear::iamf2bear)
endif()
find_package(wavwriter REQUIRED)
target_link_libraries(${PROJECT_NAME} PRIVATE $<$<CONFIG:Debug>:wavwriter::wavwriter>)

# Public headers
set(IAMF_PUBLIC_HEADER
  ${CMAKE_CURRENT_SOURCE_DIR}/include/IAMF_decoder.h
  ${CMAKE_CURRENT_SOURCE_DIR}/include/IAMF_defines.h
  ${CMAKE_CURRENT_SOURCE_DIR}/include/vlogging_tool_sr.h
)
set_target_properties(${PROJECT_NAME} PROPERTIES PUBLIC_HEADER "${IAMF_PUBLIC_HEADER}")

target_include_directories(${PROJECT_NAME}
  PUBLIC $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/include>
         $<BUILD_INTERFACE:${PROJECT_BINARY_DIR}/include>
         $<INSTALL_INTERFACE:include>
  PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Install/export
include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME}
  EXPORT iamf-targets
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# Export targets for find_package()
install(EXPORT iamf-targets
  FILE iamf-targets.cmake
  NAMESPACE iamf::
  DESTINATION ${CMAKE_INSTALL_PREFIX}/cmake
)

# Config + version files
include(CMakePackageConfigHelpers)
configure_package_config_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/config.cmake.in
  ${CMAKE_CURRENT_BINARY_DIR}/iamf-config.cmake
  INSTALL_DESTINATION ${CMAKE_INSTALL_PREFIX}/cmake
)

write_basic_package_version_file(
  ${CMAKE_CURRENT_BINARY_DIR}/iamf-config-version.cmake
  VERSION 1.0.0
  COMPATIBILITY AnyNewerVersion
)

install(FILES
  ${CMAKE_CURRENT_BINARY_DIR}/iamf-config.cmake
  ${CMAKE_CURRENT_BINARY_DIR}/iamf-config-version.cmake
  DESTINATION ${CMAKE_INSTALL_PREFIX}/cmake
)
