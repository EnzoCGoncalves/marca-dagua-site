# ==========================================
# IMPORTAÇÕES
# ==========================================

from flask import Flask, render_template, request, send_file
from PIL import Image, ImageOps
from io import BytesIO
import zipfile


# ==========================================
# CONFIGURAÇÃO DO SITE
# ==========================================

app = Flask(__name__)

# Limita o tamanho total do envio para 100 MB
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

# Limita a dimensão máxima das fotos processadas.
# Isso evita processamento excessivamente pesado em celulares
# e deixa a geração do ZIP bem mais rápida.
MAX_DIMENSAO = 4000


# ==========================================
# FUNÇÃO PARA CRIAR A MARCA D'ÁGUA
# ==========================================

def adicionar_marca_dagua(foto, marca, opacidade=30, tamanho=30):

    # Abre a foto e corrige automaticamente a rotação do celular
    imagem = Image.open(foto)
    imagem = ImageOps.exif_transpose(imagem).convert("RGBA")

    # Reduz fotos gigantes mantendo boa qualidade.
    # Fotos menores que isso não são alteradas.
    imagem.thumbnail(
        (MAX_DIMENSAO, MAX_DIMENSAO),
        Image.Resampling.LANCZOS
    )

    # Abre a marca
    logo = Image.open(marca).convert("RGBA")

    # Define a largura da marca como porcentagem da foto
    largura_maxima = max(1, int(imagem.width * (tamanho / 100)))
    largura_maxima = min(largura_maxima, imagem.width)

    # Mantém a proporção da marca
    proporcao = largura_maxima / logo.width
    nova_altura = max(1, int(logo.height * proporcao))

    # Redimensiona a marca
    logo = logo.resize(
        (largura_maxima, nova_altura),
        Image.Resampling.LANCZOS
    )

    # ==========================================
    # ALTERAR A TRANSPARÊNCIA
    # ==========================================

    alpha = logo.getchannel("A")
    alpha = alpha.point(
        lambda pixel: int(pixel * (opacidade / 100))
    )
    logo.putalpha(alpha)

    # ==========================================
    # COLOCAR NO CENTRO
    # ==========================================

    x = (imagem.width - logo.width) // 2
    y = (imagem.height - logo.height) // 2

    imagem.alpha_composite(logo, (x, y))

    # ==========================================
    # PREPARAR O ARQUIVO FINAL
    # ==========================================

    arquivo_final = BytesIO()

    # Qualidade 88 reduz bastante o tamanho do ZIP
    # sem deixar a foto visualmente ruim para uso comum.
    imagem.convert("RGB").save(
        arquivo_final,
        format="JPEG",
        quality=88,
        optimize=True,
        progressive=True
    )

    arquivo_final.seek(0)

    return arquivo_final


# ==========================================
# ROTA PRINCIPAL
# ==========================================

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "GET":
        return render_template("index.html")

    # ==========================================
    # RECEBER ARQUIVOS
    # ==========================================

    fotos = request.files.getlist("fotos")
    marca = request.files.get("marca")

    if not fotos or not marca:
        return "Envie pelo menos uma foto e uma marca d'água.", 400

    # ==========================================
    # RECEBER CONFIGURAÇÕES
    # ==========================================

    try:
        opacidade = max(1, min(100, int(request.form.get("opacidade", 30))))
        tamanho = max(5, min(80, int(request.form.get("tamanho", 30))))
    except ValueError:
        return "Configuração inválida.", 400

    # ==========================================
    # CRIAR O ZIP
    # ==========================================

    zip_final = BytesIO()

    with zipfile.ZipFile(
        zip_final,
        "w",
        zipfile.ZIP_DEFLATED,
        compresslevel=6
    ) as zip_file:

        for foto in fotos:

            if not foto.filename:
                continue

            try:
                resultado = adicionar_marca_dagua(
                    foto,
                    marca,
                    opacidade,
                    tamanho
                )

                nome_original = foto.filename.rsplit("/", 1)[-1]
                nome_original = nome_original.rsplit("\\", 1)[-1]

                nome_base = nome_original.rsplit(".", 1)[0]
                nome_saida = f"{nome_base}_marca_dagua.jpg"

                zip_file.writestr(
                    nome_saida,
                    resultado.getvalue()
                )

            except Exception as erro:
                print(f"Erro ao processar {foto.filename}: {erro}")

    zip_final.seek(0)

    # ==========================================
    # BAIXAR O ZIP
    # ==========================================

    return send_file(
        zip_final,
        mimetype="application/zip",
        as_attachment=True,
        download_name="fotos_com_marca_dagua.zip",
        max_age=0
    )


# ==========================================
# INICIAR O SERVIDOR
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
