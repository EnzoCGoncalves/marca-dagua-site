# Aplicativos MarcaFlow (custo zero)

Esta pasta mantém dois invólucros do site `https://marca-dagua-site.onrender.com/`:

- `apps/windows`: aplicativo Electron portátil para gerar `MarcaFlow-Windows.exe`.
- `apps/android`: aplicativo Android baseado em Trusted Web Activity para gerar `MarcaFlow-Android.apk`.

## Testar sem publicar

Na aba **Actions** do GitHub, abra **Gerar aplicativos gratuitos**, clique em **Run workflow** e baixe os dois artefatos ao terminar.

## Criar uma versão para os botões do site

```bash
git tag v1.0.0
git push origin v1.0.0
```

O workflow gera uma Release no GitHub com os nomes esperados pelos botões do site.

O APK de teste usa a assinatura de depuração automática do Android. Para publicar na Play Store é necessário criar e proteger uma chave definitiva; isso não é necessário para instalação direta.

O EXE não possui certificado comercial. Por isso, o Windows pode exibir o aviso “Editor desconhecido”.
