from io import BytesIO
import os
from pathlib import Path
import zipfile

from flask import Flask, jsonify, render_template, request, send_file, send_from_directory
from PIL import Image, ImageOps, UnidentifiedImageError
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
MAX_DIMENSAO = 4000
FORMATOS = {"JPEG", "PNG", "WEBP", "BMP", "GIF", "TIFF"}


def preparar_marca(arquivo):
    marca = Image.open(arquivo)
    if marca.format not in FORMATOS:
        raise UnidentifiedImageError
    marca.load()
    return ImageOps.exif_transpose(marca).convert("RGBA")


def adicionar_marca_dagua(foto, marca_original, opacidade=30, tamanho=30):
    imagem = Image.open(foto)
    if imagem.format not in FORMATOS:
        raise UnidentifiedImageError
    imagem = ImageOps.exif_transpose(imagem).convert("RGBA")
    imagem.thumbnail((MAX_DIMENSAO, MAX_DIMENSAO), Image.Resampling.LANCZOS)

    largura = min(imagem.width, max(1, round(imagem.width * tamanho / 100)))
    altura = max(1, round(marca_original.height * largura / marca_original.width))
    marca = marca_original.resize((largura, altura), Image.Resampling.LANCZOS)
    if opacidade < 100:
        marca.putalpha(marca.getchannel("A").point(lambda p: p * opacidade // 100))

    posicao = ((imagem.width - marca.width) // 2, (imagem.height - marca.height) // 2)
    imagem.alpha_composite(marca, posicao)
    saida = BytesIO()
    # Evita o custo alto de optimize=True; progressive mantém arquivo leve.
    imagem.convert("RGB").save(saida, "JPEG", quality=88, progressive=True)
    return saida.getvalue()


def nome_de_saida(nome):
    seguro = secure_filename(Path(nome).name) or "foto"
    return f"{Path(seguro).stem}_marca_dagua.jpg"


@app.errorhandler(413)
def arquivo_grande(_erro):
    return jsonify(erro="O envio ultrapassa o limite de 100 MB."), 413


@app.get("/service-worker.js")
def service_worker():
    resposta = send_from_directory(app.static_folder, "service-worker.js")
    resposta.headers["Content-Type"] = "application/javascript; charset=utf-8"
    resposta.headers["Cache-Control"] = "no-cache"
    resposta.headers["Service-Worker-Allowed"] = "/"
    return resposta


@app.get("/.well-known/assetlinks.json")
def android_asset_links():
    return jsonify([
        {
            "relation": ["delegate_permission/common.handle_all_urls"],
            "target": {
                "namespace": "android_app",
                "package_name": "com.enzocgoncalves.marcaflow",
                "sha256_cert_fingerprints": [
                    "16:CC:14:99:87:E8:B8:D5:1E:90:6A:F7:C3:D3:29:62:2F:2A:93:56:67:23:65:C6:2F:B6:96:EC:93:38:B5:11"
                ],
            },
        }
    ])


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    fotos = [f for f in request.files.getlist("fotos") if f.filename]
    marca_arquivo = request.files.get("marca")
    if not fotos or not marca_arquivo or not marca_arquivo.filename:
        return jsonify(erro="Selecione ao menos uma foto e uma marca d’água."), 400

    try:
        opacidade = max(1, min(100, int(request.form.get("opacidade", 30))))
        tamanho = max(5, min(80, int(request.form.get("tamanho", 30))))
        marca = preparar_marca(marca_arquivo)  # aberta uma única vez por lote
    except (ValueError, UnidentifiedImageError, OSError):
        return jsonify(erro="A marca d’água não é uma imagem válida."), 400

    resultados, erros, usados = [], [], set()
    for foto in fotos:
        try:
            conteudo = adicionar_marca_dagua(foto, marca, opacidade, tamanho)
            nome = nome_de_saida(foto.filename)
            base, sufixo, numero = Path(nome).stem, Path(nome).suffix, 2
            while nome.lower() in usados:
                nome = f"{base}_{numero}{sufixo}"
                numero += 1
            usados.add(nome.lower())
            resultados.append((nome, conteudo))
        except (UnidentifiedImageError, OSError, ValueError):
            erros.append(Path(foto.filename).name)

    if not resultados:
        return jsonify(erro="Nenhuma das fotos enviadas pôde ser processada."), 400

    if len(resultados) == 1 and len(fotos) == 1:
        nome, conteudo = resultados[0]
        return send_file(BytesIO(conteudo), mimetype="image/jpeg", as_attachment=True,
                         download_name=nome, max_age=0)

    pacote = BytesIO()
    # JPEG já é comprimido: ZIP_STORED é bem mais rápido que recomprimir cada foto.
    with zipfile.ZipFile(pacote, "w", compression=zipfile.ZIP_STORED) as arquivo_zip:
        for nome, conteudo in resultados:
            arquivo_zip.writestr(nome, conteudo)
        if erros:
            arquivo_zip.writestr("LEIA-ME.txt", "Imagens não processadas:\n" + "\n".join(erros))
    pacote.seek(0)
    return send_file(pacote, mimetype="application/zip", as_attachment=True,
                     download_name="fotos_com_marca_dagua.zip", max_age=0)


if __name__ == "__main__":
    # O recarregador do Flask pode iniciar o processo duas vezes e conflitar com
    # a sincronização do OneDrive. Ative-o apenas quando realmente precisar:
    # PowerShell: $env:FLASK_DEBUG="1"; python app.py
    modo_debug = os.environ.get("FLASK_DEBUG") == "1"
    print("\nMarcaFlow disponível em http://127.0.0.1:5000\n")
    app.run(host="127.0.0.1", port=5000, debug=modo_debug, use_reloader=modo_debug)
