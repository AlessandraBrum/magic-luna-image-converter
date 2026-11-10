import ctypes
import subprocess
import webbrowser
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image, ImageChops, ImageDraw, ImageTk, features

COR_FUNDO = "#16111C"
COR_PAINEL = "#221A2B"
COR_BORDA = "#4A3A5C"
COR_TEXTO = "#F5F0FA"
COR_TEXTO_SUAVE = "#D4C6E8"
COR_LAVANDA = "#C9B3F0"

COR_BOTAO = "#6A3D9E"
COR_BOTAO_HOVER = "#57318A"
COR_BOTAO_DESLIGADO = "#2E2340"
COR_TEXTO_DESLIGADO = "#C9B3F0"
COR_BORDA_BOTAO = "#9C7FD0"
COR_DIVISOR = "#4A3A5C"

COR_ROSA = (232, 90, 140)
COR_ROXO = (122, 47, 190)

FONTE_TITULO = ("Georgia", 36, "bold")
FONTE_SUBTITULO = ("Segoe UI", 18)
FONTE_TEXTO = ("Segoe UI", 16)
FONTE_BOTAO = ("Segoe UI", 17, "bold")
FONTE_PEQUENA = ("Segoe UI", 15)

FORMATOS = {
    "WebP": ("WEBP", ".webp"),
    "PNG": ("PNG", ".png"),
    "JPG": ("JPEG", ".jpg"),
    "GIF": ("GIF", ".gif"),
    "BMP": ("BMP", ".bmp"),
    "TIFF": ("TIFF", ".tiff"),
    "ICO": ("ICO", ".ico"),
}

if features.check("avif"):
    FORMATOS["AVIF"] = ("AVIF", ".avif")

FORMATOS_SEM_TRANSPARENCIA = ("JPG", "BMP")

TIPOS_DE_ENTRADA = "*.png *.jpg *.jpeg *.webp *.gif *.bmp *.tif *.tiff *.ico *.avif"

LINK_PORTFOLIO = "https://www.alessandrabrum.com"
# FIM CONFIGURAÇÕES


# ESTADO 
arquivo_escolhido = None
formato_escolhido = "WebP" #Vira outro formato quando abre o menu dropdown. Só pra ter um ponto de partida.
arquivo_salvo = None


# INÍCIO DESENHOS DA LUA E DAS ESTRELAS
ESCALA = 4


def criar_degrade(largura, altura):
    degrade = Image.new("RGB", (largura, altura))
    pincel = ImageDraw.Draw(degrade)

    for linha in range(altura):
        quanto = linha / (altura - 1)

        r = int(COR_ROSA[0] + (COR_ROXO[0] - COR_ROSA[0]) * quanto)
        g = int(COR_ROSA[1] + (COR_ROXO[1] - COR_ROSA[1]) * quanto)
        b = int(COR_ROSA[2] + (COR_ROXO[2] - COR_ROSA[2]) * quanto)

        pincel.line([(0, linha), (largura, linha)], fill=(r, g, b))

    return degrade


