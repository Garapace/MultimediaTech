import sys
import math
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QSlider, QLabel, QPushButton, QScrollArea,
                               QSizePolicy, QGroupBox)
from PySide6.QtGui import (QPainter, QPen, QBrush, QColor, QPolygonF,
                           QLinearGradient)
from PySide6.QtCore import Qt, QPoint, QPointF
from enum import Enum




class DisplayMode(Enum):
    POINTS = "Точки"
    WIREFRAME = "Каркас"
    FILLED = "Заливка"


class Vector3D:
    def __init__(self, x, y, z):
        """Инициализация 3D вектора с координатами x, y, z."""
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        """Сложение двух векторов."""
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        """Вычитание двух векторов."""
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        """Умножение вектора на скаляр."""
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __neg__(self):
        """Унарное отрицание вектора."""
        return Vector3D(-self.x, -self.y, -self.z)

    def length(self):
        """Вычисление длины вектора."""
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalized(self):
        """Нормализация вектора (приведение к единичной длине)."""
        length = self.length()
        if length == 0:
            return Vector3D(0, 0, 0)
        return Vector3D(self.x / length, self.y / length, self.z / length)

    def dot(self, other):
        """Скалярное произведение двух векторов."""
        return self.x * other.x + self.y * other.y + self.z * other.z


class Matrix4x4:
    def __init__(self):
        """Инициализация матрицы 4x4 (единичная матрица по умолчанию)."""
        self.m = [[0] * 4 for _ in range(4)]
        self.m[0][0] = 1
        self.m[1][1] = 1
        self.m[2][2] = 1
        self.m[3][3] = 1

    def __mul__(self, other):
        """Умножение матрицы на вектор или другую матрицу."""
        if isinstance(other, Vector3D):
            x = self.m[0][0] * other.x + self.m[0][1] * other.y + self.m[0][2] * other.z + self.m[0][3]
            y = self.m[1][0] * other.x + self.m[1][1] * other.y + self.m[1][2] * other.z + self.m[1][3]
            z = self.m[2][0] * other.x + self.m[2][1] * other.y + self.m[2][2] * other.z + self.m[2][3]
            w = self.m[3][0] * other.x + self.m[3][1] * other.y + self.m[3][2] * other.z + self.m[3][3]
            if w != 0:
                x /= w
                y /= w
                z /= w
            return Vector3D(x, y, z)
        elif isinstance(other, Matrix4x4):
            result = Matrix4x4()
            for i in range(4):
                for j in range(4):
                    result.m[i][j] = sum(self.m[i][k] * other.m[k][j] for k in range(4))
            return result

    def transform_vector(self, v):
        """Трансформация вектора (направления) с использованием только линейной части матрицы."""
        x = self.m[0][0] * v.x + self.m[0][1] * v.y + self.m[0][2] * v.z
        y = self.m[1][0] * v.x + self.m[1][1] * v.y + self.m[1][2] * v.z
        z = self.m[2][0] * v.x + self.m[2][1] * v.y + self.m[2][2] * v.z
        return Vector3D(x, y, z)

    @staticmethod
    def from_linear(linear):
        """Создание Matrix4x4 из 3x3 линейной части."""
        mat = Matrix4x4()
        for i in range(3):
            for j in range(3):
                mat.m[i][j] = linear[i][j]
        mat.m[0][3] = 0
        mat.m[1][3] = 0
        mat.m[2][3] = 0
        mat.m[3][0] = 0
        mat.m[3][1] = 0
        mat.m[3][2] = 0
        mat.m[3][3] = 1
        return mat

    @staticmethod
    def translation(x, y, z):
        """Создание матрицы переноса на вектор (x, y, z)."""
        mat = Matrix4x4()
        mat.m[0][3] = x
        mat.m[1][3] = y
        mat.m[2][3] = z
        return mat

    @staticmethod
    def rotation_x(angle):
        """Создание матрицы поворота вокруг оси X на угол angle (в градусах)."""
        mat = Matrix4x4()
        rad = math.radians(angle)
        mat.m[1][1] = math.cos(rad)
        mat.m[1][2] = -math.sin(rad)
        mat.m[2][1] = math.sin(rad)
        mat.m[2][2] = math.cos(rad)
        return mat

    @staticmethod
    def rotation_y(angle):
        """Создание матрицы поворота вокруг оси Y на угол angle (в градусах)."""
        mat = Matrix4x4()
        rad = math.radians(angle)
        mat.m[0][0] = math.cos(rad)
        mat.m[0][2] = math.sin(rad)
        mat.m[2][0] = -math.sin(rad)
        mat.m[2][2] = math.cos(rad)
        return mat

    @staticmethod
    def rotation_z(angle):
        """Создание матрицы поворота вокруг оси Z на угол angle (в градусах)."""
        mat = Matrix4x4()
        rad = math.radians(angle)
        mat.m[0][0] = math.cos(rad)
        mat.m[0][1] = -math.sin(rad)
        mat.m[1][0] = math.sin(rad)
        mat.m[1][1] = math.cos(rad)
        return mat

    @staticmethod
    def scaling(sx, sy, sz):
        """Создание матрицы масштабирования с коэффициентами sx, sy, sz."""
        mat = Matrix4x4()
        mat.m[0][0] = sx
        mat.m[1][1] = sy
        mat.m[2][2] = sz
        return mat

    def inverse_rotation(self):
        """Получение обратной матрицы поворота (транспонирование 3x3 части)."""
        result = Matrix4x4()
        for i in range(3):
            for j in range(3):
                result.m[i][j] = self.m[j][i]
        return result


