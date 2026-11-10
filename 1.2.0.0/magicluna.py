import ctypes
import subprocess
import zlib
import webbrowser
from pathlib import Path
from tkinter import filedialog


import customtkinter as ctk
from PIL import Image, ImageChops, ImageDraw, ImageOps, ImageSequence, ImageTk, features

try:
    import pypdfium2 as pdfium

    PDF_DISPONIVEL = True
except ImportError:
    pdfium = None
    PDF_DISPONIVEL = False

Image.init()

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

FORMATOS_CANDIDATOS = {
    "WebP": ("WEBP", ".webp"),
    "PNG": ("PNG", ".png"),
    "JPG": ("JPEG", ".jpg"),
    "GIF": ("GIF", ".gif"),
    "BMP": ("BMP", ".bmp"),
    "TIFF": ("TIFF", ".tiff"),
    "ICO": ("ICO", ".ico"),
    "AVIF": ("AVIF", ".avif"),
    "PDF": ("PDF", ".pdf"),
}

RECURSOS_NECESSARIOS = {
    "WebP": "webp",
    "AVIF": "avif",
}

FORMATOS = {}
for nome, (nome_pillow, extensao) in FORMATOS_CANDIDATOS.items():
    recurso = RECURSOS_NECESSARIOS.get(nome)
    if nome_pillow in Image.SAVE and (recurso is None or features.check(recurso)):
        FORMATOS[nome] = (nome_pillow, extensao)

FORMATOS_SEM_TRANSPARENCIA = ("JPG", "BMP", "PDF")
FORMATOS_SO_COLORIDOS = ("WebP", "AVIF", "ICO")

OPCOES_DE_SALVAMENTO = {
    "WEBP": {"lossless": True},
    "JPEG": {"quality": 95},
    "AVIF": {"quality": 90},
    "TIFF": {"compression": "tiff_lzw"},
}

MODOS_COM_TRANSPARENCIA = ("RGBA", "LA", "PA", "RGBa", "La")
MODOS_DE_16_BITS = ("I", "I;16", "I;16L", "I;16B")


FORMATOS_QUE_NAO_SAO_IMAGENS = ("BUFR", "GRIB", "HDF5", "MPEG")


def listar_tipos_de_entrada():
    extensoes = sorted(
        extensao
        for extensao, formato in Image.registered_extensions().items()
        if formato in Image.OPEN and formato not in FORMATOS_QUE_NAO_SAO_IMAGENS
    )
    if PDF_DISPONIVEL and ".pdf" not in extensoes:
        extensoes.append(".pdf")
        extensoes.sort()
    return " ".join(f"*{extensao}" for extensao in extensoes)


TIPOS_DE_ENTRADA = listar_tipos_de_entrada()

TEXTO_STATUS_PADRAO = "Your new image will be saved in the same folder as the original."
TEXTO_ATALHOS = (
    "Keyboard: Ctrl+O selects an image · Ctrl+F changes the format · Enter converts it"
)
LIMITE_NOME_NO_PAINEL = 20

LINK_PORTFOLIO = "https://www.alessandrabrum.com"
# FIM CONFIGURAÇÕES


# ESTADO 
arquivo_escolhido = None
formato_escolhido = "WebP" #Vira outro formato quando abre o menu dropdown. Só pra ter um ponto de partida.
arquivo_salvo = None
resultados = {}


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




def desenhar_seta_menu(tamanho):
    t = tamanho * ESCALA
    seta = Image.new("RGBA", (t, t), (0, 0, 0, 0))
    pincel = ImageDraw.Draw(seta)
    traco = int(t * 0.14)
    pontos = [
        (int(t * 0.18), int(t * 0.34)),
        (int(t * 0.5), int(t * 0.66)),
        (int(t * 0.82), int(t * 0.34)),
    ]
    pincel.line(pontos, fill=COR_TEXTO, width=traco, joint="curve")

    raio = traco / 2
    for x, y in (pontos[0], pontos[2]):
        pincel.ellipse([x - raio, y - raio, x + raio, y + raio], fill=COR_TEXTO)

    return seta.resize((tamanho, tamanho), Image.LANCZOS)


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
def encurtar_nome(nome):
    if len(nome) <= LIMITE_NOME_NO_PAINEL:
        return nome
    return nome[: LIMITE_NOME_NO_PAINEL - 3] + "..."