def pintar_com_degrade(mascara):
    largura, altura = mascara.size
    resultado = criar_degrade(largura, altura).convert("RGBA")

    resultado.putalpha(mascara)

    tamanho_final = (largura // ESCALA, altura // ESCALA)
    return resultado.resize(tamanho_final, Image.LANCZOS)


def desenhar_lua(tamanho):
    t = tamanho * ESCALA

    cheia = Image.new("L", (t, t), 0)
    ImageDraw.Draw(cheia).ellipse([0, 0, t - 1, t - 1], fill=255)

    mordida = Image.new("L", (t, t), 0)
    deslocamento = int(t * 0.28)
    ImageDraw.Draw(mordida).ellipse(
        [deslocamento, -deslocamento, t - 1 + deslocamento, t - 1 - deslocamento],
        fill=255,
    )

    crescente = ImageChops.subtract(cheia, mordida)
    return pintar_com_degrade(crescente)


def desenhar_estrela(tamanho):
    t = tamanho * ESCALA
    meio = t / 2
    cintura = t * 0.12

    pontos = [
        (meio, 0),
        (meio + cintura, meio - cintura),
        (t, meio),
        (meio + cintura, meio + cintura),
        (meio, t),
        (meio - cintura, meio + cintura),
        (0, meio),
        (meio - cintura, meio - cintura),
    ]

    estrela = Image.new("L", (t, t), 0)
    ImageDraw.Draw(estrela).polygon(pontos, fill=255)
    return pintar_com_degrade(estrela)


def desenhar_icone_arquivo(tamanho):
    t = tamanho * ESCALA
    icone = Image.new("RGBA", (t, t), (0, 0, 0, 0))
    pincel = ImageDraw.Draw(icone)
    traco = int(t * 0.05)
    dobra = int(t * 0.28)

    esquerda, topo = int(t * 0.18), int(t * 0.06)
    direita, base = int(t * 0.82), int(t * 0.94)
    contorno = [
        (esquerda, topo),
        (direita - dobra, topo),
        (direita, topo + dobra),
        (direita, base),
        (esquerda, base),
        (esquerda, topo),
    ]
    pincel.line(contorno, fill=COR_LAVANDA, width=traco, joint="curve")

    pincel.line(
        [(direita - dobra, topo), (direita - dobra, topo + dobra), (direita, topo + dobra)],
        fill=COR_LAVANDA,
        width=traco,
    )

    for altura_linha in (0.45, 0.60, 0.75):
        y = int(t * altura_linha)
        pincel.line(
            [(int(t * 0.32), y), (int(t * 0.68), y)],
            fill=COR_LAVANDA,
            width=traco,
        )

    return icone.resize((tamanho, tamanho), Image.LANCZOS)

def desenhar_icone_pasta(tamanho):
    t = tamanho * ESCALA
    icone = Image.new("RGBA", (t, t), (0, 0, 0, 0))
    pincel = ImageDraw.Draw(icone)
    traco = int(t * 0.08)

    def ponto(x, y):
        return (int(t * x / 24), int(t * y / 24))

    fundo_da_pasta = [
        ponto(3, 18.5), ponto(3, 5), ponto(9, 5), ponto(11, 7.5),
        ponto(19, 7.5), ponto(19, 10),
    ]
    tampa_aberta = [
        ponto(3, 18.5), ponto(5.8, 10.3), ponto(21.5, 10.3),
        ponto(19, 18.5), ponto(3, 18.5),
    ]
    pincel.line(fundo_da_pasta, fill=COR_LAVANDA, width=traco, joint="curve")
    pincel.line(tampa_aberta, fill=COR_LAVANDA, width=traco, joint="curve")

    return icone.resize((tamanho, tamanho), Image.LANCZOS)




def desenhar_icone_janela(tamanho):
    t = tamanho * ESCALA
    fundo = Image.new("RGBA", (t, t), (0, 0, 0, 0))
    ImageDraw.Draw(fundo).rounded_rectangle(
        [0, 0, t - 1, t - 1],
        radius=int(t * 0.22),
        fill=COR_BOTAO_DESLIGADO,
    )
    fundo = fundo.resize((tamanho, tamanho), Image.LANCZOS)

    tamanho_lua = int(tamanho * 0.7)
    margem = (tamanho - tamanho_lua) // 2
    lua_pequena = desenhar_lua(tamanho_lua)

    fundo.paste(lua_pequena, (margem, margem), lua_pequena)
    return fundo


def virar_imagem_ctk(imagem_pillow):
    return ctk.CTkImage(
        light_image=imagem_pillow,
        dark_image=imagem_pillow,
        size=imagem_pillow.size,
    )
# FIM DESENHOS DA LUA E DAS ESTRELAS



# INÍCIO DOS BOTÕES
def selecionar_arquivo(evento=None):
    global arquivo_escolhido

    caminho = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[("Images", TIPOS_DE_ENTRADA)],
    )

    if not caminho:
        return

    arquivo_escolhido = Path(caminho)
    rotulo_arquivo.configure(text=arquivo_escolhido.name, text_color=COR_TEXTO)

    botao_converter.configure(state="normal", fg_color=COR_BOTAO)
    rotulo_status.configure(text="Your new image will be saved in the same folder as the original.")



def escolher_formato(nome_formato):
    global formato_escolhido
    formato_escolhido = nome_formato

    if nome_formato in FORMATOS_SEM_TRANSPARENCIA:
        rotulo_status.configure(
            text=f"{nome_formato} has no transparency: transparent areas will turn white."
        )
    else:
        rotulo_status.configure(text="Your new image will be saved in the same folder as the original.")


