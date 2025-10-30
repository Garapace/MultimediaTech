from PySide6.QtGui import QPen, QColor, QPainter, QPolygon, QBrush
from PySide6.QtCore import Qt, QPoint
import numpy as np
from sympy import Float

class PlotRectangle:
    def __init__(self, x_values, y_values, function_input, widget_width, widget_height):
        # Валидация данных
        if x_values is None or y_values is None or len(x_values) == 0:
            self.valid = False
            return
        self.valid = True

        self.function_input = function_input
        self.x_values = x_values
        self.y_values = y_values

        # Отступы как в triangle
        self.window_start = 50
        self.window_end = 15
        self.widget_width = widget_width - self.window_start - self.window_end
        self.widget_height = widget_height - self.window_start

        # Очистка данных
        self.cleaned_values = []
        for sublist in y_values:
            cleaned_sublist = [
                float(value) if isinstance(value, (int, float, Float)) else 0
                for value in sublist
            ]
            self.cleaned_values.append(cleaned_sublist)

        # Анализ значений
        all_vals = np.concatenate(self.cleaned_values) if len(self.cleaned_values) > 0 else [0]
        lower_bound = np.percentile(all_vals, 5)
        upper_bound = np.percentile(all_vals, 95)
        self.min_val = lower_bound
        self.max_val = upper_bound
        self.max_val_without_padd = np.max(all_vals)
        self.min_val_without_padd = np.min(all_vals)

        # Padding
        val_range = self.max_val - self.min_val
        padding = val_range * 0.3 if val_range != 0 else 1.0
        self.min_val -= padding
        self.max_val += padding
        if self.min_val > 0:
            self.min_val = -padding
        if self.max_val < 0:
            self.max_val = padding

        # Подготовка позиционирования
        self._compute_y_mapping()

    def _compute_y_mapping(self):
        """Вычисляет позиционирование по вертикали"""
        gap_size = 20
        
        # Добавляем по одной дополнительной ячейке сверху и снизу для отступов
        num_categories_with_padding = len(self.x_values) + 2
        
        total_bar_height = (self.widget_height - gap_size * (num_categories_with_padding - 1)) // num_categories_with_padding
        parallelepiped_height = total_bar_height // len(self.cleaned_values)

        # y_positions[i][j] - Y-координата для серии i в категории j
        self.y_positions = [[0] * num_categories_with_padding for _ in range(len(self.cleaned_values))]
        
        for j in range(num_categories_with_padding):
            y_start = j * (total_bar_height + gap_size)
            for i in range(len(self.cleaned_values)):
                y_center = self.window_start + y_start + i * parallelepiped_height + parallelepiped_height // 2
                y_center = int(max(self.window_start, min(self.window_start + self.widget_height - 1, y_center)))
                self.y_positions[i][j] = y_center

        self._parallelepiped_height = parallelepiped_height
        self._num_categories_with_padding = num_categories_with_padding

    def value_to_x(self, value):
        """Преобразует значение в X-координату (горизонтальная ось)"""
        denom = (self.max_val - self.min_val) if (self.max_val - self.min_val) != 0 else 1.0
        rel = (value - self.min_val) / denom
        x = int(self.window_start + rel * self.widget_width)
        x = max(self.window_start, min(self.window_start + self.widget_width, x))
        return x

    def draw_legend(self, painter):
        """Легенда как в triangle"""
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

        item_widths = [
            box_size + text_offset + painter.fontMetrics().horizontalAdvance(item.text()) + gap
            for item in self.function_input
        ] if self.function_input else []
        total_width = sum(item_widths) - gap if item_widths else 0

        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawRect(legend_start_x - 5, self.widget_height, total_width + 10, self.window_start)

        current_x = legend_start_x
        if self.function_input:
            for i, item in enumerate(self.function_input):
                color = bar_styles[i % len(bar_styles)]
                painter.setBrush(QBrush(color))
                painter.drawRect(current_x, legend_start_y, box_size, box_size)
                painter.drawText(current_x + text_offset, legend_start_y + box_size // 2 + 5, item.text())
                current_x += item_widths[i]

    def draw_grid(self, painter, style):
        """Сетка как в triangle, но повернутая на 90°"""
        if not self.valid:
            return

        pen = QPen(style.grid_color)
        pen.setWidth(style.grid_width)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)

        # ВЕРТИКАЛЬНЫЕ ЛИНИИ - значения
        max_value = float(np.max([abs(self.min_val_without_padd), self.max_val_without_padd]))
        if max_value == 0:
            max_value = float(self.max_val) if self.max_val != 0 else 1.0

        # Сетка значений как в triangle
        step = max_value / 4
        value_positions = []
        current_val = 0
        while current_val <= max_value * 1.2:
            value_positions.append(current_val)
            current_val += step
        
        # Рисуем вертикальные линии
        for val in value_positions:
            if val == 0:
                continue
                
            x_pos = self.value_to_x(val)
            painter.drawLine(x_pos, 0, x_pos, self.widget_height)
            painter.drawText(x_pos + 2, self.widget_height - 5, f"{val:.3f}")

            if val != 0:
                x_neg = self.value_to_x(-val)
                painter.drawLine(x_neg, 0, x_neg, self.widget_height)
                painter.drawText(x_neg + 2, self.widget_height - 5, f"-{val:.3f}")

        # ГОРИЗОНТАЛЬНЫЕ ЛИНИИ - категории
        # Рисуем линии только для реальных категорий (пропускаем дополнительные ячейки)
        for j in range(1, self._num_categories_with_padding - 1):
            y_positions = [self.y_positions[i][j] for i in range(len(self.cleaned_values))]
            if y_positions:
                y_mapped = int(np.mean(y_positions))
                painter.drawLine(self.window_start, y_mapped, self.window_start + self.widget_width, y_mapped)
                
                # Подписываем реальные категории
                cat_index = j - 1
                if cat_index < len(self.x_values):
                    painter.drawText(5, y_mapped + 5, f"{self.x_values[cat_index]:.2f}")

        # РАМКА СЕТКИ
        painter.drawLine(self.window_start, 0, self.window_start + self.widget_width, 0)  # верх
        painter.drawLine(self.window_start, self.widget_height, self.window_start + self.widget_width, self.widget_height)  # низ
        painter.drawLine(self.window_start, 0, self.window_start, self.widget_height)  # лево
        painter.drawLine(self.window_start + self.widget_width, 0, self.window_start + self.widget_width, self.widget_height)  # право

    def draw_zero_line(self, painter, style):
        """Рисует нулевую линию поверх блоков"""
        if not self.valid:
            return
            
        zero_x = self.value_to_x(0)
        pen = QPen(style.grid_black)
        pen.setWidth(style.grid_width + 1)
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(zero_x, 0, zero_x, self.widget_height)

    def draw_parallelepiped(self, painter, y_center, x_start, x_end, height, color):
        """Рисует параллелепипед (горизонтальный блок)"""
        depth = 8  # глубина 3D эффекта
        half_height = height // 2

        # Передняя грань
        front_top_left = QPoint(x_start, y_center - half_height)
        front_top_right = QPoint(x_end, y_center - half_height)
        front_bottom_right = QPoint(x_end, y_center + half_height)
        front_bottom_left = QPoint(x_start, y_center + half_height)

        # Задняя грань (смещена по глубине)
        back_top_left = QPoint(front_top_left.x() + depth, front_top_left.y() - depth)
        back_top_right = QPoint(front_top_right.x() + depth, front_top_right.y() - depth)
        back_bottom_right = QPoint(front_bottom_right.x() + depth, front_bottom_right.y() - depth)
        back_bottom_left = QPoint(front_bottom_left.x() + depth, front_bottom_left.y() - depth)

        painter.setPen(Qt.NoPen)

        # Боковая грань (правая)
        painter.setBrush(QBrush(color.darker(140)))
        painter.drawPolygon(QPolygon([front_top_right, front_bottom_right, back_bottom_right, back_top_right]))

        # Верхняя грань
        painter.setBrush(QBrush(color.lighter(130)))
        painter.drawPolygon(QPolygon([front_top_left, front_top_right, back_top_right, back_top_left]))

        # Передняя грань
        painter.setBrush(QBrush(color))
        painter.drawPolygon(QPolygon([front_top_left, front_top_right, front_bottom_right, front_bottom_left]))

        # Контуры
        pen = QPen(Qt.black)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        
        # Контур передней грани
        painter.drawPolygon(QPolygon([front_top_left, front_top_right, front_bottom_right, front_bottom_left]))
        # Контур верхней грани
        painter.drawPolygon(QPolygon([front_top_left, front_top_right, back_top_right, back_top_left]))
        # Контур боковой грани
        painter.drawPolygon(QPolygon([front_top_right, front_bottom_right, back_bottom_right, back_top_right]))

    def draw_plot(self, painter):
        """Основная отрисовка параллелепипедов"""
        if not self.valid:
            return

        bar_styles = [
            QColor(210, 0, 107),
            QColor(255, 108, 0),
            QColor(0, 158, 142),
            QColor(149, 236, 0)
        ]

        # Нулевая позиция
        zero_x = self.value_to_x(0)

        # Рисуем параллелепипеды только для реальных категорий (пропускаем дополнительные ячейки)
        for j_real in range(len(self.x_values)):
            # Смещаем индекс для учета дополнительной ячейки сверху
            j = j_real + 1
            
            for i, data_series in enumerate(self.cleaned_values):
                if j_real >= len(data_series):
                    continue
                    
                color = bar_styles[i % len(bar_styles)]
                y_center = self.y_positions[i][j]
                value = data_series[j_real]
                
                # Определяем границы блока
                x_val = self.value_to_x(value)
                x_start = min(zero_x, x_val)
                x_end = max(zero_x, x_val)
                
                if x_start == x_end:
                    continue  # пропускаем нулевые значения

                # Ограничиваем координаты
                x_start = max(self.window_start, x_start)
                x_end = min(self.window_start + self.widget_width, x_end)

                # Рисуем параллелепипед
                self.draw_parallelepiped(painter, y_center, x_start, x_end, 
                                       self._parallelepiped_height - 4, color)

        # Легенда
        self.draw_legend(painter)