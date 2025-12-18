import re
from enum import Enum
from typing import List, Optional, Dict, Any, Tuple
import sys
import os
import math


class TokenType(Enum):
    # Ключевые слова
    IF = "if"
    ELSE = "else"
    SWITCH = "switch"
    CASE = "case"
    DEFAULT = "default"
    FUNCTION = "function"
    RETURN = "return"
    PRINT = "print"  # Добавили print

    # Типы
    POINT = "point"
    LINE = "line"
    CIRCLE = "circle"
    POLYGON = "polygon"

    # Встроенные функции
    DISTANCE = "distance"
    INTERSECTION = "intersection"
    BELONGS = "belongs"

    # Операторы и разделители
    ASSIGN = "="
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    COMMA = ","
    COLON = ":"
    SEMICOLON = ";"

    # Идентификаторы и литералы
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"

    # Конец файла
    EOF = "EOF"


class Token:
    def __init__(self, type: TokenType, value: str = "", line: int = 0, column: int = 0):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        return f"Token({self.type}, '{self.value}', {self.line}:{self.column})"


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def tokenize(self) -> List[Token]:
        keywords = {
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'switch': TokenType.SWITCH,
            'case': TokenType.CASE,
            'default': TokenType.DEFAULT,
            'function': TokenType.FUNCTION,
            'return': TokenType.RETURN,
            'print': TokenType.PRINT,  # Добавили print
            'point': TokenType.POINT,
            'line': TokenType.LINE,
            'circle': TokenType.CIRCLE,
            'polygon': TokenType.POLYGON,
            'distance': TokenType.DISTANCE,
            'intersection': TokenType.INTERSECTION,
            'belongs': TokenType.BELONGS
        }

        while self.position < len(self.source):
            char = self.source[self.position]

            # Пропускаем пробельные символы
            if char.isspace():
                if char == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.position += 1
                continue

            # Пропускаем комментарии (# и //)
            if char == '#' or (
                    char == '/' and self.position + 1 < len(self.source) and self.source[self.position + 1] == '/'):
                while self.position < len(self.source) and self.source[self.position] != '\n':
                    self.position += 1
                    self.column += 1
                continue

            # Строковые литералы
            if char == '"':
                start = self.position
                self.position += 1
                self.column += 1
                while (self.position < len(self.source) and
                       self.source[self.position] != '"'):
                    if self.source[self.position] == '\n':
                        self.line += 1
                        self.column = 1
                    else:
                        self.column += 1
                    self.position += 1

                if self.position < len(self.source) and self.source[self.position] == '"':
                    string_literal = self.source[start + 1:self.position]
                    self.tokens.append(Token(TokenType.STRING, string_literal, self.line, self.column))
                    self.position += 1
                    self.column += 1
                else:
                    raise SyntaxError(f"Незакрытая строка в позиции {self.line}:{self.column}")
                continue

            # Числа
            if char.isdigit() or (
                    char == '.' and self.position + 1 < len(self.source) and self.source[self.position + 1].isdigit()):
                start = self.position
                has_dot = char == '.'
                while self.position < len(self.source):
                    next_char = self.source[self.position]
                    if next_char == '.':
                        if has_dot:
                            break
                        has_dot = True
                    elif not next_char.isdigit():
                        break
                    self.position += 1
                    self.column += 1

                number = self.source[start:self.position]
                self.tokens.append(Token(TokenType.NUMBER, number, self.line, self.column))
                continue

            # Идентификаторы и ключевые слова
            if char.isalpha() or char == '_':
                start = self.position
                while (self.position < len(self.source) and
                       (self.source[self.position].isalnum() or self.source[self.position] == '_')):
                    self.position += 1
                    self.column += 1
                identifier = self.source[start:self.position]

                if identifier in keywords:
                    self.tokens.append(Token(keywords[identifier], identifier, self.line, self.column))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, identifier, self.line, self.column))
                continue

            # Операторы и разделители
            operators = {
                '=': TokenType.ASSIGN,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                ',': TokenType.COMMA,
                ':': TokenType.COLON,
                ';': TokenType.SEMICOLON
            }

            if char in operators:
                self.tokens.append(Token(operators[char], char, self.line, self.column))
                self.position += 1
                self.column += 1
                continue

            # Неизвестный символ
            raise SyntaxError(f"Неизвестный символ '{char}' в позиции {self.line}:{self.column}")

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[0] if tokens else Token(TokenType.EOF)

    def error(self, message: str):
        raise SyntaxError(f"Синтаксическая ошибка в {self.current_token.line}:{self.current_token.column}: {message}")

    def eat(self, token_type: TokenType):
        if self.current_token.type == token_type:
            self.position += 1
            if self.position < len(self.tokens):
                self.current_token = self.tokens[self.position]
            else:
                self.current_token = Token(TokenType.EOF)
        else:
            self.error(f"Ожидался {token_type}, получен {self.current_token.type}")

    def parse(self) -> Dict[str, Any]:
        return self.program()

    def program(self) -> Dict[str, Any]:
        statements = []
        while self.current_token.type != TokenType.EOF:
            statements.append(self.statement())
        return {"type": "program", "statements": statements}

    def statement(self) -> Dict[str, Any]:
        if self.current_token.type == TokenType.IF:
            return self.if_statement()
        elif self.current_token.type == TokenType.SWITCH:
            return self.switch_statement()
        elif self.current_token.type == TokenType.FUNCTION:
            return self.function_declaration()
        elif self.current_token.type == TokenType.RETURN:
            return self.return_statement()
        elif self.current_token.type == TokenType.PRINT:
            return self.print_statement()
        elif self.current_token.type == TokenType.IDENTIFIER:
            # Присваивание или вызов функции
            lookahead = self.tokens[self.position + 1] if self.position + 1 < len(self.tokens) else None
            if lookahead and lookahead.type == TokenType.ASSIGN:
                return self.assignment()
            else:
                return self.expression_statement()
        else:
            return self.expression_statement()

    def assignment(self) -> Dict[str, Any]:
        identifier = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.ASSIGN)
        expr = self.expression()
        self.eat(TokenType.SEMICOLON)
        return {"type": "assignment", "identifier": identifier, "expression": expr}

    def print_statement(self) -> Dict[str, Any]:
        self.eat(TokenType.PRINT)
        self.eat(TokenType.LPAREN)
        expr = self.expression()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.SEMICOLON)
        return {"type": "print_statement", "expression": expr}

    def expression_statement(self) -> Dict[str, Any]:
        expr = self.expression()
        self.eat(TokenType.SEMICOLON)
        return {"type": "expression_statement", "expression": expr}

    def if_statement(self) -> Dict[str, Any]:
        self.eat(TokenType.IF)
        self.eat(TokenType.LPAREN)
        condition = self.expression()
        self.eat(TokenType.RPAREN)

        then_branch = self.block()

        else_branch = None
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            else_branch = self.block()

        return {"type": "if_statement", "condition": condition, "then_branch": then_branch, "else_branch": else_branch}

    def switch_statement(self) -> Dict[str, Any]:
        self.eat(TokenType.SWITCH)
        self.eat(TokenType.LPAREN)
        expression = self.expression()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)

        cases = []
        default_case = None

        while self.current_token.type in (TokenType.CASE, TokenType.DEFAULT):
            if self.current_token.type == TokenType.CASE:
                cases.append(self.case())
            else:
                default_case = self.default_case()

        self.eat(TokenType.RBRACE)
        return {"type": "switch_statement", "expression": expression, "cases": cases, "default": default_case}

    def case(self) -> Dict[str, Any]:
        self.eat(TokenType.CASE)
        value = self.expression()
        self.eat(TokenType.COLON)
        statements = []
        while (self.current_token.type not in (TokenType.CASE, TokenType.DEFAULT, TokenType.RBRACE) and
               self.current_token.type != TokenType.EOF):
            statements.append(self.statement())
        return {"type": "case", "value": value, "statements": statements}

    def default_case(self) -> Dict[str, Any]:
        self.eat(TokenType.DEFAULT)
        self.eat(TokenType.COLON)
        statements = []
        while (self.current_token.type not in (TokenType.CASE, TokenType.DEFAULT, TokenType.RBRACE) and
               self.current_token.type != TokenType.EOF):
            statements.append(self.statement())
        return {"type": "default_case", "statements": statements}

    def function_declaration(self) -> Dict[str, Any]:
        self.eat(TokenType.FUNCTION)
        name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.LPAREN)

        parameters = []
        if self.current_token.type == TokenType.IDENTIFIER:
            parameters.append(self.current_token.value)
            self.eat(TokenType.IDENTIFIER)
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                parameters.append(self.current_token.value)
                self.eat(TokenType.IDENTIFIER)

        self.eat(TokenType.RPAREN)
        body = self.block()

        return {"type": "function_declaration", "name": name, "parameters": parameters, "body": body}

    def return_statement(self) -> Dict[str, Any]:
        self.eat(TokenType.RETURN)
        expr = self.expression()
        self.eat(TokenType.SEMICOLON)
        return {"type": "return_statement", "expression": expr}

    def block(self) -> Dict[str, Any]:
        self.eat(TokenType.LBRACE)
        statements = []
        while self.current_token.type != TokenType.RBRACE and self.current_token.type != TokenType.EOF:
            statements.append(self.statement())
        self.eat(TokenType.RBRACE)
        return {"type": "block", "statements": statements}

    def expression(self) -> Dict[str, Any]:
        # Обрабатываем простые выражения: числа, строки, идентификаторы
        if self.current_token.type == TokenType.NUMBER:
            value = self.current_token.value
            self.eat(TokenType.NUMBER)
            return {"type": "number", "value": value}
        elif self.current_token.type == TokenType.STRING:
            value = self.current_token.value
            self.eat(TokenType.STRING)
            return {"type": "string", "value": value}
        elif self.current_token.type == TokenType.IDENTIFIER:
            # Это может быть переменная или вызов функции
            lookahead = self.tokens[self.position + 1] if self.position + 1 < len(self.tokens) else None
            if lookahead and lookahead.type == TokenType.LPAREN:
                return self.function_call()
            else:
                identifier = self.current_token.value
                self.eat(TokenType.IDENTIFIER)
                return {"type": "identifier", "value": identifier}
        else:
            # Встроенные функции
            return self.function_call()

    def function_call(self) -> Dict[str, Any]:
        if self.current_token.type in (TokenType.DISTANCE, TokenType.INTERSECTION, TokenType.BELONGS,
                                       TokenType.POINT, TokenType.LINE, TokenType.CIRCLE, TokenType.POLYGON):
            # Встроенные функции и конструкторы
            func_name = self.current_token.type.value
            self.eat(self.current_token.type)
        else:
            # Пользовательские функции
            func_name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)

        self.eat(TokenType.LPAREN)
        arguments = []

        if self.current_token.type != TokenType.RPAREN:
            arguments.append(self.expression())
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                arguments.append(self.expression())

        self.eat(TokenType.RPAREN)

        return {"type": "function_call", "function": func_name, "arguments": arguments}


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}
        self.functions = {}
        self.current_scope = "global"
        self.errors = []
        self.warnings = []

    def analyze(self, ast: Dict[str, Any]) -> Dict[str, Any]:
        self.errors.clear()
        self.warnings.clear()
        self.symbol_table.clear()
        self.functions.clear()

        # Добавляем встроенные функции
        self._add_builtin_functions()

        self._visit_program(ast)

        return {
            "success": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "symbol_table": self.symbol_table.copy(),
            "functions": self.functions.copy()
        }

    def _add_builtin_functions(self):
        # Встроенные функции
        self.functions["distance"] = {
            "parameters": ["point", "point"],
            "return_type": "number",
            "scope": "global"
        }
        self.functions["intersection"] = {
            "parameters": ["line", "line"],
            "return_type": "point",
            "scope": "global"
        }
        self.functions["belongs"] = {
            "parameters": ["point", "any_geometry"],
            "return_type": "boolean",
            "scope": "global"
        }

        # Конструкторы
        self.functions["point"] = {
            "parameters": ["number", "number"],
            "return_type": "point",
            "scope": "global"
        }
        self.functions["line"] = {
            "parameters": ["point", "point"],
            "return_type": "line",
            "scope": "global"
        }
        self.functions["circle"] = {
            "parameters": ["point", "number"],
            "return_type": "circle",
            "scope": "global"
        }
        self.functions["polygon"] = {
            "parameters": ["point", "point", "point"],  # минимум 3 точки
            "return_type": "polygon",
            "scope": "global",
            "min_args": 3
        }

        # Функция вывода
        self.functions["print"] = {
            "parameters": ["any"],
            "return_type": "void",
            "scope": "global"
        }

    def _error(self, message: str, line: int = 0, column: int = 0):
        self.errors.append(f"Семантическая ошибка ({line}:{column}): {message}")

    def _warning(self, message: str, line: int = 0, column: int = 0):
        self.warnings.append(f"Предупреждение ({line}:{column}): {message}")

    def _visit_program(self, node: Dict[str, Any]):
        for statement in node["statements"]:
            self._visit_statement(statement)

    def _visit_statement(self, node: Dict[str, Any]):
        node_type = node["type"]

        if node_type == "assignment":
            self._visit_assignment(node)
        elif node_type == "expression_statement":
            self._visit_expression(node["expression"])
        elif node_type == "print_statement":
            self._visit_print_statement(node)
        elif node_type == "if_statement":
            self._visit_if_statement(node)
        elif node_type == "switch_statement":
            self._visit_switch_statement(node)
        elif node_type == "function_declaration":
            self._visit_function_declaration(node)
        elif node_type == "return_statement":
            self._visit_return_statement(node)
        elif node_type == "block":
            self._visit_block(node)
        else:
            self._error(f"Неизвестный тип оператора: {node_type}")

    def _visit_assignment(self, node: Dict[str, Any]):
        identifier = node["identifier"]
        expr_type = self._visit_expression(node["expression"])

        if expr_type == "error":
            return

        # Проверяем, не объявлена ли уже переменная
        if identifier in self.symbol_table:
            existing_type = self.symbol_table[identifier]["type"]
            if existing_type != expr_type:
                self._warning(f"Переменная '{identifier}' изменяет тип с {existing_type} на {expr_type}")
        else:
            # Неявное объявление переменной
            self.symbol_table[identifier] = {
                "type": expr_type,
                "scope": self.current_scope
            }

    def _visit_print_statement(self, node: Dict[str, Any]):
        # Для print проверяем, что аргумент существует
        self._visit_expression(node["expression"])

    def _visit_expression(self, node: Dict[str, Any]) -> str:
        node_type = node["type"]

        if node_type == "function_call":
            return self._visit_function_call(node)
        elif node_type == "identifier":
            identifier = node["value"]
            if identifier in self.symbol_table:
                return self.symbol_table[identifier]["type"]
            else:
                self._error(f"Необъявленная переменная: {identifier}")
                return "error"
        elif node_type == "number":
            return "number"
        elif node_type == "string":
            return "string"
        else:
            self._error(f"Неизвестный тип выражения: {node_type}")
            return "error"

    def _visit_function_call(self, node: Dict[str, Any]) -> str:
        func_name = node["function"]
        arguments = node["arguments"]

        # Проверяем, существует ли функция
        if func_name not in self.functions:
            self._error(f"Необъявленная функция: {func_name}")
            return "error"

        func_info = self.functions[func_name]
        expected_params = func_info["parameters"]

        # Для функции print разрешаем любой тип
        if func_name == "print":
            # Проверяем каждый аргумент
            for arg in arguments:
                self._visit_expression(arg)
            return "void"

        # Проверка количества аргументов
        if "min_args" in func_info:
            if len(arguments) < func_info["min_args"]:
                self._error(
                    f"Функция {func_name} требует минимум {func_info['min_args']} аргументов, получено {len(arguments)}")
                return "error"
        elif len(arguments) != len(expected_params):
            self._error(f"Функция {func_name} ожидает {len(expected_params)} аргументов, получено {len(arguments)}")
            return "error"

        # Проверка типов аргументов
        for i, (arg, expected_type) in enumerate(zip(arguments, expected_params)):
            arg_type = self._visit_expression(arg)
            if arg_type == "error":
                continue

            # Если тип аргумента unknown (параметр функции), пропускаем проверку
            if arg_type == "unknown":
                continue

            if expected_type == "any_geometry":
                # Проверяем, что аргумент - геометрическая фигура
                if arg_type not in ["point", "line", "circle", "polygon"]:
                    self._error(
                        f"Аргумент {i + 1} функции {func_name} должен быть геометрической фигурой, получен {arg_type}")
            elif expected_type == "any":
                # Для функций типа print - принимаем любой тип
                continue
            elif arg_type != expected_type and expected_type != "unknown":
                self._error(
                    f"Аргумент {i + 1} функции {func_name} должен быть типа {expected_type}, получен {arg_type}")

        return func_info["return_type"]

    def _visit_if_statement(self, node: Dict[str, Any]):
        condition_type = self._visit_expression(node["condition"])

        # Для условий if разрешаем любые типы (неявное преобразование)
        if condition_type == "error":
            return

        self._visit_block(node["then_branch"])
        if node["else_branch"]:
            self._visit_block(node["else_branch"])

    def _visit_switch_statement(self, node: Dict[str, Any]):
        expr_type = self._visit_expression(node["expression"])

        if expr_type == "error":
            return

        for case in node["cases"]:
            case_type = self._visit_expression(case["value"])
            if case_type != expr_type and case_type != "error" and case_type != "unknown":
                self._error(f"Тип case ({case_type}) не совпадает с типом switch выражения ({expr_type})")

            for statement in case["statements"]:
                self._visit_statement(statement)

        if node["default"]:
            for statement in node["default"]["statements"]:
                self._visit_statement(statement)

    def _visit_function_declaration(self, node: Dict[str, Any]):
        func_name = node["name"]

        if func_name in self.functions:
            self._error(f"Функция {func_name} уже объявлена")
            return

        # Сохраняем текущую область видимости
        old_scope = self.current_scope
        self.current_scope = func_name

        # Добавляем функцию в таблицу функций
        self.functions[func_name] = {
            "parameters": ["unknown"] * len(node["parameters"]),
            "return_type": "unknown",
            "scope": old_scope
        }

        # Добавляем параметры в таблицу символов
        for param in node["parameters"]:
            self.symbol_table[param] = {
                "type": "unknown",
                "scope": self.current_scope
            }

        # Анализируем тело функции
        return_type = self._visit_block(node["body"])

        # Обновляем информацию о функции
        self.functions[func_name]["return_type"] = return_type or "void"

        # Восстанавливаем область видимости
        self.current_scope = old_scope

    def _visit_return_statement(self, node: Dict[str, Any]) -> str:
        if "expression" in node:
            return self._visit_expression(node["expression"])
        return "void"

    def _visit_block(self, node: Dict[str, Any]) -> str:
        return_type = "void"

        for statement in node["statements"]:
            if statement["type"] == "return_statement":
                return_type = self._visit_return_statement(statement)
            else:
                self._visit_statement(statement)

        return return_type


