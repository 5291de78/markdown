# Additional clean files
cmake_minimum_required(VERSION 3.16)

if("${CONFIG}" STREQUAL "" OR "${CONFIG}" STREQUAL "")
  file(REMOVE_RECURSE
  [[CMakeFiles\grade_demo_autogen.dir\AutogenUsed.txt]]
  [[CMakeFiles\grade_demo_autogen.dir\ParseCache.txt]]
  "grade_demo_autogen"
  )
endif()
