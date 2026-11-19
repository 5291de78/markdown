#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QWidget>

class QSpinBox;
class QSlider;
class QLabel;

// 继承 QWidget 作为程序主窗口
class MainWindow : public QWidget {
    Q_OBJECT                    // Qt 元对象系统的标记，AUTOMOC 靠它生成信号槽代码

public:
    explicit MainWindow(QWidget *parent = nullptr);

private slots:
    void evaluate();            // 点击"评定"按钮时执行

private:
    QSpinBox *m_scoreSpin;      // 数字输入框
    QSlider  *m_scoreSlider;    // 滑条
    QLabel   *m_result;         // 结果显示标签
};

#endif // MAINWINDOW_H
