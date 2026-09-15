# Site de Marca D'água

## Instalação

```bash
python -m pip install -r requirements.txt
```

## Rodar

Com o ambiente virtual ativado:

```bash
python app.py
```

Ou, sem ativá-lo no Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe app.py
```

Depois abra:

http://127.0.0.1:5000

## Como usar

1. Escolha várias fotos de uma vez.
2. Escolha sua marca.
3. Ajuste a opacidade.
4. Ajuste o tamanho.
5. Clique em "Aplicar marca e baixar".
6. Uma foto é baixada como JPG; várias fotos são baixadas em um ZIP.

## Estrutura

- app.py = servidor e processamento
- templates/index.html = página do site
- static/style.css = visual
- requirements.txt = dependências
