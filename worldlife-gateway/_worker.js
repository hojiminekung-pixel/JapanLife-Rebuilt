export default {
  async fetch(request, env) {
    const u = new URL(request.url);
    let p = u.pathname;

    if (p === "/x") p = "/";
    else if (p.startsWith("/x/")) p = p.slice(2);

    // Compatibility aliases used by the legacy World Life client.
    if (p.startsWith("/jxx/")) p = p.slice(4);
    if (p.startsWith("/maintxx/")) p = p.slice(8);
    if (p.startsWith("/savex/")) p = p.slice(6);
    if (p.startsWith("/cf/")) p = "/patch.bin";
    if (p.startsWith("/devices")) p = "/devices";

    const target = new URL("https://worldlife-gateway.bomsronthai.workers.dev");
    target.pathname = p || "/";
    target.search = u.search;

    const headers = new Headers(request.headers);
    headers.delete("host");

    const init = {
      method: request.method,
      headers,
      redirect: "follow"
    };

    if (request.method !== "GET" && request.method !== "HEAD") {
      init.body = request.body;
    }

    try {
      const upstream = await fetch(new Request(target, init));
      const out = new Headers(upstream.headers);
      out.set("Access-Control-Allow-Origin", "*");
      out.set("Access-Control-Allow-Methods", "GET,POST,PUT,PATCH,DELETE,OPTIONS");
      out.set("Access-Control-Allow-Headers", "content-type,authorization,x-worldlife-key,x-api-key");
      return new Response(upstream.body, {
        status: upstream.status,
        statusText: upstream.statusText,
        headers: out
      });
    } catch (e) {
      return new Response(JSON.stringify({
        ok: false,
        error: "upstream_fetch_failed",
        message: String(e)
      }), {
        status: 502,
        headers: {
          "content-type": "application/json; charset=utf-8",
          "Access-Control-Allow-Origin": "*"
        }
      });
    }
  }
};