def proximo_formato(evento=None):
    nomes = list(FORMATOS)
    posicao = nomes.index(formato_escolhido)
    proximo = nomes[(posicao + 1) % len(nomes)]

    menu_formato.set(proximo)
    escolher_formato(proximo)


def preparar_imagem(imagem):
    if formato_escolhido not in FORMATOS_SEM_TRANSPARENCIA:
        return imagem

    imagem = imagem.convert("RGBA")
    fundo_branco = Image.new("RGB", imagem.size, (255, 255, 255))
    fundo_branco.paste(imagem, mask=imagem.getchannel("A"))
    return fundo_branco

def converter_arquivo(evento=None):
    global arquivo_salvo

    if arquivo_escolhido is None:
        return

    nome_pillow, extensao = FORMATOS[formato_escolhido]
    arquivo_novo = arquivo_escolhido.with_suffix(extensao)

    if arquivo_novo == arquivo_escolhido:
        arquivo_novo = arquivo_escolhido.with_stem(arquivo_escolhido.stem + "-copy")

    try:
        with Image.open(arquivo_escolhido) as imagem:
            imagem = preparar_imagem(imagem)

            if nome_pillow == "WEBP":
                imagem.save(arquivo_novo, nome_pillow, lossless=True)
            elif nome_pillow == "JPEG":
                imagem.save(arquivo_novo, nome_pillow, quality=95)
            elif nome_pillow == "AVIF":
                imagem.save(arquivo_novo, nome_pillow, quality=90)
            else:
                imagem.save(arquivo_novo, nome_pillow)
    except FileNotFoundError:
        rotulo_status.configure(text="This file no longer exists. Please select it again.")
        return
    except OSError:
        rotulo_status.configure(text="This file could not be read as an image.")
        return

    antes = arquivo_escolhido.stat().st_size / 1024
    depois = arquivo_novo.stat().st_size / 1024

    rotulo_status.configure(
        text=f"Saved {arquivo_novo.name} in the same folder: {antes:.1f} KB → {depois:.1f} KB"
    )

    arquivo_salvo = arquivo_novo
    botao_pasta.configure(state="normal")


def abrir_pasta(evento=None):
    if arquivo_salvo is None or not arquivo_salvo.exists():
        return

    subprocess.Popen(f'explorer /select,"{arquivo_salvo}"')


def mostrar_dica(evento=None):
    dica_pasta.place(in_=botao_pasta, relx=0.5, y=-8, anchor="s")
    dica_pasta.lift()


def esconder_dica(evento=None):
    dica_pasta.place_forget()


def abrir_portfolio(evento=None):
    webbrowser.open(LINK_PORTFOLIO)
# FIM FUNÇÕES DOS BOTÕES


# INÍCIO JANELA
ctk.set_appearance_mode("dark")

janela = ctk.CTk(fg_color=COR_FUNDO)
janela.title("Magic Luna - Local Image Converter")
janela.geometry("720x620")
janela.minsize(660, 600)

icone_janela = ImageTk.PhotoImage(desenhar_icone_janela(64))
janela.after(300, lambda: janela.iconphoto(False, icone_janela))

def pintar_barra_de_titulo():
    try:
        barra = ctypes.windll.user32.GetParent(janela.winfo_id())
        cor_fundo = ctypes.c_int(0x001C1116)
        cor_texto = ctypes.c_int(0x00FFFFFF)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            barra, 35, ctypes.byref(cor_fundo), ctypes.sizeof(cor_fundo)
        )
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            barra, 36, ctypes.byref(cor_texto), ctypes.sizeof(cor_texto)
        )
    except AttributeError:
        pass


janela.after(300, pintar_barra_de_titulo)
# FIM JANELA


ceu = ctk.CTkFrame(janela, fg_color="transparent")
ceu.pack(pady=(32, 0))

imagem_lua = virar_imagem_ctk(desenhar_lua(64))
imagem_estrela_grande = virar_imagem_ctk(desenhar_estrela(22))
imagem_estrela_pequena = virar_imagem_ctk(desenhar_estrela(14))

estrela_esquerda = ctk.CTkLabel(ceu, text="", image=imagem_estrela_pequena)
estrela_esquerda.grid(row=0, column=0, sticky="s", padx=(0, 10), pady=(0, 6))

lua = ctk.CTkLabel(ceu, text="", image=imagem_lua)
lua.grid(row=0, column=1)

