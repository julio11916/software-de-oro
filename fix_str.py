import re

text = open('static/js/usuario/orden_personalizada.js', encoding='utf-8').read()
text = re.sub(r'//.*', '', text)
text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

# remove strings inside quotes to see if we have unclosed quotes
def find_unclosed():
    i = 0
    while i < len(text):
        char = text[i]
        if char in ("'", '"', '`'):
            quote = char
            start = i
            i += 1
            found = False
            while i < len(text):
                if text[i] == '\\':
                    i += 2
                    continue
                if text[i] == quote:
                    found = True
                    break
                # JS template literals can have newlines, but single/double cannot unless escaped
                if text[i] == '\n' and quote != '`':
                    print("Unclosed string at", start, repr(text[max(0, start-50):min(len(text), start+50)]))
                    return
                i += 1
            if not found:
                print("Unclosed string starting at", start, repr(text[max(0, start-50):min(len(text), start+50)]))
                return
        i += 1
    print("All quotes closed")
find_unclosed()
