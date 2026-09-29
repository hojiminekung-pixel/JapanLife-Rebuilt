const SUPABASE_URL = "https://hgsugqaswxxkrsalvkci.supabase.co";
const FUNCTION_NAME = "legacy-api-full";

const EMPTY_MANIFEST = {
  protocol: "world-life-resource-v1",
  game: "world-life",
  server_version: "0.1.0",
  status: "development",
  resources: []
};

export default {
  async fetch(request) {
    const incoming = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: corsHeaders()
      });
    }

    if (incoming.pathname === "/" || incoming.pathname === "/health") {
      return json({
        ok: true,
        server: "World-Life-Server",
        proxy: "world-life-api",
        status: "online"
      });
    }

    // Resource manifest used by the rebuilt World Life client.
    // Keep this endpoint stable while the real resource manifest is finalized.
    if (incoming.pathname === "/resource") {
      return json(EMPTY_MANIFEST);
    }

    // Compatibility gateway for the legacy JSON path.
    const target =
      SUPABASE_URL +
      "/functions/v1/" +
      FUNCTION_NAME +
      incoming.pathname +
      incoming.search;

    const headers = new Headers(request.headers);
    headers.set("X-World-Life-Server", "1");

    const response = await fetch(target, {
      method: request.method,
      headers,
      body:
        request.method === "GET" || request.method === "HEAD"
          ? undefined
          : request.body
    });

    const responseHeaders = new Headers(response.headers);
    for (const [key, value] of Object.entries(corsHeaders())) {
      responseHeaders.set(key, value);
    }

    return new Response(response.body, {
      status: response.status,
      headers: responseHeaders
    });
  }
};

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "GET,HEAD,POST,PUT,PATCH,DELETE,OPTIONS",
    "Cache-Control": "no-store"
  };
}

function json(value) {
  return new Response(JSON.stringify(value), {
    status: 200,
    headers: {
      ...corsHeaders(),
      "Content-Type": "application/json; charset=utf-8"
    }
  });
}
