#include "mainwindow.h"

#include <QHBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QSlider>
#include <QSpinBox>
#include <QVBoxLayout>

MainWindow::MainWindow(QWidget *parent) : QWidget(parent) {
    setWindowTitle("成绩等级评定");
    resize(400, 200);

    auto *title = new QLabel("输入成绩（0~100），点击评定：");

    // 1. 创建控件
    m_scoreSpin = new QSpinBox;                 // 数字输入框
    m_scoreSpin->setRange(0, 100);              // 限定范围
    m_scoreSpin->setValue(85);

    m_scoreSlider = new QSlider(Qt::Horizontal); // 水平滑条
    m_scoreSlider->setRange(0, 100);
    m_scoreSlider->setValue(85);

    auto *inputRow = new QHBoxLayout;           // 水平布局：输入框 + 滑条并排
    inputRow->addWidget(m_scoreSpin);
    inputRow->addWidget(m_scoreSlider);

    auto *button = new QPushButton("评定");

    m_result = new QLabel("等待评定……");
    m_result->setAlignment(Qt::AlignCenter);
    m_result->setStyleSheet("font-size: 18px; padding: 8px;");

    // 2. 信号与槽（Qt 的核心机制）
    //    输入框变 -> 滑条跟着变；滑条变 -> 输入框跟着变（双向同步）
    connect(m_scoreSpin, qOverload<int>(&QSpinBox::valueChanged),
            m_scoreSlider, &QSlider::setValue);
    connect(m_scoreSlider, &QSlider::valueChanged,
            m_scoreSpin, &QSpinBox::setValue);

    //    点击按钮 -> 调用自己的 evaluate() 槽函数
    connect(button, &QPushButton::clicked, this, &MainWindow::evaluate);

    // 3. 垂直布局把各行排好
    auto *layout = new QVBoxLayout(this);
    layout->addWidget(title);
    layout->addLayout(inputRow);
    layout->addWidget(button);
    layout->addWidget(m_result);
}

void MainWindow::evaluate() {
    int score = m_scoreSpin->value();
    QString text, color;

    // 4. 业务逻辑：分数 -> 等级 + 配色
    if (score >= 90)      { text = "优秀 (A)"; color = "#2e7d32"; }
    else if (score >= 80) { text = "良好 (B)"; color = "#1565c0"; }
    else if (score >= 70) { text = "中等 (C)"; color = "#ef6c00"; }
    else if (score >= 60) { text = "及格 (D)"; color = "#c62828"; }
    else                  { text = "不及格 (F)"; color = "#b71c1c"; }

    m_result->setText(QString("得分 %1 分 —— 等级：%2").arg(score).arg(text));
    m_result->setStyleSheet(
        QString("font-size: 18px; padding: 8px; color: white; background: %1;")
            .arg(color));
}
