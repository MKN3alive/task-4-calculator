import operator
import math

class Calculator:
    
    #приоритеты операций
    _precedence = {
        "=": 0,
        "+": 1, "-": 1,
        "*": 2, "/": 2,
        "^": 3,
        "u-": 4,
    }
    
    #операции 
    _operations = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "^": operator.pow,
    }

    #спец значения
    _special_values = ["inf", "+inf", "-inf", "nan"]
    
    def __init__(self):
        self.previous_result = 0
        self.variables = {"_": 0}
        
    @staticmethod
    def _is_number(token: str) -> bool:
        """Проверяет, является ли токен числом"""
        
        if token in __class__._special_values:
            return True
        try:
            float(token)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def _parse_number(token: str) -> float:
        """Переводит токен в число"""
        
        try:
            return float(token)
        except ValueError:
            return float("nan")
    
    @staticmethod
    def _tokenize(expression: str) -> list[str]:
        """Разбивает выражение на токены"""
        tokens = []
        i = 0
        n = len(expression)
        
        while i < n:
            char = expression[i]
            
            if char.isspace():
                i += 1
                continue
                
            if char.isdigit() or char == '.':
                j = i
                while j < n and (expression[j].isdigit() or expression[j] == '.'):
                    j += 1
                tokens.append(expression[i:j])
                i = j
                continue
                
            if char in ('i', 'n', '+', '-'):
                if expression[i:i+3] == 'inf':
                    tokens.append('inf')
                    i += 3
                    continue
                elif expression[i:i+4] == '+inf':
                    tokens.append('+inf')
                    i += 4
                    continue
                elif expression[i:i+4] == '-inf':
                    tokens.append('-inf')
                    i += 4
                    continue
                elif expression[i:i+3] == 'nan':
                    tokens.append('nan')
                    i += 3
                    continue
            
            if char in '+-*/^()_':
                if char == '-':
                    if not tokens or tokens[-1] in '+-*/^(':
                        tokens.append('u-')
                    else:
                        tokens.append(char)
                else:
                    tokens.append(char)
                i += 1
                continue
                
            i += 1
            
        return tokens
    
    @staticmethod
    @staticmethod
    def _infix_to_rpn(tokens: list[str]) -> list[str]:
        """Преобразует инфиксное выражение в обратную польскую запись"""
        output = []
        stack = []
        
        for token in tokens:
            if __class__._is_number(token) or token == '_':
                output.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if not stack:
                    raise ValueError("Лишняя закрывающая скобка")
                stack.pop()  
            else:
                while (stack and stack[-1] != '(' and
                    __class__._precedence.get(stack[-1], 0) >= __class__._precedence.get(token, 0)):
                    output.append(stack.pop())
                stack.append(token)
        
        for token in stack:
            if token == '(':
                raise ValueError("Не хватает закрывающей скобки")
        
        while stack:
            output.append(stack.pop())
        
        return output

            
    def _evaluate_rpn(self, rpn_tokens: list[str]) -> float:
        """Вычисляет значение выражения в RPN"""
        
        stack = []
        
        for token in rpn_tokens:
            if self._is_number(token):
                stack.append(self._parse_number(token))
            elif token == '_':
                stack.append(self.previous_result)
            elif token == 'u-':
                if not stack:
                    raise ValueError("Недостаточно операндов для унарного минуса")
                operand = stack.pop()
                if math.isinf(operand):
                    stack.append(-operand)
                elif math.isnan(operand):
                    stack.append(float('nan'))
                else:
                    stack.append(-operand)
            else:
                if len(stack) < 2:
                    raise ValueError("Недостаточно операндов для операции")
                b = stack.pop()
                a = stack.pop()
                
                try:
                    if token == '/' and b == 0:
                        if a == 0:
                            result = float('nan')
                        elif math.isinf(a):
                            result = float('nan') if math.isinf(b) else float('inf') if a > 0 else float('-inf')
                        else:
                            result = float('inf') if a > 0 else float('-inf')
                    elif token == '^':
                        if a == 0 and b == 0:
                            result = float('nan')
                        elif math.isinf(a) or math.isinf(b):
                            result = self._handle_power_special_cases(a, b)
                        else:
                            result = self._operations[token](a, b)
                    else:
                        result = self._operations[token](a, b)
                        
                    if not math.isinf(result) and not math.isnan(result):
                        if abs(result) > 1e308:
                            result = float('inf') if result > 0 else float('-inf')
                            
                except Exception as e:
                    raise ValueError(f"Ошибка при выполнении операции {token}: {str(e)}")
                
                stack.append(result)
        
        if len(stack) != 1:
            raise ValueError("Некорректное выражение")
            
        return stack[0]
    
    @staticmethod
    def _handle_power_special_cases(a: str, b: str) -> float:
        """Обрабатывает особые случаи для операции возведения в степень"""
        
        if math.isinf(a):
            if a > 0:
                if b > 0:
                    return float('inf')
                elif b < 0:
                    return 0.0
                else:  
                    return 1.0
            else: 
                if b > 0:
                    if b % 2 == 0:
                        return float('inf')
                    else:
                        return float('-inf')
                elif b < 0:
                    if b % 2 == 0:
                        return 0.0
                    else:
                        return -0.0
                else:
                    return 1.0
        elif math.isinf(b):
            if abs(a) > 1:
                if b > 0:
                    return float('inf')
                else:
                    return 0.0
            elif abs(a) == 1:
                return 1.0
            else:  
                if b > 0:
                    return 0.0
                else:
                    return float('inf')
        return float('nan')
    
    def calculate(self, expression: str) -> float:
        """Основной метод для вычисления выражения"""
        
        if not expression.strip():
            return self.previous_result
            
        try:
            expression = expression.replace('_', str(self.previous_result))
            
            tokens = self._tokenize(expression)
            rpn_tokens = self._infix_to_rpn(tokens)
            result = self._evaluate_rpn(rpn_tokens)
            
            self.previous_result = result
            self.variables['_'] = result
            
            return result
            
        except Exception as e:
            raise ValueError(f"Ошибка вычисления: {str(e)}")
        
    @staticmethod
    def format_result(result: float) -> str:
        """Форматирует результат для вывода"""
        
        if math.isnan(result):
            return "nan"
        
        elif math.isinf(result):
            return "inf" if result > 0 else "-inf"
        
        else:
            formatted = f"{result:.10g}"
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.')
            return formatted

if __name__ == "__main__":
    
    calculator = Calculator()
    
    print("<<Калькулятор>>\n\nПоддерживаемые операции: +, -, *, /, ^, _ (предыдущий результат)")
    print("Введите 'quit' для выхода")
    
    while True:
        try:
            expression = input("> ").strip()
            
            if expression.lower() in ('quit', 'exit', 'q'):
                break
                
            if not expression:
                continue
                
            result = calculator.calculate(expression)
            print(calculator.format_result(result))
            
        except KeyboardInterrupt:
            print("\nВыход из калькулятора")
            break
        
        except Exception as e:
            print(f"Ошибка: {e}")
