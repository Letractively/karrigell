Login("admin")

def index():
    frameset = FRAMESET(cols="25%,*",borderwidth=0)
    frameset <= FRAME(src="../fileMenu.py")
    frameset <= FRAME(name="right")

    return frameset