class Face:
    def __init__(self, vertices, color):
        """Инициализация грани с заданными вершинами и цветом."""
        self.vertices = vertices
        self.color = color
        self.normal = self.calculate_normal()
        self.center = self.calculate_center()

    def is_visible(self, camera_pos):
        """Проверяет, видима ли грань с позиции камеры (алгоритм Робертса)."""
        view_dir = (self.center - camera_pos).normalized()
        return self.normal.dot(view_dir) > 0

    def calculate_normal(self):
        """Вычисление нормали грани по трем вершинам."""
        if len(self.vertices) < 3:
            return Vector3D(0, 0, 0)
        v1 = self.vertices[1] - self.vertices[0]
        v2 = self.vertices[2] - self.vertices[0]
        normal = Vector3D(
            v1.y * v2.z - v1.z * v2.y,
            v1.z * v2.x - v1.x * v2.z,
            v1.x * v2.y - v1.y * v2.x
        )
        return normal.normalized()

    def calculate_center(self):
        """Вычисление центра грани как среднего положения вершин."""
        if not self.vertices:
            return Vector3D(0, 0, 0)
        x = sum(v.x for v in self.vertices) / len(self.vertices)
        y = sum(v.y for v in self.vertices) / len(self.vertices)
        z = sum(v.z for v in self.vertices) / len(self.vertices)
        return Vector3D(x, y, z)


