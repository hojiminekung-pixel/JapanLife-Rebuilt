// World Life Legacy Compatibility Gateway
// Preserves the Master client's legacy protocol surface.
// No /game/* or /shop-api/* protocol is introduced here.
const S = "https://hgsugqaswxxkrsalvkci.supabase.co";
const API = S + "/functions/v1/legacy-api-full";
const MAN = S + "/functions/v1/world-life-resource-manifest";
const RES = S + "/storage/v1/object/public/world-life-resources/";
const C = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET,HEAD,POST,PUT,PATCH,DELETE,OPTIONS",
  "Access-Control-Allow-Headers": "*"
};

function headers(h = new Headers()) {
  for (const [k, v] of Object.entries(C)) h.set(k, v);
  return h;
}
function json(value, status = 200) {
  return new Response(JSON.stringify(value), {
    status,
    headers: headers(new Headers({"content-type": "application/json; charset=utf-8"}))
  });
}
async function proxy(request, target) {
  const h = new Headers(request.headers);
  h.delete("host");
  h.delete("content-length");
  const response = await fetch(new Request(target, {
    method: request.method,
    headers: h,
    body: ["GET", "HEAD"].includes(request.method) ? undefined : request.body,
    redirect: "follow"
  }));
  return new Response(response.body, {
    status: response.status,
    headers: headers(new Headers(response.headers))
  });
}
function validResource(name) {
  return /^[A-Za-z0-9._-]+\.smf$/.test(name);
}

async function handle(request) {
  const url = new URL(request.url);
  const path = url.pathname;

  if (request.method === "OPTIONS") {
    return new Response(null, {status: 204, headers: headers()});
  }

  if (path === "/" || path === "/health") {
    return json({
      ok: true,
      server: "World-Life-Server",
      protocol: "legacy",
      status: "online",
      routes: [
        "/json/*",
        "/japanlife/v1_5_7/patch.bin",
        "/resource",
        "/resource/<name>"
      ]
    });
  }

  if (path === "/resource") {
    return proxy(request, MAN);
  }

  if (path.startsWith("/resource/")) {
    const name = decodeURIComponent(path.slice("/resource/".length));
    if (!validResource(name)) {
      return new Response("Invalid resource name", {status: 400, headers: headers()});
    }
    return proxy(request, RES + encodeURIComponent(name));
  }

  if (path === "/japanlife/v1_5_7/patch.bin" || path === "/patch.bin") {
    return proxy(request, API + "/patch.bin" + url.search);
  }

  if (path.startsWith("/japanlife/v1_5_7/")) {
    const name = decodeURIComponent(path.slice("/japanlife/v1_5_7/".length));
    if (validResource(name)) {
      return proxy(request, RES + encodeURIComponent(name));
    }
  }

  if (path === "/json" || path.startsWith("/json/")) {
    return proxy(request, API + path.slice("/json".length) + url.search);
  }

  if (path.startsWith("/legacy/")) {
    return proxy(request, API + "/" + path.slice("/legacy/".length) + url.search);
  }

  if (
    path.startsWith("/get/") ||
    path.startsWith("/save/") ||
    path.startsWith("/util/") ||
    path.startsWith("/shop/") ||
    path.startsWith("/rollback/") ||
    path === "/devices"
  ) {
    return proxy(request, API + path + url.search);
  }

  return json({error: "legacy_route_not_found"}, 404);
}

export default {fetch: handle};
