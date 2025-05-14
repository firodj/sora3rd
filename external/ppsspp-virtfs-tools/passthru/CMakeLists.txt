cmake_minimum_required(VERSION 3.13)
project(virtfs-passthru)
set(CMAKE_CXX_STANDARD 14)
set(SOURCE_FILES passthru.cpp)

add_library(virtfs-passthru SHARED ${SOURCE_FILES})

if (MSVC)
    target_compile_options(virtfs-passthru PRIVATE /D_USRDLL /D_WINDLL /Gd /errorReport:prompt /Zc:wchar_t /Zc:forScope /GR- /arch:SSE2 /EHsc /GS /Gy /Oy- /nologo /W3 /WX- /MP /analyze /D _CRT_SECURE_NO_WARNINGS)
    target_compile_options(virtfs-passthru PRIVATE
        $<$<CONFIG:Debug>:/Od;/D_DEBUG;/RTC1;/Z7;/W3;/MDd;/LDd>
        $<$<CONFIG:Release>:/O2;/DNDEBUG;/W3;/MD;/LD>
    )
else()
    target_compile_options(virtfs-passthru PRIVATE -fpic -shared)
endif()
