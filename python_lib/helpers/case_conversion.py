def pascal_to_snake(s: str):
    snake = []
    for i, c in enumerate(s):
        if c.isupper():
            c = c.lower()
            if i > 0:
                c = '_' + c
        snake.append(c)
    return ''.join(snake)