def texto_status_do_formato():
    if formato_escolhido in FORMATOS_SEM_TRANSPARENCIA:
        return f"{formato_escolhido} has no transparency: transparent areas will turn white."
    return TEXTO_STATUS_PADRAO


def caminho_livre(destino):
    if not destino.exists():
        return destino

    numero = 1
    while True:
        sufixo = "-copy" if numero == 1 else f"-copy-{numero}"
        candidato = destino.with_stem(destino.stem + sufixo)
        if not candidato.exists():
            return candidato
        numero += 1


def mensagem_de_erro(erro):
    if PDF_DISPONIVEL and isinstance(erro, pdfium.PdfiumError):
        return "This PDF could not be read. It may be damaged or password-protected."
    if isinstance(erro, FileNotFoundError):
        return "This file no longer exists. Please select it again."
    if isinstance(erro, PermissionError):
        return "No permission to save in this folder."
    if isinstance(erro, Image.UnidentifiedImageError):
        return "This file could not be read as an image."
    if isinstance(erro, (Image.DecompressionBombError, MemoryError)):
        return "This image is too large to convert."
    if isinstance(erro, (OSError, ValueError)):
        return f"This image could not be saved as {formato_escolhido}."
    return "Something went wrong while converting this image."


def selecionar_arquivo(evento=None):
    global arquivo_escolhido

    caminho = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[("Images", TIPOS_DE_ENTRADA), ("All files", "*.*")],
    )

    if not caminho:
        return

    arquivo_escolhido = Path(caminho)
    rotulo_arquivo.configure(text=encurtar_nome(arquivo_escolhido.name), text_color=COR_TEXTO)

    botao_converter.configure(state="normal", fg_color=COR_BOTAO)
    rotulo_status.configure(text=texto_status_do_formato())



def escolher_formato(nome_formato):
    global formato_escolhido
    formato_escolhido = nome_formato
    rotulo_status.configure(text=texto_status_do_formato())


def proximo_formato(evento=None):
    nomes = list(FORMATOS)
    posicao = nomes.index(formato_escolhido)
    proximo = nomes[(posicao + 1) % len(nomes)]

    menu_formato.set(proximo)
    escolher_formato(proximo)


def preparar_imagem(imagem):
    imagem = ImageOps.exif_transpose(imagem)

    if imagem.mode == "La":
        imagem = imagem.convert("LA")

    if imagem.mode in MODOS_DE_16_BITS:
        imagem = imagem.point(lambda valor: valor / 256).convert("L")

    tem_transparencia = imagem.mode in MODOS_COM_TRANSPARENCIA or "transparency" in imagem.info

    if formato_escolhido in FORMATOS_SEM_TRANSPARENCIA:
        imagem = imagem.convert("RGBA")
        fundo_branco = Image.new("RGB", imagem.size, (255, 255, 255))
        fundo_branco.paste(imagem, mask=imagem.getchannel("A"))
        return fundo_branco

    if tem_transparencia:
        return imagem.convert("RGBA")

    if imagem.mode == "L" and formato_escolhido not in FORMATOS_SO_COLORIDOS:
        return imagem

    return imagem.convert("RGB")


def renderizar_pdf(caminho):
    documento = pdfium.PdfDocument(str(caminho))
    try:
        imagens = []
        for pagina in documento:
            largura, altura = pagina.get_size()
            escala = min(4, 8000 / max(largura, altura))
            imagens.append(pagina.render(scale=escala).to_pil())
        return imagens
    finally:
        documento.close()


def carregar_imagens(caminho):
    if caminho.suffix.lower() == ".pdf":
        return [preparar_imagem(pagina).copy() for pagina in renderizar_pdf(caminho)]

    with Image.open(caminho) as imagem:
        if formato_escolhido == "PDF":
            quadros = [quadro.copy() for quadro in ImageSequence.Iterator(imagem)]
        else:
            quadros = [imagem]
        return [preparar_imagem(quadro).copy() for quadro in quadros]


def definir_destinos(origem, extensao, quantidade):
    if quantidade == 1:
        return [caminho_livre(origem.with_suffix(extensao))]

    destinos = []
    for numero in range(1, quantidade + 1):
        destinos.append(caminho_livre(origem.with_name(f"{origem.stem}-page-{numero}{extensao}")))
    return destinos


def montar_fluxo(entradas, dados):
    return f"<< {entradas} /Length {len(dados)} >>\nstream\n".encode() + dados + b"\nendstream"


