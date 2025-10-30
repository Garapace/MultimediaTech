from PySide6.QtWidgets import QMainWindow, QWidget, QLineEdit, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QComboBox
from .plot_widget import PlotWidget
from data import DataProcessor
from plots.plot_generator import PlotGenerator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph Visualization App")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Создание виджетов
        self.plot_widget = PlotWidget()
        self.function_inputs = []
        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("Enter range (e.g., 0,10,100)")
        self.range_input.setText("1,10,7")
        self.add_function_button = QPushButton("Add Function")
        self.plot_button = QPushButton("Plot")
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems(["Linear rectangle", "Gistogram triangle"])
        self.plot_type_combo.setCurrentText("3D Bar Chart")

        # Установка макета
        main_layout = QVBoxLayout(self.central_widget)
        self.function_layout = QVBoxLayout()

        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("Range:"))
        range_layout.addWidget(self.range_input)

        plot_type_layout = QHBoxLayout()
        plot_type_layout.addWidget(QLabel("Plot Type:"))
        plot_type_layout.addWidget(self.plot_type_combo)

        main_layout.addLayout(range_layout)
        main_layout.addLayout(plot_type_layout)
        main_layout.addLayout(self.function_layout)
        main_layout.addWidget(self.add_function_button)
        main_layout.addWidget(self.plot_button)
        main_layout.addWidget(self.plot_widget)

        # Добавление первого ввода функции
        self.add_function_input()

        # Подключение сигналов и слотов
        self.add_function_button.clicked.connect(self.add_function_input)
        self.plot_button.clicked.connect(self.plot_graph)

    def add_function_input(self):
        # Создаем горизонтальный контейнер для ввода функции и выпадающего списка
        function_container = QWidget()
        function_layout = QHBoxLayout(function_container)
        
        # Создаем выпадающий список с примерами
        example_combo = QComboBox()
        example_combo.addItems([
            "Выберите пример...",
            "10 * sin(x)",
            "10 * sin(2*x + exp(cos(abs(x))))"
        ])
        example_combo.setMaximumWidth(200)
        
        # Создаем поле ввода функции
        function_input = QLineEdit()
        function_input.setPlaceholderText("Enter function (e.g., np.sin(x))")
        
        # Создаем кнопку удаления
        delete_button = QPushButton("Удалить")
        delete_button.setMaximumWidth(80)
        delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; border: none; padding: 5px; }")
        
        # Добавляем виджеты в контейнер
        function_layout.addWidget(QLabel("Function:"))
        function_layout.addWidget(function_input)
        function_layout.addWidget(QLabel("Examples:"))
        function_layout.addWidget(example_combo)
        function_layout.addWidget(delete_button)
        
        # Сохраняем ссылки на виджеты
        self.function_inputs.append(function_input)
        if len(self.function_inputs) == 1:
            function_input.setText("10 * sin(x)")
        
        # Подключаем обработчик выбора примера
        example_combo.currentTextChanged.connect(
            lambda text, input_field=function_input: self.on_example_selected(text, input_field)
        )
        
        # Подключаем обработчик удаления функции
        delete_button.clicked.connect(
            lambda: self.remove_function_input(function_container, function_input)
        )
        
        # Добавляем контейнер в основной макет
        self.function_layout.addWidget(function_container)

    def on_example_selected(self, example_text, input_field):
        """Обработчик выбора примера из выпадающего списка"""
        if example_text != "Выберите пример...":
            input_field.setText(example_text)

    def remove_function_input(self, container, function_input):
        """Удаляет функцию из интерфейса и из списка"""
        # Удаляем из списка function_inputs
        if function_input in self.function_inputs:
            self.function_inputs.remove(function_input)
        
        # Удаляем контейнер из макета
        self.function_layout.removeWidget(container)
        container.deleteLater()

    def plot_graph(self):
        plot_type = self.plot_type_combo.currentText()
        data_processor = DataProcessor(self.function_inputs, self.range_input.text())
        x_values, y_values = data_processor.process_data()

        plot_generator = PlotGenerator(plot_type, x_values, y_values, self.function_inputs)
        plot_generator.generate_plot(self.plot_widget)

# Пример использования
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
