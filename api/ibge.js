/**
 * Proxy de reserva para as APIs públicas do IBGE (servicodados.ibge.gov.br).
 * O index.html chama o IBGE direto do navegador e só usa esta função se a
 * chamada direta falhar (rede/CORS). Aceita apenas as APIs usadas pelo painel.
 *
 * Uso: /api/ibge?path=/api/v3/agregados/6579/periodos/-1/variaveis/9324&localidades=N3[all]
 */
const BASE = "https://servicodados.ibge.gov.br";
const PERMITIDO = /^\/api\/(v1\/localidades|v3\/agregados|v3\/malhas)\/[\w\-\/\[\],|]*$/;

module.exports = async (req, res) => {
  const q = { ...(req.query || {}) };
  const path = String(q.path || "");
  delete q.path;
  if (!PERMITIDO.test(path)) return res.status(400).json({ erro: "consulta não permitida" });

  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(q)) {
    if (!/^[a-zA-Z]+$/.test(k)) continue;
    qs.set(k, String(v).slice(0, 4000));
  }

  let ultimoErro = null;
  for (let t = 0; t < 2; t++) {
    try {
      const r = await fetch(`${BASE}${path}${qs.toString() ? `?${qs}` : ""}`, {
        headers: { Accept: "application/json, application/vnd.geo+json" },
        signal: AbortSignal.timeout(20000),
      });
      if (!r.ok) {
        ultimoErro = `HTTP ${r.status}`;
        if (r.status >= 500) { await new Promise((s) => setTimeout(s, 700)); continue; }
        return res.status(r.status).json({ erro: ultimoErro });
      }
      const texto = await r.text();
      res.setHeader("Cache-Control", "public, s-maxage=21600, stale-while-revalidate=86400");
      res.setHeader("Content-Type", "application/json; charset=utf-8");
      return res.status(200).send(texto);
    } catch (e) {
      ultimoErro = e.name === "TimeoutError" ? "timeout" : "erro de conexão";
    }
  }
  return res.status(502).json({ erro: ultimoErro || "falha ao consultar o IBGE" });
};
