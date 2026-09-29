const SUPABASE_URL = "https://hgsugqaswxxkrsalvkci.supabase.co";
const FUNCTION_NAME = "legacy-api-full";
const MANIFEST_FUNCTION = "world-life-resource-manifest";

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

    if (incoming.pathname === "/resource") {
      const manifestResponse = await fetch(
        SUPABASE_URL + "/functions/v1/" + MANIFEST_FUNCTION
      );

      return new Response(await manifestResponse.text(), {
        status: manifestResponse.status,
        headers: {
          ...corsHeaders(),
          "Content-Type": "application/json; charset=utf-8"
        }
      });
    }

    if (incoming.pathname.startsWith("/resource/")) {
      const name = decodeURIComponent(
        incoming.pathname.substring("/resource/".length)
      );

      if (!/^[A-Za-z0-9._-]+\.smf$/.test(name)) {
        return new Response("Invalid resource name", {
          status: 400,
          headers: corsHeaders()
        });
      }

      const storageUrl =
        SUPABASE_URL +
        "/storage/v1/object/public/world-life-resources/" +
        encodeURIComponent(name);

      const resourceResponse = await fetch(storageUrl);
      const headers = new Headers(resourceResponse.headers);
      headers.set("Access-Control-Allow-Origin", "*");
      headers.set("Cache-Control", "public, max-age=86400");

      return new Response(resourceResponse.body, {
        status: resourceResponse.status,
        headers
      });
    }

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
    "Access-Control-Allow-Methods": "GET,HEAD,POST,PUT,PATCH,DELETE,OPTIONS"
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
