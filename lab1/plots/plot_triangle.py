from PySide6.QtGui import QPen, QColor, QPainter, QPolygon, QBrush
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
import numpy as np
from sympy import Float

from scipy.stats import gaussian_kde, mode
import itertools

class PlotTriangle:
    def __init__(self, x_values, y_values, function_input, widget_width, widget_height):
        self.function_input = function_input
        self.x_values = x_values
        self.unclear_value = y_values
        self.min_x = np.min(x_values)
        self.max_x = np.max(x_values)

        self.window_start = 50
        self.window_end = 15
        self.widget_width = widget_width - self.window_start - self.window_end
        self.widget_height = widget_height - self.window_start

        self.y_values = []
        self.x_grid = [[0] * len(y_values[0]) for _ in range(len(y_values))]
        for sublist in self.unclear_value:
            cleaned_sublist = [
                float(value) if isinstance(value, (int, float, Float)) else 0
                for value in sublist
            ]
            self.y_values.append(cleaned_sublist)

        all_y_values = np.concatenate(self.y_values)

        lower_bound = np.percentile(all_y_values, 5)
        upper_bound = np.percentile(all_y_values, 95)
        self.min_y = lower_bound
        self.max_y = upper_bound
        self.max_y_without_padd = np.max(y_values)
        self.min_y_without_padd = np.min(y_values)
        # Добавляем отступ для визуального комфорта
        y_range = self.max_y - self.min_y
        padding = y_range * 0.3
        self.min_y -= padding
        self.max_y += padding


        if self.min_y > 0:
            self.min_y = 0 - padding
        if self.max_y < 0:
            self.max_y = 0 + padding

    def calculate_x_mapped(self):
        gap_size = 20  # Размер промежутка между группами параллелепипедов

        total_bar_width = (self.widget_width - gap_size * (len(self.x_values) - 1)) // len(self.x_values)
        piramide_bar = total_bar_width // len(self.y_values)

        for j in range(len(self.x_values)):
            x_start = j * (total_bar_width + gap_size)  # Добавляем зазор между группами
            for i, y_data in enumerate(self.y_values):
                adjusted_x = self.calculate_parallelipiped_x(x_start, i, piramide_bar)
                self.x_grid[i][j] = adjusted_x


    def x_widget(self, x, widget_width):
        return int((x - self.min_x) / (self.max_x - self.min_x) * widget_width)

    def y_widget(self, y, widget_height):
        return int(widget_height - (y - self.min_y) / (self.max_y - self.min_y) * widget_height)

    def draw_legend(self, painter):
        bar_styles = [
            QColor(210, 0, 107),
            QColor(255, 108, 0),
            QColor(0, 158, 142),
            QColor(149, 236, 0)
        ]
        text_offset = 20
        legend_start_x = 0
        legend_start_y = self.widget_height + self.window_start / 2 - text_offset / 2
        box_size = 15

        gap = 5

        # Вычисляем ширину каждой легенды
        item_widths = [
            box_size + text_offset + painter.fontMetrics().horizontalAdvance(item.text()) + gap
            for item in self.function_input
        ]
        total_width = sum(item_widths) - gap  # убираем лишний пробел после последнего элемента

        # Рисуем белый фон под легенду
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawRect(legend_start_x - 5, self.widget_height , total_width + 10, self.window_start)

        # Рисуем элементы легенды в ряд
        current_x = legend_start_x
        for i, item in enumerate(self.function_input):
            color = bar_styles[i % len(bar_styles)]
            painter.setBrush(QBrush(color))
            painter.drawRect(current_x, legend_start_y, box_size, box_size)
            painter.drawText(current_x + text_offset, legend_start_y + box_size // 2 + 5, item.text())
            current_x += item_widths[i]



    def draw_grid(self, painter, style):
        pen = QPen(style.grid_color)
        pen.setWidth(style.grid_width)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)

        # Рисуем вертикальные линии сетки
        self.calculate_x_mapped()
        transorm_grid = np.array(self.x_grid).T

        for j in range(len(self.x_values)):
            x_mapped = np.mean(transorm_grid[j][:])
            painter.drawLine(x_mapped, 0, x_mapped, self.widget_height)

            label = f"{self.x_values[j]:.2f}"  # Format the label as needed
            painter.drawText(x_mapped + 5, self.widget_height - 5, label)

        # Рисуем горизонтальные линии сетки
        y_zero_mapped = self.y_widget(0, self.widget_height)
        max_value = float(np.max([abs(self.min_y_without_padd), self.max_y_without_padd]))


        # Горизонтальные линии
        step = max_value / 4
        y = 0
        while y < float(np.max([abs(self.min_y), self.max_y])):

            y += step

            # y_mapped = int(y_zero_mapped - y / self.max_y * y_zero_mapped)
            y_mapped = self.y_widget(y, self.widget_height)
            if y == 0:
                painter.drawLine(0, y_mapped, self.window_start + self.widget_width + self.window_end, y_mapped)

                label = f" {y:.3f}"  # Format the label as needed
                painter.drawText(5, y_mapped, label)
                continue
            if y_mapped > 0 :
                painter.drawLine(0, y_mapped, self.window_start + self.widget_width + self.window_end, y_mapped)

                label = f"{y:.3f}"  # Format the label as needed
                painter.drawText(5, y_mapped, label)

            horizont_mapped = y_zero_mapped + (y_zero_mapped - y_mapped)
            if horizont_mapped < self.widget_height:

                painter.drawLine(0, horizont_mapped, self.window_start + self.widget_width + self.window_end, horizont_mapped)

                label = f"-{y:.3f}"  # Format the label as needed
                painter.drawText(5, horizont_mapped, label)


        # Рисуем ось X
        pen.setStyle(Qt.SolidLine)
        pen.setColor(style.grid_black)
        painter.setPen(pen)
        painter.drawLine(0, y_zero_mapped, self.window_end + self.window_start + self.widget_width, y_zero_mapped)


    # def calculate_parallelipiped_x(self, x_start, i, parallelipiped_bar):
    #     x_parallelipiped = self.window_start + x_start + i * parallelipiped_bar + parallelipiped_bar / 2
    #     return x_parallelipiped

    def calculate_parallelipiped_x(self, x_start, i, parallelipiped_bar):
        # Убираем смещение, которое вызывало сдвиг от оси X
        x_parallelipiped = self.window_start + x_start + i * parallelipiped_bar + parallelipiped_bar / 2
        return x_parallelipiped

    def draw_parallelepiped(self, painter, adjusted_x, y_zero_mapped, y_data_value, piramide_bar):
        y = self.y_widget(y_data_value, self.widget_height)

        # Определяем размеры параллелепипеда
        # Убираем смещение, которое вызывало сдвиг от оси X
        # y_zero_mapped -= self.shift

        width = piramide_bar
        depth = piramide_bar // 8  # Глубина для создания lab2 эффекта
        height = abs(self.y_zero_mapped - y)


        # Определяем координаты для передней грани
        if y_data_value == 0:
            front_top_left = QPoint(adjusted_x - width // 2, y_zero_mapped - height)
            front_top_right = QPoint(adjusted_x + width // 2, y_zero_mapped - height)
            front_bottom_left = QPoint(adjusted_x - width // 2, y_zero_mapped)
            front_bottom_right = QPoint(adjusted_x + width // 2, y_zero_mapped)

            # Определяем координаты для задней грани
            back_top_left = QPoint(adjusted_x - width // 2 + depth, y_zero_mapped - height - depth)
            back_top_right = QPoint(adjusted_x + width // 2 + depth, y_zero_mapped - height - depth)
            back_bottom_left = QPoint(adjusted_x - width // 2 + depth, y_zero_mapped - depth)
            back_bottom_right = QPoint(adjusted_x + width // 2 + depth, y_zero_mapped - depth)

        elif y_data_value > 0:
            # Если значение положительное, рисуем выше оси OX
            front_top_left = QPoint(adjusted_x, y_zero_mapped - height)
            front_top_right = QPoint(adjusted_x, y_zero_mapped - height)
            front_bottom_left = QPoint(adjusted_x - width // 2, y_zero_mapped)
            front_bottom_right = QPoint(adjusted_x + width // 2, y_zero_mapped)

            # Определяем координаты для задней грани
            back_top_left = QPoint(adjusted_x, y_zero_mapped - height)
            back_top_right = QPoint(adjusted_x, y_zero_mapped - height)
            back_bottom_left = QPoint(adjusted_x - width // 2 + depth, y_zero_mapped - depth)
            back_bottom_right = QPoint(adjusted_x + width // 2 + depth, y_zero_mapped - depth)
        else:
            # Если значение отрицательное, рисуем ниже оси OX
            front_top_left = QPoint(adjusted_x - width // 2, y_zero_mapped)
            front_top_right = QPoint(adjusted_x + width // 2, y_zero_mapped)
            front_bottom_left = QPoint(adjusted_x, y_zero_mapped + height)
            front_bottom_right = QPoint(adjusted_x, y_zero_mapped + height)

            # Определяем координаты для задней грани
            back_top_left = QPoint(adjusted_x - width // 2 + depth, y_zero_mapped - depth)
            back_top_right = QPoint(adjusted_x + width // 2 + depth, y_zero_mapped - depth)
            back_bottom_left = QPoint(adjusted_x, y_zero_mapped + height)
            back_bottom_right = QPoint(adjusted_x, y_zero_mapped + height)

        # Рисуем переднюю грань
        painter.drawPolygon(QPolygon([
            front_top_left,
            front_top_right,
            front_bottom_right,
            front_bottom_left
        ]))

        # Рисуем верхнюю грань
        painter.drawPolygon(QPolygon([
            front_top_left,
            front_top_right,
            back_top_right,
            back_top_left
        ]))

        # Рисуем боковую грань (правую)
        painter.drawPolygon(QPolygon([
            front_top_right,
            front_bottom_right,
            back_bottom_right,
            back_top_right
        ]))

    def draw_plot(self, painter):
        bar_styles = [
            QColor(210, 0, 107),
            QColor(255, 108, 0),
            QColor(0, 158, 142),
            QColor(149, 236, 0)
        ]

        # Используем точно ту же логику, что и в calculate_x_mapped
        gap_size = 20  # Размер промежутка между группами параллелепипедов
        total_bar_width = (self.widget_width - gap_size * (len(self.x_values) - 1)) // len(self.x_values)
        parallelepiped_bar = total_bar_width // len(self.y_values)

        self.y_zero_mapped = self.y_widget(0, self.widget_height)

        for j in range(len(self.x_values)):
            x_start = j * (total_bar_width + gap_size)  # Добавляем зазор между группами
            
            # Рисуем все функции для данного x рядом друг с другом
            for i, y_data in enumerate(self.y_values):
                bar_color = bar_styles[i % len(bar_styles)]
                painter.setBrush(bar_color)

                # Используем точно ту же формулу, что и в calculate_parallelipiped_x
                adjusted_x = self.calculate_parallelipiped_x(x_start, i, parallelepiped_bar)
                self.draw_parallelepiped(painter, adjusted_x, self.y_zero_mapped, y_data[j], parallelepiped_bar)

        self.draw_legend(painter)
