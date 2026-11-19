cmake_minimum_required(VERSION 3.20)
project(grade_demo LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)          # 扫描 Q_OBJECT 并自动运行 moc

find_package(Qt6 REQUIRED COMPONENTS Widgets)

# 头文件也列进来，让 AUTOMOC 找到 Q_OBJECT
add_executable(grade_demo main.cpp mainwindow.cpp mainwindow.h)
target_link_libraries(grade_demo PRIVATE Qt6::Widgets)