class Letter3D:
    def __init__(self, height, width, depth, offset_x=0, letter_type='M'):
        """Инициализация 3D буквы с заданными размерами, смещением и типом ('M' или 'C')."""
        self.height = height
        self.width = width
        self.depth = depth
        self.offset_x = offset_x
        self.letter_type = letter_type
        self.vertices = []
        self.faces = []
        self.transform = Matrix4x4.rotation_x(180)  # Начальная трансформация: перевернуть вверх ногами
        self.scale = 2.0  # Индивидуальный масштаб для каждой буквы
        self.update_geometry()

    def update_geometry(self):
        """Обновление геометрии буквы: создание вершин и граней."""
        self.vertices = []
        self.faces = []
        h, w, d, ox = self.height, self.width, self.depth, self.offset_x
        bar_thickness = h * 0.2

        if self.letter_type == 'M':
            self.create_letter_M(h, w, d, ox, bar_thickness)
        else:
            self.create_letter_C(h, w, d, ox, bar_thickness)

    def create_letter_M(self, h, w, d, ox, bar_thickness):
        """Создание геометрии буквы 'Д' с заданными параметрами."""
        hw = w / 2
        hd = d / 2
        
        # Увеличиваем ширину для нижней части
        bottom_width_multiplier = 1.5  # Коэффициент увеличения ширины нижней части
        bottom_hw = hw * bottom_width_multiplier
        
        # Верхняя горизонтальная линия
        front_top = [
            Vector3D(ox - hw, h, -hd), Vector3D(ox + hw, h, -hd),
            Vector3D(ox + hw, h - bar_thickness, -hd), Vector3D(ox - hw, h - bar_thickness, -hd)
        ]
        back_top = [
            Vector3D(ox - hw, h, hd), Vector3D(ox + hw, h, hd),
            Vector3D(ox + hw, h - bar_thickness, hd), Vector3D(ox - hw, h - bar_thickness, hd)
        ]
        
        # Левая вертикальная линия (сверху до низа)
        front_left = [
            Vector3D(ox - hw, h, -hd), Vector3D(ox - hw + bar_thickness, h, -hd),
            Vector3D(ox - hw + bar_thickness, 0, -hd), Vector3D(ox - hw, 0, -hd)
        ]
        back_left = [
            Vector3D(ox - hw, h, hd), Vector3D(ox - hw + bar_thickness, h, hd),
            Vector3D(ox - hw + bar_thickness, 0, hd), Vector3D(ox - hw, 0, hd)
        ]
        
        # Правая вертикальная линия (сверху до низа)
        front_right = [
            Vector3D(ox + hw - bar_thickness, h, -hd), Vector3D(ox + hw, h, -hd),
            Vector3D(ox + hw, 0, -hd), Vector3D(ox + hw - bar_thickness, 0, -hd)
        ]
        back_right = [
            Vector3D(ox + hw - bar_thickness, h, hd), Vector3D(ox + hw, h, hd),
            Vector3D(ox + hw, 0, hd), Vector3D(ox + hw - bar_thickness, 0, hd)
        ]
        
        # Нижняя горизонтальная линия (более длинная, с ножками)
        leg_height = bar_thickness * 1.3  # Высота ножек
        front_bottom = [
            Vector3D(ox - bottom_hw, 0, -hd), Vector3D(ox + bottom_hw, 0, -hd),
            Vector3D(ox + bottom_hw, -leg_height, -hd), Vector3D(ox - bottom_hw, -leg_height, -hd)
        ]
        back_bottom = [
            Vector3D(ox - bottom_hw, 0, hd), Vector3D(ox + bottom_hw, 0, hd),
            Vector3D(ox + bottom_hw, -leg_height, hd), Vector3D(ox - bottom_hw, -leg_height, hd)
        ]
        
        # Левая ножка (под расширенной нижней горизонталью)
        front_left_leg = [
            Vector3D(ox - bottom_hw, -leg_height, -hd), Vector3D(ox - bottom_hw + bar_thickness, -leg_height, -hd),
            Vector3D(ox - bottom_hw + bar_thickness, -leg_height * 2, -hd), Vector3D(ox - bottom_hw, -leg_height * 2, -hd)
        ]
        back_left_leg = [
            Vector3D(ox - bottom_hw, -leg_height, hd), Vector3D(ox - bottom_hw + bar_thickness, -leg_height, hd),
            Vector3D(ox - bottom_hw + bar_thickness, -leg_height * 2, hd), Vector3D(ox - bottom_hw, -leg_height * 2, hd)
        ]
        
        # Правая ножка (под расширенной нижней горизонталью)
        front_right_leg = [
            Vector3D(ox + bottom_hw - bar_thickness, -leg_height, -hd), Vector3D(ox + bottom_hw, -leg_height, -hd),
            Vector3D(ox + bottom_hw, -leg_height * 2, -hd), Vector3D(ox + bottom_hw - bar_thickness, -leg_height * 2, -hd)
        ]
        back_right_leg = [
            Vector3D(ox + bottom_hw - bar_thickness, -leg_height, hd), Vector3D(ox + bottom_hw, -leg_height, hd),
            Vector3D(ox + bottom_hw, -leg_height * 2, hd), Vector3D(ox + bottom_hw - bar_thickness, -leg_height * 2, hd)
        ]

        self.vertices = (front_top + back_top + front_left + back_left + front_right + back_right +
                        front_bottom + back_bottom + front_left_leg + back_left_leg + front_right_leg + back_right_leg)
        
        colors = [QColor(0, 0, 200), QColor(0, 0, 163), QColor(0, 0, 122)]

        self._create_faces_for_part(front_top, back_top, colors)
        self._create_faces_for_part(front_left, back_left, colors)
        self._create_faces_for_part(front_right, back_right, colors)
        self._create_faces_for_part(front_bottom, back_bottom, colors)
        self._create_faces_for_part(front_left_leg, back_left_leg, colors)
        self._create_faces_for_part(front_right_leg, back_right_leg, colors)

    def create_letter_C(self, h, w, d, ox, bar_thickness):
        """Создание геометрии буквы 'C' с заданными параметрами."""
        # Увеличиваем размер буквы С чтобы соответствовать размеру Д
        scale_factor = 1.5  # Такой же коэффициент увеличения как у буквы Д
        scaled_h = h * scale_factor
        scaled_w = w * scale_factor
        
        hw = scaled_w / 2
        hd = d / 2
        
        # Смещение вниз на высоту ножек буквы Д
        leg_height = bar_thickness * 1.3  # Такая же высота ножек как у буквы Д
        y_offset = -leg_height * 2  # Смещение вниз на полную высоту ножек
        
        # Левая вертикальная линия
        front_left = [
            Vector3D(ox - hw, scaled_h + y_offset, -hd), Vector3D(ox - hw + bar_thickness, scaled_h + y_offset, -hd),
            Vector3D(ox - hw + bar_thickness, 0 + y_offset, -hd), Vector3D(ox - hw, 0 + y_offset, -hd)
        ]
        back_left = [
            Vector3D(ox - hw, scaled_h + y_offset, hd), Vector3D(ox - hw + bar_thickness, scaled_h + y_offset, hd),
            Vector3D(ox - hw + bar_thickness, 0 + y_offset, hd), Vector3D(ox - hw, 0 + y_offset, hd)
        ]
        
        # Верхняя горизонтальная линия
        front_top = [
            Vector3D(ox - hw + bar_thickness, scaled_h + y_offset, -hd), Vector3D(ox + hw, scaled_h + y_offset, -hd),
            Vector3D(ox + hw, scaled_h - bar_thickness + y_offset, -hd), Vector3D(ox - hw + bar_thickness, scaled_h - bar_thickness + y_offset, -hd)
        ]
        back_top = [
            Vector3D(ox - hw + bar_thickness, scaled_h + y_offset, hd), Vector3D(ox + hw, scaled_h + y_offset, hd),
            Vector3D(ox + hw, scaled_h - bar_thickness + y_offset, hd), Vector3D(ox - hw + bar_thickness, scaled_h - bar_thickness + y_offset, hd)
        ]
        
        # Нижняя горизонтальная линия
        front_bottom = [
            Vector3D(ox - hw + bar_thickness, bar_thickness + y_offset, -hd), Vector3D(ox + hw, bar_thickness + y_offset, -hd),
            Vector3D(ox + hw, 0 + y_offset, -hd), Vector3D(ox - hw + bar_thickness, 0 + y_offset, -hd)
        ]
        back_bottom = [
            Vector3D(ox - hw + bar_thickness, bar_thickness + y_offset, hd), Vector3D(ox + hw, bar_thickness + y_offset, hd),
            Vector3D(ox + hw, 0 + y_offset, hd), Vector3D(ox - hw + bar_thickness, 0 + y_offset, hd)
        ]

        self.vertices = (front_left + back_left + front_top + back_top + 
                        front_bottom + back_bottom)
        colors = [QColor(0, 102, 204), QColor(0, 82, 163), QColor(0, 61, 122)]

        self._create_faces_for_part(front_left, back_left, colors)
        self._create_faces_for_part(front_top, back_top, colors)
        self._create_faces_for_part(front_bottom, back_bottom, colors)

    def _create_faces_for_part(self, front_vertices, back_vertices, colors):
        """Создание граней для части буквы (передняя, задняя и боковые грани)."""
        self.faces.append(Face([front_vertices[0], front_vertices[1], front_vertices[2], front_vertices[3]], colors[0]))
        self.faces.append(Face([back_vertices[0], back_vertices[3], back_vertices[2], back_vertices[1]], colors[0]))

        for i in range(len(front_vertices)):
            next_i = (i + 1) % len(front_vertices)
            side_face = [
                front_vertices[i],
                back_vertices[i],
                back_vertices[next_i],
                front_vertices[next_i]
            ]
            v1 = side_face[1] - side_face[0]
            v2 = side_face[2] - side_face[0]
            normal = Vector3D(
                v1.y * v2.z - v1.z * v2.y,
                v1.z * v2.x - v1.x * v2.z,
                v1.x * v2.y - v1.y * v2.x
            ).normalized()
            center = Vector3D(
                sum(v.x for v in side_face) / 4,
                sum(v.y for v in side_face) / 4,
                sum(v.z for v in side_face) / 4
            )
            to_center = center * (-1)
            if normal.dot(to_center) < 0:
                side_face = [front_vertices[i], front_vertices[next_i], back_vertices[next_i], back_vertices[i]]
            self.faces.append(Face(side_face, colors[1]))

        if len(front_vertices) >= 4:
            top_face = [front_vertices[0], front_vertices[1], back_vertices[1], back_vertices[0]]
            bottom_face = [front_vertices[3], front_vertices[2], back_vertices[2], back_vertices[3]]
            self.faces.append(Face(top_face, colors[2]))
            self.faces.append(Face(bottom_face, colors[2]))

    def rotate(self, axis, angle):
        """Поворот буквы вокруг заданной оси на угол angle."""
        if axis == 0:
            rot = Matrix4x4.rotation_x(angle)
        elif axis == 1:
            rot = Matrix4x4.rotation_y(angle)
        else:
            rot = Matrix4x4.rotation_z(angle)
        self.transform = rot * self.transform

    def set_scale(self, scale_factor):
        """Установка масштаба буквы."""
        self.scale = scale_factor


