
---

## 🔧 Funcionalidades

- Tela de login com senha protegida
- Integração com API externa via Railway:
  - `https://sinais-production.up.railway.app/signals?timeframe=...`
- Filtros por tipo de sinal (BUY, SELL, HOLD)
- Alertas personalizados com:
  - Par de moedas
  - Preço alvo
  - Condição (acima/abaixo)
- Notificações locais do navegador
- Atualização automática dos dados
- Interface responsiva (mobile/tablet)

---

## 🛠 Tecnologias

- HTML5
- CSS3 (custom theme com `:root` e variáveis)
- JavaScript (ES6)
- Font Awesome (ícones)
- Chart.js (suporte a gráficos no futuro)
- API hospedada no [Railway](https://railway.app)
- Hospedagem estática via [Netlify](https://netlify.app)

---

## 📦 Deploy Manual no Netlify

1. Crie uma conta em [Netlify](https://netlify.app)
2. Faça o upload manual da pasta com:
    - `index.html`
    - `style.css`
    - `app.js`
3. **Não é necessário build command.**
4. Em **Publish directory**, use:
    ```
    . 
    ```
5. Pronto! O site será publicado.

---

## 🔐 Senha de acesso

A senha padrão é: `ope1001`  
(Definida na função `checkPassword()` do arquivo `app.js`)

---

## 📄 Licença

Este projeto é privado ou sob licença personalizada. Para uso comercial ou distribuição, entre em contato com o autor.

---

## ✨ Autor

Desenvolvido por [Seu Nome ou Empresa]  
Contato: [seu@email.com] | Instagram: [@seuperfil]
