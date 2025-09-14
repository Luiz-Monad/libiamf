# FindFDKAAC.cmake - Find FDK-AAC library
# This module defines:
#  FDKAAC_FOUND - True if FDK-AAC is found
#  FDKAAC_INCLUDE_DIRS - Include directories for FDK-AAC
#  FDKAAC_LIBRARIES - Libraries to link for FDK-AAC
#  FDKAAC_VERSION - Version of FDK-AAC found

find_path(FDKAAC_INCLUDE_DIR
    NAMES fdk-aac/aacenc_lib.h
    PATHS ${FDKAAC_ROOT}
    PATH_SUFFIXES include
)

find_library(FDKAAC_LIBRARY
    NAMES fdk-aac
    PATHS ${FDKAAC_ROOT}
    PATH_SUFFIXES lib
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(FDKAAC
    REQUIRED_VARS FDKAAC_LIBRARY FDKAAC_INCLUDE_DIR
    VERSION_VAR FDKAAC_VERSION
)

if(FDKAAC_FOUND)
    set(FDKAAC_LIBRARIES ${FDKAAC_LIBRARY})
    set(FDKAAC_INCLUDE_DIRS ${FDKAAC_INCLUDE_DIR})
    
    if(NOT TARGET FDKAAC::fdk-aac)
        add_library(FDKAAC::fdk-aac UNKNOWN IMPORTED)
        set_target_properties(FDKAAC::fdk-aac PROPERTIES
            IMPORTED_LOCATION "${FDKAAC_LIBRARY}"
            INTERFACE_INCLUDE_DIRECTORIES "${FDKAAC_INCLUDE_DIR}"
        )
    endif()
endif()

mark_as_advanced(FDKAAC_INCLUDE_DIR FDKAAC_LIBRARY)
