export async function onRequest(context) {
  const incoming = new URL(context.request.url);
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