class CodeGenerator:
    """Генератор кода на Python"""

    def __init__(self):
        self.code = []
        self.indent_level = 0
        self.temp_counter = 0
        self.builtin_functions = {
            'point': 'Point',
            'line': 'Line',
            'circle': 'Circle',
            'polygon': 'Polygon',
            'distance': 'distance',
            'intersection': 'intersection',
            'belongs': 'belongs',
            'print': 'print'  # Добавили print
        }

    def generate(self, ast: Dict[str, Any]) -> str:
        """Генерирует код на Python из AST"""
        self.code = []

        # Добавляем заголовок с импортами
        self._add_header()

        # Генерируем код программы
        self._generate_program(ast)

        # Добавляем вызов main, если она есть
        self._add_main_call()

        return '\n'.join(self.code)

    def _add_header(self):
        """Добавляет заголовок с импортами и определением классов"""
        header = '''# Сгенерированный код из геометрического языка
import math

# Определение геометрических классов
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"Point({self.x}, {self.y})"

    def __repr__(self):
        return self.__str__()


class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __str__(self):
        return f"Line({self.p1}, {self.p2})"


class Circle:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def __str__(self):
        return f"Circle({self.center}, {self.radius})"


class Polygon:
    def __init__(self, *points):
        self.points = points

    def __str__(self):
        return f"Polygon({len(self.points)} points)"


# Встроенные геометрические функции
def distance(p1, p2):
    """Расстояние между двумя точками"""
    if isinstance(p1, Point) and isinstance(p2, Point):
        return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
    return 0.0


def intersection(l1, l2):
    """Точка пересечения двух линий"""
    if isinstance(l1, Line) and isinstance(l2, Line):
        # Упрощенная реализация
        x1, y1 = l1.p1.x, l1.p1.y
        x2, y2 = l1.p2.x, l1.p2.y
        x3, y3 = l2.p1.x, l2.p1.y
        x4, y4 = l2.p2.x, l2.p2.y

        denom = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
        if denom == 0:
            return None

        x = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / denom
        y = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / denom

        return Point(x, y)
    return None


def belongs(point, geometry):
    """Проверяет, принадлежит ли точка геометрической фигуре"""
    if not isinstance(point, Point):
        return False

    if isinstance(geometry, Point):
        return point.x == geometry.x and point.y == geometry.y
    elif isinstance(geometry, Line):
        # Упрощенная проверка для линии
        return True
    elif isinstance(geometry, Circle):
        dx = point.x - geometry.center.x
        dy = point.y - geometry.center.y
        return dx*dx + dy*dy <= geometry.radius*geometry.radius
    elif isinstance(geometry, Polygon):
        # Упрощенная проверка для многоугольника
        return True

    return False

'''
        self.code.append(header)

    def _add_main_call(self):
        """Добавляет вызов функции main, если она есть"""
        self.code.append("\n# Запуск программы")
        self.code.append("if __name__ == \"__main__\":")
        self.code.append("    # Поиск функции main")
        self.code.append("    if 'main' in globals() and callable(main):")
        self.code.append("        main()")
        self.code.append("    else:")
        self.code.append("        print(\"Функция main не найдена\")")

    def _add_line(self, line: str):
        """Добавляет строку кода с учетом отступа"""
        indent = "    " * self.indent_level
        self.code.append(indent + line)

    def _generate_program(self, node: Dict[str, Any]):
        """Генерирует код для всей программы"""
        for statement in node["statements"]:
            self._generate_statement(statement)

    def _generate_statement(self, node: Dict[str, Any]):
        """Генерирует код для оператора"""
        node_type = node["type"]

        if node_type == "assignment":
            self._generate_assignment(node)
        elif node_type == "expression_statement":
            self._generate_expression_statement(node)
        elif node_type == "print_statement":
            self._generate_print_statement(node)
        elif node_type == "if_statement":
            self._generate_if_statement(node)
        elif node_type == "switch_statement":
            self._generate_switch_statement(node)
        elif node_type == "function_declaration":
            self._generate_function_declaration(node)
        elif node_type == "return_statement":
            self._generate_return_statement(node)
        elif node_type == "block":
            self._generate_block(node)
        else:
            raise ValueError(f"Неизвестный тип оператора: {node_type}")

    def _generate_assignment(self, node: Dict[str, Any]):
        """Генерирует код для присваивания"""
        identifier = node["identifier"]
        expr_code = self._generate_expression(node["expression"])
        self._add_line(f"{identifier} = {expr_code}")

    def _generate_print_statement(self, node: Dict[str, Any]):
        """Генерирует код для оператора print"""
        expr_code = self._generate_expression(node["expression"])
        self._add_line(f"print({expr_code})")

    def _generate_expression_statement(self, node: Dict[str, Any]):
        """Генерирует код для выражения-оператора"""
        expr_code = self._generate_expression(node["expression"])
        self._add_line(expr_code)

    def _generate_if_statement(self, node: Dict[str, Any]):
        """Генерирует код для условного оператора"""
        condition = self._generate_expression(node["condition"])
        self._add_line(f"if {condition}:")

        self.indent_level += 1
        self._generate_block(node["then_branch"])
        self.indent_level -= 1

        if node["else_branch"]:
            self._add_line("else:")
            self.indent_level += 1
            self._generate_block(node["else_branch"])
            self.indent_level -= 1

    def _generate_switch_statement(self, node: Dict[str, Any]):
        """Генерирует код для оператора switch (преобразуется в if-elif-else)"""
        expr = self._generate_expression(node["expression"])
        temp_var = self._new_temp()

        self._add_line(f"{temp_var} = {expr}")

        first_case = True
        for case in node["cases"]:
            case_value = self._generate_expression(case["value"])

            if first_case:
                self._add_line(f"if {temp_var} == {case_value}:")
                first_case = False
            else:
                self._add_line(f"elif {temp_var} == {case_value}:")

            self.indent_level += 1
            for statement in case["statements"]:
                self._generate_statement(statement)
            self.indent_level -= 1

        if node["default"]:
            self._add_line("else:")
            self.indent_level += 1
            for statement in node["default"]["statements"]:
                self._generate_statement(statement)
            self.indent_level -= 1

    def _generate_function_declaration(self, node: Dict[str, Any]):
        """Генерирует код для объявления функции"""
        name = node["name"]
        params = ", ".join(node["parameters"])

        self._add_line("")
        self._add_line(f"def {name}({params}):")

        self.indent_level += 1
        self._generate_block(node["body"])
        self.indent_level -= 1
        self._add_line("")

    def _generate_return_statement(self, node: Dict[str, Any]):
        """Генерирует код для оператора return"""
        if "expression" in node:
            expr = self._generate_expression(node["expression"])
            self._add_line(f"return {expr}")
        else:
            self._add_line("return")

    def _generate_block(self, node: Dict[str, Any]):
        """Генерирует код для блока"""
        for statement in node["statements"]:
            self._generate_statement(statement)

    def _generate_expression(self, node: Dict[str, Any]) -> str:
        """Генерирует код для выражения и возвращает строку"""
        node_type = node["type"]

        if node_type == "number":
            return node["value"]
        elif node_type == "string":
            return f'"{node["value"]}"'
        elif node_type == "identifier":
            return node["value"]
        elif node_type == "function_call":
            return self._generate_function_call(node)
        else:
            raise ValueError(f"Неизвестный тип выражения: {node_type}")

    def _generate_function_call(self, node: Dict[str, Any]) -> str:
        """Генерирует код для вызова функции"""
        func_name = node["function"]
        arguments = node["arguments"]

        # Преобразуем имя функции для Python
        if func_name in self.builtin_functions:
            func_name = self.builtin_functions[func_name]

        # Генерируем аргументы
        arg_codes = []
        for arg in arguments:
            arg_codes.append(self._generate_expression(arg))

        args_str = ", ".join(arg_codes)
        return f"{func_name}({args_str})"

    def _new_temp(self) -> str:
        """Создает новую временную переменную"""
        self.temp_counter += 1
        return f"__temp_{self.temp_counter}"


