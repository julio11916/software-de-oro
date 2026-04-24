import re

text = open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8').read()
lines = text.split('\n')
target_text = '\n'.join(lines[411:695])

def parse(snippet):
    i = 0
    length = len(snippet)
    brace_count = 0
    in_single_quote = False
    in_double_quote = False
    in_backtick = False
    in_line_comment = False
    in_block_comment = False
    line = 412

    while i < length:
        char = snippet[i]
        
        if char == '\n':
            line += 1
            if in_line_comment:
                in_line_comment = False
            i += 1
            continue
            
        if in_line_comment or in_block_comment:
            if in_block_comment and char == '*' and i + 1 < length and snippet[i+1] == '/':
                in_block_comment = False
                i += 1
            i += 1
            continue
            
        if in_single_quote:
            if char == '\\': i += 1
            elif char == "'": in_single_quote = False
            i += 1
            continue
            
        if in_double_quote:
            if char == '\\': i += 1
            elif char == '"': in_double_quote = False
            i += 1
            continue
            
        if in_backtick:
            if char == '\\' and i + 1 < length:
                i += 1
            elif char == '`':
                in_backtick = False
            i += 1
            continue

        if not (in_single_quote or in_double_quote or in_backtick):
            if char == '/' and i + 1 < length:
                if snippet[i+1] == '/':
                    in_line_comment = True
                    i += 1
                elif snippet[i+1] == '*':
                    in_block_comment = True
                    i += 1
            elif char == "'":
                in_single_quote = True
            elif char == '"':
                in_double_quote = True
            elif char == '`':
                in_backtick = True
            elif char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count < 0:
                    print(f'EXTRA }} at line {line}!')
                    return
        i += 1
        
    print(f'Final brace_count inside updateSummary: {brace_count}')

parse(target_text)
