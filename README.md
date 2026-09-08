# Site de Marca D'água

## Instalação

```bash
uv init
uv add flask pillow
```

## Rodar

```bash
uv run python app.py
```

Depois abra:

http://127.0.0.1:5000

## Como usar

1. Escolha várias fotos de uma vez.
2. Escolha sua marca.
3. Ajuste a opacidade.
4. Ajuste o tamanho.
5. Clique em "Aplicar em todas e baixar ZIP".
6. O navegador baixa um ZIP contendo todas as fotos processadas.

## Estrutura

- app.py = servidor e processamento
- templates/index.html = página do site
- static/style.css = visual
- requirements.txt = dependências
