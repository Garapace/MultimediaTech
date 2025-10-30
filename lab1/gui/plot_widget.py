from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter
from plots import PlotStyle, PlotRectangle, PlotTriangle


class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.plot_type = None
        self.x_values = None
        self.y_values = None
        self.function_input = None

        self.setMinimumSize(600, 600)
        self.style = PlotStyle()

    def set_data(self, plot_type, x_values, y_values, function_input):
        self.x_values = x_values
        self.y_values = y_values
        self.plot_type = plot_type
        self.function_input = function_input
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # фон
        painter.setBrush(self.style.background_color)
        painter.drawRect(self.rect())

        # создаём нужный объект
        if self.plot_type == "Gistogram triangle":
            plot_obj = PlotTriangle(self.x_values, self.y_values, self.function_input, self.width(), self.height())
        elif self.plot_type == "Linear rectangle":
            plot_obj = PlotRectangle(self.x_values, self.y_values, self.function_input, self.width(), self.height())
        else:
            plot_obj = PlotRectangle(self.x_values, self.y_values, self.function_input, self.width(), self.height())

        # рисуем обязательно в порядке: сетка (без нуля), блоки, нулевая линия поверх
        if hasattr(plot_obj, "draw_grid"):
            plot_obj.draw_grid(painter, self.style)

        if hasattr(plot_obj, "draw_plot"):
            plot_obj.draw_plot(painter)

        # рисуем нулевую линию поверх (если есть метод)
        if hasattr(plot_obj, "draw_zero_line"):
            plot_obj.draw_zero_line(painter, self.style)
        else:
            # для обратной совместимости: если draw_grid рисует ноль — ничего не делаем
            pass

        painter.end()
    