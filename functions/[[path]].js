export async function onRequest(context) {
  const incoming = new URL(context.request.url);

  if (incoming.pathname === "/android/BeeGameLauncher.html") {
    return new Response(
      '<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body></body></html>',
      {
        status: 200,
        headers: {
          "content-type": "text/html; charset=utf-8",
          "cache-control": "no-store",
          "access-control-allow-origin": "*"
        }
      }
    );
  }

  const upstream = new URL(
    "https://worldlife-gateway.bomsronthai.workers.dev" +
      incoming.pathname +
      incoming.search
  );

  const headers = new Headers(context.request.headers);
  headers.delete("host");

  return fetch(upstream, {
    method: context.request.method,
    headers,
    body:
      context.request.method === "GET" || context.request.method === "HEAD"
        ? undefined
        : context.request.body,
    redirect: "follow",
  });
}

// World Life compatibility route active.
// Launcher DNS-safe route.
