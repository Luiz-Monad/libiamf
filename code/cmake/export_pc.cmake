
function(get_target_location out_var target)
  set(loc)
  
  # Try different location properties for imported targets
  get_target_property(loc ${target} IMPORTED_LOCATION_RELEASE)
  if(NOT loc)
    get_target_property(loc ${target} IMPORTED_LOCATION)
  endif()
  if(NOT loc)
    get_target_property(loc ${target} IMPORTED_LOCATION_DEBUG)
  endif()
  if(NOT loc)
    get_target_property(loc ${target} IMPORTED_LOCATION_RELWITHDEBINFO)
  endif()
  if(NOT loc)
    get_target_property(loc ${target} IMPORTED_LOCATION_MINSIZEREL)
  endif()
  
  set(${out_var} "${loc}" PARENT_SCOPE)
endfunction()

function(collect_target_libs out_var target)  
  if(NOT TARGET ${target})
    return()
  endif()

  # Get all types of link libraries
  get_target_property(interface_libs ${target} INTERFACE_LINK_LIBRARIES)
  get_target_property(link_libs ${target} LINK_LIBRARIES)
  get_target_property(imported_link_interface ${target} IMPORTED_LINK_INTERFACE_LIBRARIES)
  
  set(libs)
  if(interface_libs)
    list(APPEND libs ${interface_libs})
  endif()
  if(link_libs)
    list(APPEND libs ${link_libs})
  endif()
  if(imported_link_interface)
    list(APPEND libs ${imported_link_interface})
  endif()  
  if(NOT libs)
    set(${out_var} "" PARENT_SCOPE)
    return()
  endif()

  set(result)

  # First, add the target's own library file if it's a library target
  get_target_property(target_type ${target} TYPE)
  get_target_location(loc ${target})
  if(loc)
    list(APPEND result ${loc})
  endif()
  
  # Then collect dependencies
  foreach(lib IN LISTS libs)
    # Strip $<LINK_ONLY:...>
    if(lib MATCHES "^\\$<LINK_ONLY:(.*)>$")
      set(lib_stripped "${CMAKE_MATCH_1}")
    else()
      set(lib_stripped "${lib}")
    endif()
    if(TARGET ${lib_stripped})
      # Recursively collect from dependency targets
      collect_target_libs(sub_libs ${lib_stripped})
      if(sub_libs)
        list(APPEND result ${sub_libs})
      endif()      
      # Try different location properties for imported targets
      get_target_location(loc ${lib_stripped})
      if(loc)
        list(APPEND result ${loc})
      endif()
    elseif(lib_stripped MATCHES "^-l" OR lib_stripped MATCHES "^-L" OR lib_stripped STREQUAL "pthread")
      list(APPEND result ${lib_stripped})
    endif()
  endforeach()

  if(result)
  list(REMOVE_DUPLICATES result)
  endif()
  set(${out_var} "${result}" PARENT_SCOPE)
endfunction()

function(target_export_pc TARGET_NAME VERSION TEMPLATE_FILE)
  set(options)
  set(oneValueArgs DESTINATION)
  cmake_parse_arguments(ARG "${options}" "${oneValueArgs}" "" ${ARGN})

  if(NOT ARG_DESTINATION)
    message(FATAL_ERROR "target_export_pc requires DESTINATION")
  endif()

  # Collect recursive libs
  collect_target_libs(all_libs ${TARGET_NAME})

  set(LIBS_PRIVATE "")
  foreach(lib IN LISTS all_libs)
    if(lib MATCHES "\\.a$")
      get_filename_component(libname ${lib} NAME_WE)
      string(REGEX REPLACE "^lib" "" libname ${libname})
      list(APPEND LIBS_PRIVATE "-l${libname}")
    else()
      list(APPEND LIBS_PRIVATE "${lib}")
    endif()
  endforeach()

  string(JOIN " " LIBS_PRIVATE ${LIBS_PRIVATE})

  configure_file(
    ${TEMPLATE_FILE}
    ${CMAKE_CURRENT_BINARY_DIR}/${TARGET_NAME}.pc
    @ONLY
  )

  install(FILES ${CMAKE_CURRENT_BINARY_DIR}/${TARGET_NAME}.pc
    DESTINATION ${ARG_DESTINATION}
  )
endfunction()
