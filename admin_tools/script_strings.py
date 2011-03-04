def get_strings(script):
    src = open(script,'rb').readline
    strings = []
    import tokenize,token
    state = None
    for info in tokenize.tokenize(src):
        typ,token_string = token.tok_name[info[0]],info[1]
        if state is None and typ == "NAME" and token_string == "_":
            state = True
        elif state is True and typ == "OP" and token_string == "(":
            state = "ready"
        elif state == "ready":
            if typ == "STRING":
                _string = eval(token_string)
                if not _string in strings:
                    strings.append(_string)
            state = None
    return strings