def gravar_pdf(imagens, destino, resolucao=150):
    ids_paginas = [5 + 3 * posicao for posicao in range(len(imagens))]
    kids = " ".join(f"{numero} 0 R" for numero in ids_paginas)
    objetos = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: f"<< /Type /Pages /Kids [{kids}] /Count {len(imagens)} >>".encode(),
    }

    for posicao, imagem in enumerate(imagens):
        if imagem.mode not in ("L", "RGB"):
            imagem = imagem.convert("RGB")

        largura, altura = imagem.size
        pagina_largura = largura * 72 / resolucao
        pagina_altura = altura * 72 / resolucao
        reducao = min(1, 14400 / max(pagina_largura, pagina_altura))
        pagina_largura *= reducao
        pagina_altura *= reducao

        espaco_de_cor = "/DeviceGray" if imagem.mode == "L" else "/DeviceRGB"
        id_imagem = 3 + 3 * posicao
        id_conteudo = 4 + 3 * posicao
        id_pagina = 5 + 3 * posicao

        objetos[id_imagem] = montar_fluxo(
            f"/Type /XObject /Subtype /Image /Width {largura} /Height {altura} "
            f"/ColorSpace {espaco_de_cor} /BitsPerComponent 8 /Filter /FlateDecode",
            zlib.compress(imagem.tobytes(), 6),
        )
        objetos[id_conteudo] = montar_fluxo(
            "",
            f"q {pagina_largura:.4f} 0 0 {pagina_altura:.4f} 0 0 cm /Im0 Do Q".encode(),
        )
        objetos[id_pagina] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {pagina_largura:.4f} {pagina_altura:.4f}] "
            f"/Resources << /XObject << /Im0 {id_imagem} 0 R >> >> /Contents {id_conteudo} 0 R >>"
        ).encode()

    saida = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    posicoes = {}
    for numero in sorted(objetos):
        posicoes[numero] = len(saida)
        saida += f"{numero} 0 obj\n".encode() + objetos[numero] + b"\nendobj\n"

    inicio_xref = len(saida)
    total = len(objetos) + 1
    saida += f"xref\n0 {total}\n".encode() + b"0000000000 65535 f \n"
    for numero in sorted(objetos):
        saida += f"{posicoes[numero]:010d} 00000 n \n".encode()
    saida += (
        f"trailer\n<< /Size {total} /Root 1 0 R >>\nstartxref\n{inicio_xref}\n%%EOF\n"
    ).encode()

    with open(destino, "wb") as arquivo:
        arquivo.write(saida)


def gravar_imagens(imagens, destinos, nome_pillow):
    opcoes = OPCOES_DE_SALVAMENTO.get(nome_pillow, {})

    if nome_pillow == "PDF":
        gravar_pdf(imagens, destinos[0])
        return

    for imagem, destino in zip(imagens, destinos):
        imagem.save(destino, nome_pillow, **opcoes)


def converter_arquivo(evento=None):
    global arquivo_salvo

    if arquivo_escolhido is None:
        return

    eh_pdf = arquivo_escolhido.suffix.lower() == ".pdf"

    if eh_pdf and formato_escolhido == "PDF":
        rotulo_status.configure(text="This file is already a PDF. Choose another format.")
        return

    if eh_pdf and not PDF_DISPONIVEL:
        rotulo_status.configure(text="To read PDF files, install pypdfium2: pip install pypdfium2")
        return

    nome_pillow, extensao = FORMATOS[formato_escolhido]
    chave = (arquivo_escolhido, formato_escolhido)
    destinos = []
    comecou_a_gravar = False

    try:
        imagens = carregar_imagens(arquivo_escolhido)
        if nome_pillow == "PDF":
            destinos = resultados.get(chave) or definir_destinos(arquivo_escolhido, extensao, 1)
        else:
            destinos = resultados.get(chave) or definir_destinos(arquivo_escolhido, extensao, len(imagens))
        comecou_a_gravar = True
        gravar_imagens(imagens, destinos, nome_pillow)
        antes = arquivo_escolhido.stat().st_size / 1024
        depois = sum(destino.stat().st_size for destino in destinos) / 1024
    except Exception as erro:
        if comecou_a_gravar:
            for destino in destinos:
                try:
                    destino.unlink(missing_ok=True)
                except OSError:
                    pass
        rotulo_status.configure(text=mensagem_de_erro(erro))
        return

    resultados[chave] = destinos

    if len(destinos) == 1:
        rotulo_status.configure(
            text=f"Saved {destinos[0].name} in the same folder: {antes:.1f} KB → {depois:.1f} KB"
        )
    else:
        rotulo_status.configure(
            text=f"Saved {len(destinos)} pages in the same folder: {antes:.1f} KB → {depois:.1f} KB"
        )

    arquivo_salvo = destinos[0]
    botao_pasta.configure(state="normal")


