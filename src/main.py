import tkinter as tk

from src.interface import InterfaceBagagem

def main() -> None:
    janela = tk.Tk()
    InterfaceBagagem(janela)
    janela.mainloop()

if __name__ == "__main__":
    main()
