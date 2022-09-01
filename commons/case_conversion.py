def pascal_to_snake(s: str):
    snake = []
    for i, c in enumerate(s):
        if c.isupper():
            c = c.lower()
            if i > 0:
                c = '_' + c
        snake.append(c)
    return ''.join(snake)


def snake_to_pascal(s: str):
    pascal = []
    for i, c in enumerate(s):
        if c == '_':
            continue
        if i == 0 or s[i - 1] == '_':
            c = c.upper()
        pascal.append(c)
    return ''.join(pascal)