def abrir_pasta(evento=None):
    if arquivo_salvo is None or not arquivo_salvo.exists():
        return

    subprocess.Popen(f'explorer /select,"{arquivo_salvo}"')


def mostrar_dica(evento=None):
    if botao_pasta.cget("state") != "normal":
        return

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
janela.geometry("720x600")
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
    width=125,
    height=48,
    command=selecionar_arquivo,
)

divisor_painel = ctk.CTkFrame(painel, width=2, height=48, fg_color=COR_DIVISOR, corner_radius=0)

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
    dropdown_hover_color=COR_BOTAO,
    dropdown_text_color=COR_TEXTO,
    corner_radius=10,
    width=130,
    height=48,
)
menu_formato.set(formato_escolhido)

tela_menu = menu_formato._canvas
coordenadas_seta = tela_menu.coords("dropdown_arrow")
if coordenadas_seta:
    xs, ys = coordenadas_seta[0::2], coordenadas_seta[1::2]
    imagem_seta_menu = ImageTk.PhotoImage(
        desenhar_seta_menu(int(menu_formato._apply_widget_scaling(20)))
    )
    tela_menu.itemconfigure("dropdown_arrow", state="hidden")
    tela_menu.create_image(
        sum(xs) / len(xs), sum(ys) / len(ys), image=imagem_seta_menu, tags="seta_suave"
    )
    tela_menu.tag_raise("seta_suave")

rotulo_arquivo = ctk.CTkLabel(
    painel,
    text="No image selected",
    font=FONTE_TEXTO,
    text_color=COR_TEXTO_SUAVE,
    anchor="w",
)

menu_formato.pack(side="right", padx=(16, 24), pady=24)
divisor_painel.pack(side="right")
botao_selecionar.pack(side="right", padx=(12, 16))
rotulo_arquivo.pack(side="left", fill="x", expand=True)


acoes = ctk.CTkFrame(janela, fg_color="transparent")
acoes.pack(fill="x", padx=40, pady=(24, 12))

imagem_pasta = virar_imagem_ctk(desenhar_icone_pasta(28))
botao_pasta = ctk.CTkButton(
    acoes,
    text="",
    image=imagem_pasta,
    fg_color=COR_BOTAO_DESLIGADO,
    hover_color=COR_BOTAO_HOVER,
    border_color=COR_BORDA,
    border_width=2,
    corner_radius=10,
    width=52,
    height=52,
    state="disabled",
    command=abrir_pasta,
)
botao_pasta.pack(side="right", padx=(12, 0))

dica_pasta = ctk.CTkLabel(
    janela,
    text="Open folder",
    font=FONTE_PEQUENA,
    text_color=COR_TEXTO,
    fg_color=COR_PAINEL,
    corner_radius=8,
    padx=10,
    pady=4,
)
botao_pasta.bind("<Enter>", mostrar_dica, add="+")
botao_pasta.bind("<Leave>", esconder_dica, add="+")


botao_converter = ctk.CTkButton(
    acoes,
    text="Convert image",
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
botao_converter.pack(side="left", fill="x", expand=True)

rotulo_status = ctk.CTkLabel(
    janela,
    text=TEXTO_STATUS_PADRAO,
    font=FONTE_PEQUENA,
    text_color=COR_TEXTO_SUAVE,
    wraplength=620,
)
rotulo_status.pack()

rotulo_atalhos = ctk.CTkLabel(
    janela,
    text=TEXTO_ATALHOS,
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
for letra in "oO":
    janela.bind(f"<Control-{letra}>", selecionar_arquivo)
for letra in "fF":
    janela.bind(f"<Control-{letra}>", proximo_formato)
for letra in "eE":
    janela.bind(f"<Control-{letra}>", abrir_pasta)
janela.bind("<Return>", converter_arquivo)
janela.bind("<KP_Enter>", converter_arquivo)

janela.mainloop()

