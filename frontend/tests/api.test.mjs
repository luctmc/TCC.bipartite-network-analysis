import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { test } from "node:test";
import ts from "typescript";

const source = await readFile(new URL("../src/api.ts", import.meta.url), "utf8");
const { outputText } = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
});
const { api, ApiError } = await import(`data:text/javascript;base64,${Buffer.from(outputText).toString("base64")}`);

for (const [nome, body, expected] of [
  ["preserva detalhe textual", { detail: "artefato ausente" }, "artefato ausente"],
  ["formata local e mensagem do FastAPI", { detail: [{ loc: ["query", "top"], msg: "deve ser positivo" }] }, "query.top: deve ser positivo"],
  ["usa statusText para detalhe desconhecido", { detail: { erro: "inválido" } }, "Unprocessable Entity"],
  ["usa statusText para array vazio", { detail: [] }, "Unprocessable Entity"],
  ["ignora entradas malformadas", { detail: [null, {}, { loc: ["path", "id"], msg: "inválido" }] }, "path.id: inválido"],
]) {
  test(nome, async (t) => {
    t.mock.method(globalThis, "fetch", async () => ({ ok: false, status: 422, statusText: "Unprocessable Entity", json: async () => body }));
    await assert.rejects(api.health(), (error) => error instanceof ApiError && error.status === 422 && error.message === expected);
  });
}

test("mantém mensagem quando resposta não é JSON", async (t) => {
  t.mock.method(globalThis, "fetch", async () => ({ ok: false, status: 500, statusText: "Internal Server Error", json: async () => { throw new SyntaxError(); } }));
  await assert.rejects(api.health(), { message: "Internal Server Error" });
});
