
from django.core.exceptions import ValidationError

class ComplexityValidator:
    def __init__(self, min_uppercase=1, min_lowercase=1, min_digits=1, min_special=1):
        self.min_uppercase = min_uppercase
        self.min_lowercase = min_lowercase
        self.min_digits = min_digits
        self.min_special = min_special

    def validate(self, password, user=None):
        uppercase_count = sum(1 for c in password if c.isupper())
        lowercase_count = sum(1 for c in password if c.islower())
        digit_count = sum(1 for c in password if c.isdigit())
        # Считаем спецсимволы (все, что не буквы и не цифры)
        special_count = sum(1 for c in password if not c.isalnum())

        errors = []
        if uppercase_count < self.min_uppercase:
            errors.append(f"Пароль должен содержать минимум {self.min_uppercase} заглавную букву.")
        if lowercase_count < self.min_lowercase:
            errors.append(f"Пароль должен содержать минимум {self.min_lowercase} строчную букву.")
        if digit_count < self.min_digits:
            errors.append(f"Пароль должен содержать минимум {self.min_digits} цифру.")
        if special_count < self.min_special:
            errors.append(f"Пароль должен содержать минимум {self.min_special} специальный символ (!@#\$% и т.д.).")

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return "Пароль должен содержать заглавные и строчные буквы, цифры и специальные символы."