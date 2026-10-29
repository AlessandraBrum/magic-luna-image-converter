from PIL import Image
from tkinter import Tk, Button, filedialog as fd, messagebox
from pathlib import Path


def selecionar_imagem():
    entrada = fd.askopenfilename(
        title="Select a PNG image file",
        filetypes=[("Imagens PNG", "*.png")]
    )

    if entrada:
        saida = Path(entrada).with_suffix(".webp")
        Image.open(entrada).save(saida, "WEBP", lossless=True)
        messagebox.showinfo(
            "Conversion complete",
            f"File successfully converted to {saida.name}"
        )


janela = Tk()
janela.title("Magic Luna converter - Easy PNG to WebP")
janela.geometry("480x300")

botao = Button(
    janela,
    text="Select PNG file",
    command=selecionar_imagem)
botao.pack()

janela.mainloop()
