#include <QApplication>
#include "mainwindow.h"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);   // Qt 图形程序必须有且只有一个 QApplication
    MainWindow w;
    w.show();                       // show 之前窗口不可见
    return app.exec();              // 进入事件循环，直到窗口关闭
}
