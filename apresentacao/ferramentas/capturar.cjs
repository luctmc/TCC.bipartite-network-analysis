/**
 * Regrava as capturas reais usadas na reserva da demonstração (img/app/).
 *
 * Opcional: exige Playwright (`npm i -D playwright && npx playwright install chromium`
 * numa pasta qualquer). Com o sistema no ar sobre as fixtures:
 *
 *   python -m edugraph api serve --root data/fixtures
 *   node apresentacao/ferramentas/capturar.cjs [saida]
 *
 * Gera PNGs 3200 × 1800 (1600 × 900 com escala 2). Converta para WebP
 * (ex.: `cwebp -q 84`) e substitua os arquivos de apresentacao/img/app/.
 */
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

const APP = process.env.EDUGRAPH_URL || "http://127.0.0.1:8000";
const SAIDA = path.resolve(process.argv[2] || "capturas");
fs.mkdirSync(SAIDA, { recursive: true });

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 2 });
  let p = await ctx.newPage();
  const longe = () => p.mouse.move(1, 899);
  const foto = async (nome, espera = 700) => {
    await longe();
    await p.waitForTimeout(espera);
    await p.screenshot({ path: path.join(SAIDA, `${nome}.png`) });
    console.log("ok", nome);
  };

  await p.goto(`${APP}/?tour`);
  await p.waitForTimeout(2500);
  await foto("tour-01");
  for (let i = 2; i <= 9; i++) { await p.keyboard.press("ArrowRight"); await foto(`tour-0${i}`); }
  await p.keyboard.press("Escape");

  await p.close(); p = await ctx.newPage();
  await p.goto(`${APP}/?semtour`);
  await p.waitForTimeout(2000);
  await foto("lab-vazio");
  await p.click(".botao-montar");
  await p.waitForTimeout(800);
  await p.keyboard.press("Space");
  const etapas = await p.$$(".lab-etapa-chips button");
  for (let i = 0; i < 3; i++) {
    await etapas[i].click();
    await p.keyboard.press("Space");
    await p.waitForTimeout(i === 2 ? 2600 : 1800);
    await p.keyboard.press("Space");
    await foto(`louvain-etapa-${i + 1}`);
  }
  // A etapa 4 pelo botão "Ir ao resultado": tocar até o fim recomeçaria do quadro 1.
  await p.click('button[aria-label="Ir ao resultado"]');
  await p.waitForTimeout(1800);
  await foto("louvain-etapa-4");
  const convite = await p.$(".lab-convite button:not(.convite-principal)");
  if (convite) await convite.click();
  await p.check("text=As áreas que o gerador plantou");
  await p.$eval('[data-tour="revelar"]', (e) => e.scrollIntoView({ block: "center" }));
  await foto("louvain-revelar");

  await p.close(); p = await ctx.newPage();
  await p.goto(`${APP}/?semtour`);
  await p.waitForTimeout(1500);
  await p.click('.lab-algoritmo button:has-text("Girvan")');
  await p.click(".botao-montar");
  await p.waitForTimeout(2500);
  const chips = await p.$$(".lab-etapa-chips button");
  await chips[2].click();
  await p.waitForTimeout(9000);
  await foto("gn-algoritmo", 100);
  await p.click('button[aria-label="Ir ao resultado"]');
  await foto("gn-resultado", 1600);

  await p.close(); p = await ctx.newPage();
  await p.goto(`${APP}/?semtour#explorar`);
  await p.waitForTimeout(4000);
  await foto("explorar");
  await b.close();
})();