class Compiler:
    """Полноценный компилятор геометрического языка"""

    def __init__(self, target_language="python"):
        self.target_language = target_language
        self.errors = []
        self.warnings = []

    def compile(self, source_code: str, output_file: str = None) -> Dict[str, Any]:
        """Компилирует исходный код"""
        self.errors = []
        self.warnings = []

        print("\n" + "=" * 80)
        print("КОМПИЛЯЦИЯ ГЕОМЕТРИЧЕСКОГО ЯЗЫКА")
        print("=" * 80)

        # Шаг 1: Лексический анализ
        print("\n1. ЛЕКСИЧЕСКИЙ АНАЛИЗ:")
        print("-" * 30)
        try:
            lexer = Lexer(source_code)
            tokens = lexer.tokenize()
            print(f"✓ Найдено {len(tokens)} токенов")
        except SyntaxError as e:
            self.errors.append(f"Лексическая ошибка: {str(e)}")
            return self._compile_result(False, None)

        # Шаг 2: Синтаксический анализ
        print("\n2. СИНТАКСИЧЕСКИЙ АНАЛИЗ:")
        print("-" * 30)
        try:
            parser = Parser(tokens)
            ast = parser.parse()
            print("✓ AST успешно построен")
        except SyntaxError as e:
            self.errors.append(f"Синтаксическая ошибка: {str(e)}")
            return self._compile_result(False, None)

        # Шаг 3: Семантический анализ
        print("\n3. СЕМАНТИЧЕСКИЙ АНАЛИЗ:")
        print("-" * 30)
        semantic_analyzer = SemanticAnalyzer()
        semantic_result = semantic_analyzer.analyze(ast)

        if not semantic_result["success"]:
            self.errors.extend(semantic_result["errors"])
            self.warnings.extend(semantic_result["warnings"])

            print("✗ Семантические ошибки:")
            for error in semantic_result["errors"]:
                print(f"  {error}")

            return self._compile_result(False, None)

        print("✓ Семантический анализ пройден")
        self.warnings.extend(semantic_result["warnings"])

        if semantic_result["warnings"]:
            print("⚠ Предупреждения:")
            for warning in semantic_result["warnings"]:
                print(f"  {warning}")

        # Шаг 4: Генерация кода
        print(f"\n4. ГЕНЕРАЦИЯ КОДА ({self.target_language.upper()}):")
        print("-" * 30)

        try:
            code_generator = CodeGenerator()
            generated_code = code_generator.generate(ast)
            print("✓ Код успешно сгенерирован")
        except Exception as e:
            self.errors.append(f"Ошибка генерации кода: {str(e)}")
            return self._compile_result(False, None)

        # Шаг 5: Сохранение результата
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(generated_code)
                print(f"✓ Код сохранен в файл: {output_file}")
            except Exception as e:
                self.errors.append(f"Ошибка сохранения файла: {str(e)}")

        print("\n" + "=" * 80)
        print("КОМПИЛЯЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 80)

        return self._compile_result(True, generated_code)

    def _compile_result(self, success: bool, code: str = None) -> Dict[str, Any]:
        """Формирует результат компиляции"""
        return {
            "success": success,
            "code": code,
            "errors": self.errors,
            "warnings": self.warnings
        }

    def compile_file(self, input_file: str, output_file: str = None) -> Dict[str, Any]:
        """Компилирует код из файла"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                source_code = f.read()

            if not output_file:
                output_file = os.path.splitext(input_file)[0] + '.py'

            return self.compile(source_code, output_file)
        except Exception as e:
            self.errors.append(f"Ошибка чтения файла: {str(e)}")
            return self._compile_result(False, None)


def run_compiler_demo():
    """Запускает демонстрацию работы компилятора"""

    compiler = Compiler()

    # Пример 1: Простая геометрическая программа
    print("\n\nПРИМЕР 1: Простая геометрическая программа")
    print("=" * 80)

    simple_geometry = """
function calculateDistance() {
    p1 = point(1, 2);
    p2 = point(4, 6);
    d = distance(p1, p2);
    return d;
}

function main() {
    result = calculateDistance();
    print(result);
}
"""

    result = compiler.compile(simple_geometry, "output1.py")

    if result["success"]:
        print("\nСгенерированный код (первые 20 строк):")
        print("-" * 40)
        lines = result["code"].split('\n')
        for i, line in enumerate(lines[:20]):
            print(f"{i + 1:3}: {line}")
        if len(lines) > 20:
            print("...")

    # Пример 2: Программа с условиями
    print("\n\nПРИМЕР 2: Программа с условиями и switch")
    print("=" * 80)

    conditional_program = """
function classifyPoint(x, y) {
    p = point(x, y);

    if (x > 0 && y > 0) {
        quadrant = 1;
    } else if (x < 0 && y > 0) {
        quadrant = 2;
    } else if (x < 0 && y < 0) {
        quadrant = 3;
    } else if (x > 0 && y < 0) {
        quadrant = 4;
    } else {
        quadrant = 0;
    }

    switch (quadrant) {
        case 1: name = "Первый квадрант";
        case 2: name = "Второй квадрант";
        case 3: name = "Третий квадрант";
        case 4: name = "Четвертый квадрант";
        default: name = "На оси";
    }

    return name;
}

function main() {
    print(classifyPoint(3, 4));
    print(classifyPoint(-2, 5));
    print(classifyPoint(0, 0));
}
"""

    result = compiler.compile(conditional_program, "output2.py")

    # Пример 3: Комплексная геометрическая программа
    print("\n\nПРИМЕР 3: Комплексная геометрическая программа")
    print("=" * 80)

    complex_geometry = """
function createGeometry() {
    // Создаем точки
    p1 = point(0, 0);
    p2 = point(3, 0);
    p3 = point(0, 4);

    // Создаем линии
    l1 = line(p1, p2);
    l2 = line(p2, p3);
    l3 = line(p3, p1);

    // Создаем окружность
    center = point(1.5, 1.5);
    c1 = circle(center, 2.5);

    // Создаем треугольник
    triangle = polygon(p1, p2, p3);

    return triangle;
}

function checkRelations() {
    p = point(1, 1);
    c = circle(point(0, 0), 3);

    if (belongs(p, c)) {
        result = "Точка внутри окружности";
    } else {
        result = "Точка вне окружности";
    }

    return result;
}

function main() {
    geom = createGeometry();
    status = checkRelations();

    print("Геометрия создана:", geom);
    print("Статус:", status);

    // Вычисляем расстояния
    p1 = point(0, 0);
    p2 = point(3, 4);
    dist = distance(p1, p2);
    print("Расстояние:", dist);
}
"""

    result = compiler.compile(complex_geometry, "output3.py")

    if result["success"]:
        print("\nГотовые файлы для запуска:")
        print("1. output1.py - Простая геометрическая программа")
        print("2. output2.py - Программа с условиями")
        print("3. output3.py - Комплексная геометрическая программа")

        print("\nДля запуска выполните:")
        print("  python output1.py")
        print("  python output2.py")
        print("  python output3.py")


def interactive_compiler():
    """Интерактивный режим компилятора"""

    compiler = Compiler()

    print("\n" + "=" * 80)
    print("ИНТЕРАКТИВНЫЙ КОМПИЛЯТОР ГЕОМЕТРИЧЕСКОГО ЯЗЫКА")
    print("=" * 80)
    print("Поддерживаемые команды:")
    print("  compile <файл> - Компилировать файл")
    print("  run <файл>     - Запустить скомпилированный код")
    print("  demo           - Запустить демонстрацию")
    print("  exit           - Выход")
    print("=" * 80)

    while True:
        try:
            command = input("\n>>> ").strip()

            if not command:
                continue

            if command == "exit":
                print("Выход из компилятора...")
                break

            elif command == "demo":
                run_compiler_demo()

            elif command.startswith("compile "):
                filename = command[8:].strip()
                if not filename:
                    print("Укажите имя файла")
                    continue

                if not os.path.exists(filename):
                    print(f"Файл {filename} не найден")
                    continue

                result = compiler.compile_file(filename)

                if result["success"]:
                    output_file = os.path.splitext(filename)[0] + '.py'
                    print(f"✓ Файл успешно скомпилирован: {output_file}")
                else:
                    print("✗ Ошибки компиляции:")
                    for error in result["errors"]:
                        print(f"  {error}")

            elif command.startswith("run "):
                filename = command[4:].strip()
                if not filename:
                    print("Укажите имя файла")
                    continue

                if not filename.endswith('.py'):
                    filename += '.py'

                if not os.path.exists(filename):
                    print(f"Файл {filename} не найден")
                    continue

                print(f"Запуск {filename}...")
                os.system(f"python {filename}")

            else:
                print("Неизвестная команда. Доступные команды: compile, run, demo, exit")

        except KeyboardInterrupt:
            print("\nВыход из компилятора...")
            break
        except Exception as e:
            print(f"Ошибка: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Режим командной строки
        compiler = Compiler()

        if sys.argv[1] == "--compile" and len(sys.argv) > 2:
            input_file = sys.argv[2]
            output_file = sys.argv[3] if len(sys.argv) > 3 else None

            result = compiler.compile_file(input_file, output_file)

            if result["success"]:
                print("Компиляция успешно завершена")
                sys.exit(0)
            else:
                print("Ошибки компиляции:")
                for error in result["errors"]:
                    print(f"  {error}")
                sys.exit(1)

        elif sys.argv[1] == "--interactive":
            interactive_compiler()

        elif sys.argv[1] == "--demo":
            run_compiler_demo()

        else:
            print("Использование:")
            print("  python compiler.py --compile <входной_файл> [выходной_файл]")
            print("  python compiler.py --interactive")
            print("  python compiler.py --demo")
            sys.exit(1)

    else:
        # Запуск демонстрации по умолчанию
        run_compiler_demo()