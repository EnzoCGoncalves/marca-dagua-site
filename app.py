# ==========================================
# IMPORTAÇÕES
# ==========================================

# Flask cria o site e recebe os arquivos enviados
from flask import Flask, render_template, request, send_file

# Pillow trabalha com as imagens
from PIL import Image

# Bibliotecas auxiliares
from io import BytesIO
import zipfile


# ==========================================
# CONFIGURAÇÃO DO SITE
# ==========================================

# Cria a aplicação Flask
app = Flask(__name__)

# Limita o tamanho total do envio para 100 MB
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024


# ==========================================
# FUNÇÃO PARA CRIAR A MARCA D'ÁGUA
# ==========================================

def adicionar_marca_dagua(foto, marca, opacidade=30, tamanho=30):

    # Abre a foto principal
    imagem = Image.open(foto).convert("RGBA")

    # Abre a imagem da sua marca
    logo = Image.open(marca).convert("RGBA")

    # ==========================================
    # REDIMENSIONAR A MARCA
    # ==========================================

    # Define a largura da marca como uma porcentagem
    # da largura da foto
    largura_maxima = int(imagem.width * (tamanho / 100))

    # Evita que a marca fique maior que a própria foto
    largura_maxima = min(largura_maxima, imagem.width)

    # Mantém a proporção original da marca
    proporcao = largura_maxima / logo.width
    nova_altura = int(logo.height * proporcao)

    # Redimensiona a marca
    logo = logo.resize(
        (largura_maxima, nova_altura),
        Image.Resampling.LANCZOS
    )

    # ==========================================
    # ALTERAR A TRANSPARÊNCIA
    # ==========================================

    # Pega o canal Alpha da marca
    alpha = logo.getchannel("A")

    # Aplica a opacidade escolhida
    alpha = alpha.point(
        lambda pixel: int(pixel * (opacidade / 100))
    )

    # Coloca o novo Alpha na marca
    logo.putalpha(alpha)

    # ==========================================
    # CALCULAR O CENTRO
    # ==========================================

    # Calcula a posição horizontal
    x = (imagem.width - logo.width) // 2

    # Calcula a posição vertical
    y = (imagem.height - logo.height) // 2

    # ==========================================
    # COLOCAR A MARCA NO CENTRO
    # ==========================================

    # Junta a marca com a foto
    imagem.alpha_composite(logo, (x, y))

    # ==========================================
    # PREPARAR O ARQUIVO FINAL
    # ==========================================

    # Cria um arquivo na memória
    arquivo_final = BytesIO()

    # Salva em JPEG com boa qualidade
    imagem.convert("RGB").save(
        arquivo_final,
        format="JPEG",
        quality=95
    )

    # Volta para o começo do arquivo
    arquivo_final.seek(0)

    # Retorna a imagem pronta
    return arquivo_final


# ==========================================
# ROTA PRINCIPAL
# ==========================================

@app.route("/", methods=["GET", "POST"])
def index():

    # Se abriu o site normalmente
    if request.method == "GET":
        return render_template("index.html")

    # ==========================================
    # RECEBER VÁRIAS FOTOS
    # ==========================================

    # Recebe todas as fotos selecionadas
    fotos = request.files.getlist("fotos")

    # Recebe a marca
    marca = request.files.get("marca")

    # Verifica se os arquivos existem
    if not fotos or not marca:
        return "Envie pelo menos uma foto e uma marca d'água."

    # ==========================================
    # RECEBER CONFIGURAÇÕES
    # ==========================================

    # Pega a opacidade
    opacidade = int(request.form.get("opacidade", 30))

    # Pega o tamanho
    tamanho = int(request.form.get("tamanho", 30))

    # ==========================================
    # CRIAR O ZIP
    # ==========================================

    # Cria o ZIP na memória
    zip_final = BytesIO()

    # Abre o arquivo ZIP
    with zipfile.ZipFile(
        zip_final,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zip_file:

        # Percorre todas as fotos
        for numero, foto in enumerate(fotos, start=1):

            # Ignora campos vazios
            if not foto.filename:
                continue

            try:
                # Processa a foto
                resultado = adicionar_marca_dagua(
                    foto,
                    marca,
                    opacidade,
                    tamanho
                )

                # Define um nome seguro para a saída
                nome_original = foto.filename.rsplit("/", 1)[-1]
                nome_original = nome_original.rsplit("\\", 1)[-1]

                # Remove a extensão original
                nome_base = nome_original.rsplit(".", 1)[0]

                # Nome da foto processada
                nome_saida = f"{nome_base}_marca_dagua.jpg"

                # Coloca a foto dentro do ZIP
                zip_file.writestr(
                    nome_saida,
                    resultado.getvalue()
                )

            except Exception as erro:
                # Se uma foto der erro, continua com as outras
                print(f"Erro ao processar {foto.filename}: {erro}")

    # Volta para o começo do ZIP
    zip_final.seek(0)

    # ==========================================
    # BAIXAR O ZIP
    # ==========================================

    return send_file(
        zip_final,
        mimetype="application/zip",
        as_attachment=True,
        download_name="fotos_com_marca_dagua.zip"
    )


# ==========================================
# INICIAR O SERVIDOR
# ==========================================

if __name__ == "__main__":

    # Inicia o site localmente
    app.run(debug=True)