estrela_direita = ctk.CTkLabel(ceu, text="", image=imagem_estrela_grande)
estrela_direita.grid(row=0, column=2, sticky="n", padx=(10, 0), pady=(4, 0))

titulo = ctk.CTkLabel(
    janela,
    text="Image converter",
    font=FONTE_TITULO,
    text_color=COR_TEXTO,
)
titulo.pack(pady=(8, 4))

subtitulo = ctk.CTkLabel(
    janela,
    text="Convert your images to the format you need.",
    font=FONTE_SUBTITULO,
    text_color=COR_LAVANDA,
)
subtitulo.pack(pady=(0, 24))


painel = ctk.CTkFrame(
    janela,
    fg_color=COR_PAINEL,
    border_color=COR_BORDA,
    border_width=1,
    corner_radius=12,
)
painel.pack(fill="x", padx=40)

imagem_icone = virar_imagem_ctk(desenhar_icone_arquivo(44))
icone_arquivo = ctk.CTkLabel(painel, text="", image=imagem_icone)
icone_arquivo.pack(side="left", padx=(24, 12), pady=24)

botao_selecionar = ctk.CTkButton(
    painel,
    text="Select file",
    font=FONTE_BOTAO,
    fg_color=COR_BOTAO_DESLIGADO,
    hover_color=COR_PAINEL,
    border_color=COR_BORDA_BOTAO,
    border_width=2,
    text_color=COR_TEXTO,
    corner_radius=10,
    height=48,
    command=selecionar_arquivo,
)

menu_formato = ctk.CTkOptionMenu(
    painel,
    values=list(FORMATOS),
    command=escolher_formato,
    font=FONTE_BOTAO,
    dropdown_font=FONTE_TEXTO,
    fg_color=COR_BOTAO_DESLIGADO,
    button_color=COR_BOTAO,
    button_hover_color=COR_BOTAO_HOVER,
    text_color=COR_TEXTO,
    dropdown_fg_color=COR_PAINEL,
    dropdown_hover_color=COR_TEXTO,
    corner_radius=10,
    width=130,
    height=48,
)


rotulo_arquivo = ctk.CTkLabel(
    painel,
    text="No file selected",
    font=FONTE_TEXTO,
    text_color=COR_TEXTO_SUAVE,
    anchor="w",
)
rotulo_arquivo.pack(side="left", fill="x", expand=True)


botao_converter = ctk.CTkButton(
    janela,
    text="Convert to WebP",
    font=FONTE_BOTAO,
    fg_color=COR_BOTAO_DESLIGADO,
    hover_color=COR_BOTAO_HOVER,
    text_color="#FFFFFF",
    text_color_disabled=COR_TEXTO_DESLIGADO,
    corner_radius=10,
    height=52,
    state="disabled",
    command=converter_arquivo,
)
botao_converter.pack(fill="x", padx=40, pady=(24, 12))

rotulo_status = ctk.CTkLabel(
    janela,
    text="The WebP file will be saved in the same folder as the PNG file.",
    font=FONTE_PEQUENA,
    text_color=COR_TEXTO_SUAVE,
    wraplength=540,
)
rotulo_status.pack()

rotulo_atalhos = ctk.CTkLabel(
    janela,
    text="Ctrl+O selects a file · Enter converts it",
    font=FONTE_PEQUENA,
    text_color=COR_TEXTO_SUAVE,
)
rotulo_atalhos.pack(pady=(6, 0))

# INÍCIO RODAPÉ
rodape = ctk.CTkFrame(janela, fg_color="transparent")
rodape.pack(side="bottom", pady=(14, 18))

divisor = ctk.CTkFrame(janela, height=2, fg_color=COR_DIVISOR, corner_radius=0)
divisor.pack(side="bottom", fill="x", padx=40)

texto_rodape = ctk.CTkLabel(
    rodape,
    text="Developed by ",
    font=FONTE_PEQUENA,
    text_color=COR_TEXTO_SUAVE,
)
texto_rodape.pack(side="left")

link_nome = ctk.CTkLabel(
    rodape,
    text="Alessandra Brum",
    font=("Segoe UI", 15, "underline"),
    text_color=COR_TEXTO,
    cursor="hand2",
)
link_nome.pack(side="left")
link_nome.bind("<Button-1>", abrir_portfolio)

# ATALHOS DE TECLADO
janela.bind("<Control-o>", selecionar_arquivo)
janela.bind("<Return>", converter_arquivo)

janela.mainloop()

