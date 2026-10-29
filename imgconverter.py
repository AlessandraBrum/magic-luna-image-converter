from PIL import Image
from tkinter import filedialog as fd, messagebox
from pathlib import Path
import customtkinter as ctk

# INÍCIO CORES
COR_FUNDO = "#16111C"        # ameixa quase preto
COR_TEXTO = "#F5F0FA"        # quase branco
COR_LAVANDA = "#C9B3F0"      # subtítulo
COR_BOTAO = "#6A3D9E"        # roxo do botão
COR_BOTAO_HOVER = "#57318A"  # roxo ao passar o mouse
# FIM CORES

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


janela = ctk.CTk(fg_color=COR_FUNDO)
janela.title("Magic Luna converter - Easy PNG to WebP")
janela.geometry("640x420")

titulo = ctk.CTkLabel(janela, text="Image converter",
                      font=("Georgia", 36, "bold"), text_color=COR_TEXTO)
titulo.pack(pady=(40, 4))

subtitulo = ctk.CTkLabel(janela, text="PNG to WebP, with no loss of quality.",
                         font=("Segoe UI", 18), text_color=COR_LAVANDA)
subtitulo.pack(pady=(0, 24))

botao = ctk.CTkButton(
    janela,
    text="Select PNG file",
    fg_color=COR_BOTAO,
    hover_color=COR_BOTAO_HOVER,
    text_color="#FFFFFF",
    font=("Segoe UI", 17, "bold"),
    height=48,
    command=selecionar_imagem)
botao.pack(pady=40)

janela.mainloop()