class SceneWidget(QWidget):
    def __init__(self):
        """Инициализация виджета сцены с 3D буквами."""
        super().__init__()
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(50, 50, 50))
        self.setPalette(p)
        self.m_letter = Letter3D(100, 60, 30, offset_x=-60, letter_type='M')
        self.c_letter = Letter3D(100, 60, 30, offset_x=60, letter_type='C')
        self.camera_pos = Vector3D(0, 0, -400)
        self.camera_rot = [0, 0, 0]
        self.object_transform = Matrix4x4()
        self.scale = 1.2
        self.base_scale = 2.0
        self.auto_scale = True
        self.display_mode = DisplayMode.FILLED
        self.mirror_x = False
        self.mirror_y = False
        self.mirror_z = False
        self.cached_faces = None
        self.cache_valid = False

    def invalidate_cache(self):
        """Сброс кэша граней для перерисовки."""
        self.cache_valid = False


    def prepare_faces_cache(self):
        """Подготовка кэша граней для рендеринга с учетом трансформаций и алгоритма Робертса."""
        width, height = self.width(), self.height()
        self.cached_faces = []

        for letter in [self.m_letter, self.c_letter]:
            # Применение масштабирования для буквы
            scale_matrix = Matrix4x4.scaling(letter.scale, letter.scale, letter.scale)
            # Комбинирование трансформаций объекта, буквы и масштабирования
            letter_transform = self.object_transform * letter.transform * scale_matrix

            # Вычисление матрицы для нормалей (обратная транспонированная линейной части)
            temp_transform = self.object_transform * letter.transform
            s = letter.scale
            linear_part = [[temp_transform.m[i][j] for j in range(4)] for i in range(4)]
            for i in range(4):
                for j in range(4):
                    linear_part[i][j] *= 1 / s if s != 0 else 1
            normal_transform = Matrix4x4.from_linear(linear_part)

            # Трансформация вершин и вычисление нормалей вершин
            transformed_vertices = []
            vertex_normals = []
            for v in letter.vertices:
                normal_sum = Vector3D(0, 0, 0)
                count = 0
                for face in letter.faces:
                    if v in face.vertices and not getattr(face, 'is_internal', False):
                        normal_sum += face.normal
                        count += 1
                vertex_normal = normal_sum.normalized() if count > 0 else Vector3D(0, 0, 1)
                v_transformed = letter_transform * v
                v_camera = self.apply_camera_transform(v_transformed)
                transformed_vertices.append(v_camera)
                transformed_normal = normal_transform.transform_vector(vertex_normal).normalized()
                vertex_normals.append(transformed_normal)

            # Обработка каждой грани
            for face in letter.faces:
                face_vertices = [transformed_vertices[letter.vertices.index(v)] for v in face.vertices]
                face_normals = [vertex_normals[letter.vertices.index(v)] for v in face.vertices]
                original_vertices = face.vertices

                if len(face_vertices) < 3:
                    continue

                # Проверка видимости грани
                face_center_world = Vector3D(0, 0, 0)
                for v in face.vertices:
                    face_center_world += v
                face_center_world *= 1.0 / len(face.vertices)
                face_center_world = letter_transform * face_center_world

                # Трансформация нормали грани в пространство камеры
                face_normal = normal_transform.transform_vector(face.normal).normalized()
                
                # Отключаем отсечение граней - полагаемся на правильный порядок отрисовки
                # Это позволит отображать все грани и избежать проблем с неправильным отсечением

                # Вычисление центра грани в пространстве камеры
                face_center = Vector3D(0, 0, 0)
                for v in face_vertices:
                    face_center += v
                face_center *= 1.0 / len(face_vertices)

                # Проецирование вершин на экранное пространство
                screen_points = []
                valid = True
                for i, v in enumerate(face_vertices):
                    if v.z <= 0:  # Пропуск, если вершина за камерой
                        valid = False
                        break
                    factor = 500 / (v.z + 300)
                    aspect = width / height
                    px = v.x * factor * self.base_scale * (1 / aspect if aspect > 1 else 1) + width / 2
                    py = v.y * factor * self.base_scale * (1 if aspect > 1 else aspect) + height / 2
                    screen_points.append(QPointF(px, py))

                if valid and len(screen_points) >= 3:
                    avg_depth = sum(v.z for v in face_vertices) / len(face_vertices)
                    self.cached_faces.append((avg_depth, face, screen_points))

        # Сортировка граней по глубине (от дальних к ближним)
        self.cached_faces.sort(reverse=True, key=lambda x: x[0])


    def paintEvent(self, event):
        """Отрисовка сцены с учетом текущего режима отображения и закраски."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, self.display_mode != DisplayMode.POINTS)
        painter.fillRect(self.rect(), QColor(0, 0, 256))

        if not self.cache_valid or self.cached_faces is None:
            self.prepare_faces_cache()
            self.cache_valid = True

        for depth, face, screen_points in self.cached_faces:
            polygon = QPolygonF(screen_points)

            if self.display_mode == DisplayMode.POINTS:
                painter.setPen(QPen(face.color, 5))
                for point in screen_points:
                    painter.drawPoint(point)

            elif self.display_mode == DisplayMode.WIREFRAME:
                painter.setPen(QPen(face.color, 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawPolygon(polygon)

            elif self.display_mode == DisplayMode.FILLED:
                # Простая закраска без освещения
                painter.setPen(QPen(face.color, 1))
                painter.setBrush(QBrush(face.color))
                painter.drawPolygon(polygon)


    def project_point(self, point):
        """Проецирование 3D точки на 2D экран с учетом общей трансформации."""
        v_transformed = self.object_transform * point
        v_camera = self.apply_camera_transform(v_transformed)
        if v_camera.z > 0:
            factor = 300 / v_camera.z
            aspect_ratio = self.width() / self.height()
            px = v_camera.x * factor * self.base_scale * (
                1 / aspect_ratio if aspect_ratio > 1 else 1) + self.width() / 2
            py = v_camera.y * factor * self.base_scale * (1 if aspect_ratio > 1 else aspect_ratio) + self.height() / 2
            return QPoint(int(px), int(py))
        return QPoint(-1000, -1000)

    def project_point_without_object_transform(self, point):
        """Проецирование 3D точки на 2D экран без учета общей трансформации."""
        v_camera = self.apply_camera_transform(point)
        if v_camera.z > 0:
            factor = 300 / v_camera.z
            aspect_ratio = self.width() / self.height()
            px = v_camera.x * factor * self.base_scale * (
                1 / aspect_ratio if aspect_ratio > 1 else 1) + self.width() / 2
            py = v_camera.y * factor * self.base_scale * (1 if aspect_ratio > 1 else aspect_ratio) + self.height() / 2
            return QPoint(int(px), int(py))
        return QPoint(-1000, -1000)

    def apply_camera_transform(self, v):
        """Применение трансформации камеры к 3D точке."""
        rot_x = Matrix4x4.rotation_x(self.camera_rot[0])
        rot_y = Matrix4x4.rotation_y(self.camera_rot[1])
        rot_z = Matrix4x4.rotation_z(self.camera_rot[2])
        rotation = rot_x * rot_y * rot_z
        translation = Matrix4x4.translation(-self.camera_pos.x, -self.camera_pos.y, -self.camera_pos.z)
        camera_transform = rotation * translation
        return camera_transform * v

    def auto_scale_view(self):
        """Автоматическое масштабирование сцены в зависимости от размера окна."""
        if self.auto_scale:
            self.base_scale = min(self.width(), self.height()) / 600.0

    def resizeEvent(self, event):
        """Обработка изменения размера окна."""
        self.auto_scale_view()
        self.invalidate_cache()
        super().resizeEvent(event)

    def set_mirror(self, axis):
        """Установка зеркального отображения сцены по заданной оси."""
        if axis == 0:
            self.mirror_x = not self.mirror_x
        elif axis == 1:
            self.mirror_y = not self.mirror_y
        else:
            self.mirror_z = not self.mirror_z

        mirror_matrix = Matrix4x4.scaling(
            -1 if self.mirror_x else 1,
            -1 if self.mirror_y else 1,
            -1 if self.mirror_z else 1
        )
        self.object_transform = mirror_matrix
        self.invalidate_cache()
        self.update()


    def set_display_mode(self, mode):
        """Установка режима отображения (точки, каркас, заливка)."""
        self.display_mode = mode
        self.update()


    def rotate_letter(self, letter, axis, angle):
        """Поворот указанной буквы вокруг заданной оси на угол angle."""
        letter.rotate(axis, angle)
        self.invalidate_cache()
        self.update()

    def scale_letter(self, letter, scale_factor):
        """Изменение масштаба указанной буквы."""
        letter.set_scale(scale_factor)
        self.invalidate_cache()
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        """Инициализация главного окна приложения."""
        super().__init__()
        self.setWindowTitle("3D Буквы МС")
        self.setGeometry(100, 100, 1000, 800)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        self.scene = SceneWidget()
        layout.addWidget(self.scene, stretch=3)

        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        control_layout.setContentsMargins(5, 5, 5, 5)
        control_layout.setSpacing(10)

        control_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        self.create_letter_controls(control_layout, "Буква М:", 'm')
        self.create_rotation_controls(control_layout, "Вращение буквы М:", 'm')
        self.create_letter_controls(control_layout, "Буква С:", 'c')
        self.create_rotation_controls(control_layout, "Вращение буквы С:", 'c')
        self.create_transform_controls(control_layout, "Управление камерой:", self.rotate_camera, None)
        self.create_mirror_controls(control_layout)
        self.create_display_controls(control_layout)

        reset_btn = QPushButton("Сбросить вид")
        reset_btn.setMinimumHeight(40)
        reset_btn.clicked.connect(self.reset_view)
        control_layout.addWidget(reset_btn)
        control_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setWidget(control_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(350)
        scroll_area.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        layout.addWidget(scroll_area, stretch=1)

    def create_letter_controls(self, layout, title, prefix):
        """Создание элементов управления параметрами буквы (высота, ширина, глубина, масштаб)."""
        group = QGroupBox(title)
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(5)

        for param, text in [('height', 'Высота'), ('width', 'Ширина'), ('depth', 'Глубина')]:
            slider = QSlider(Qt.Horizontal)
            slider.setRange(10, 200)
            slider.setValue(getattr(self.scene, f"{prefix}_letter").__dict__[param])
            slider.valueChanged.connect(lambda v, p=param, pr=prefix: self.update_letter_param(pr, p, v))

            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)

            group_layout.addWidget(label)
            group_layout.addWidget(slider)

        scale_slider = QSlider(Qt.Horizontal)
        scale_slider.setRange(50, 200)
        scale_slider.setValue(100)
        scale_slider.valueChanged.connect(lambda v, pr=prefix: self.update_letter_scale(pr, v))

        scale_label = QLabel("Масштаб")
        scale_label.setAlignment(Qt.AlignCenter)

        group_layout.addWidget(scale_label)
        group_layout.addWidget(scale_slider)

        layout.addWidget(group)

    def create_rotation_controls(self, layout, title, letter_prefix):
        """Создание элементов управления вращением для указанной буквы."""
        group = QGroupBox(title)
        group_layout = QHBoxLayout(group)
        group_layout.setSpacing(5)

        for axis, text in [(0, "X"), (1, "Y"), (2, "Z")]:
            btn_layout = QVBoxLayout()
            btn_layout.setSpacing(5)

            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)
            btn_layout.addWidget(label)

            btn_plus = QPushButton("+")
            btn_plus.setMinimumSize(50, 30)
            btn_plus.clicked.connect(lambda _, a=axis, p=letter_prefix: self.rotate_letter(p, a, 10))
            btn_layout.addWidget(btn_plus)

            btn_minus = QPushButton("-")
            btn_minus.setMinimumSize(50, 30)
            btn_minus.clicked.connect(lambda _, a=axis, p=letter_prefix: self.rotate_letter(p, a, -10))
            btn_layout.addWidget(btn_minus)

            group_layout.addLayout(btn_layout)

        layout.addWidget(group)

    def create_transform_controls(self, layout, title, rotate_cb, scale_cb):
        """Создание элементов управления трансформацией (вращение, масштаб) для камеры."""
        group = QGroupBox(title)
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)

        if rotate_cb:
            rot_group = QWidget()
            rot_layout = QHBoxLayout(rot_group)
            rot_layout.setSpacing(5)

            for axis, text in [(0, "X"), (1, "Y"), (2, "Z")]:
                btn_layout = QVBoxLayout()
                btn_layout.setSpacing(5)

                label = QLabel(text)
                label.setAlignment(Qt.AlignCenter)
                btn_layout.addWidget(label)

                btn_plus = QPushButton("+")
                btn_plus.setMinimumSize(50, 30)
                btn_plus.clicked.connect(lambda _, a=axis: rotate_cb(a, 10))
                btn_layout.addWidget(btn_plus)

                btn_minus = QPushButton("-")
                btn_minus.setMinimumSize(50, 30)
                btn_minus.clicked.connect(lambda _, a=axis: rotate_cb(a, -10))
                btn_layout.addWidget(btn_minus)

                rot_layout.addLayout(btn_layout)

            group_layout.addWidget(rot_group)

        if scale_cb:
            scale_slider = QSlider(Qt.Horizontal)
            scale_slider.setRange(100, 400)
            scale_slider.setValue(100)
            scale_slider.valueChanged.connect(scale_cb)

            label = QLabel("Масштаб:")
            label.setAlignment(Qt.AlignCenter)

            group_layout.addWidget(label)
            group_layout.addWidget(scale_slider)

        layout.addWidget(group)

    def create_mirror_controls(self, layout):
        """Создание элементов управления зеркальным отображением."""
        group = QGroupBox("Зеркальное отображение")
        group_layout = QHBoxLayout(group)
        group_layout.setSpacing(10)

        for axis, text in [(0, "X"), (1, "Y")]:
            btn = QPushButton(f"Зеркало {text}")
            btn.setCheckable(True)
            btn.setMinimumSize(80, 30)
            btn.clicked.connect(lambda _, a=axis: self.scene.set_mirror(a))
            group_layout.addWidget(btn)

        layout.addWidget(group)


    def create_display_controls(self, layout):
        """Создание элементов управления режимом отображения."""
        group = QGroupBox("Режим отображения")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(5)

        for mode in DisplayMode:
            btn = QPushButton(mode.value)
            btn.setCheckable(True)
            btn.setMinimumHeight(30)
            btn.setChecked(mode == DisplayMode.FILLED)
            btn.clicked.connect(lambda _, m=mode: self.update_display(m))
            group_layout.addWidget(btn)

        layout.addWidget(group)


    def update_letter_param(self, prefix, param, value):
        """Обновление параметра буквы (высота, ширина, глубина)."""
        letter = getattr(self.scene, f"{prefix}_letter")
        setattr(letter, param, value)
        letter.update_geometry()
        self.scene.invalidate_cache()
        self.scene.update()

    def update_letter_scale(self, prefix, value):
        """Обновление масштаба буквы."""
        letter = getattr(self.scene, f"{prefix}_letter")
        scale_factor = value / 100.0
        self.scene.scale_letter(letter, scale_factor)

    def rotate_letter(self, letter_prefix, axis, angle):
        """Поворот указанной буквы вокруг заданной оси."""
        letter = getattr(self.scene, f"{letter_prefix}_letter")
        self.scene.rotate_letter(letter, axis, angle)

    def rotate_camera(self, axis, angle):
        """Поворот камеры вокруг заданной оси."""
        self.scene.camera_rot[axis] += angle
        self.scene.invalidate_cache()
        self.scene.update()


    def update_display(self, mode):
        """Обновление режима отображения сцены."""
        self.scene.set_display_mode(mode)
        for btn in self.findChildren(QPushButton):
            if btn.text() in [m.value for m in DisplayMode]:
                btn.setChecked(btn.text() == mode.value)


    def reset_view(self):
        """Сброс всех параметров сцены к начальным значениям."""
        self.scene.camera_pos = Vector3D(0, 0, -400)
        self.scene.camera_rot = [0, 0, 0]
        self.scene.m_letter.transform = Matrix4x4.rotation_x(180)
        self.scene.m_letter.scale = 1.0
        self.scene.c_letter.transform = Matrix4x4.rotation_x(180)
        self.scene.c_letter.scale = 1.0
        self.scene.object_transform = Matrix4x4()
        self.scene.base_scale = 2.0
        self.scene.mirror_x = False
        self.scene.mirror_y = False
        self.scene.mirror_z = False
        self.scene.set_display_mode(DisplayMode.FILLED)
        self.scene.invalidate_cache()
        self.scene.update()

        for btn in self.findChildren(QPushButton):
            if btn.text() in [m.value for m in DisplayMode]:
                btn.setChecked(btn.text() == DisplayMode.FILLED.value)
            elif btn.text().startswith("Зеркало"):
                btn.setChecked(False)

        for slider in self.findChildren(QSlider):
            parent_group = slider.parent().parent()
            if hasattr(parent_group, 'title') and parent_group.title() in ["Буква М:", "Буква С:"]:
                if slider.previousSibling().text() == "Масштаб":
                    slider.setValue(100)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())  # Использовано exec() для PySide6