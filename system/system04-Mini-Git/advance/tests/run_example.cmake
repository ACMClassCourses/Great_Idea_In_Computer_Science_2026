foreach(REQUIRED_VARIABLE PROGRAM INPUT EXPECTED ACTUAL)
    if(NOT DEFINED ${REQUIRED_VARIABLE})
        message(FATAL_ERROR "${REQUIRED_VARIABLE} was not provided")
    endif()
endforeach()

execute_process(
    COMMAND "${PROGRAM}"
    INPUT_FILE "${INPUT}"
    OUTPUT_FILE "${ACTUAL}"
    ERROR_VARIABLE ERROR_OUTPUT
    RESULT_VARIABLE RESULT
)

if(NOT RESULT EQUAL 0)
    message(FATAL_ERROR "Mini Git exited with ${RESULT}: ${ERROR_OUTPUT}")
endif()

execute_process(
    COMMAND diff -u "${EXPECTED}" "${ACTUAL}"
    OUTPUT_VARIABLE DIFFERENCE
    ERROR_VARIABLE DIFF_ERROR
    RESULT_VARIABLE DIFF_RESULT
)

if(NOT DIFF_RESULT EQUAL 0)
    message(FATAL_ERROR
        "Output differs from ${EXPECTED}:\n${DIFFERENCE}${DIFF_ERROR}")
endif()

file(REMOVE "${ACTUAL}")
