const SUPABASE_URL = "https://hgsugqaswxxkrsalvkci.supabase.co";
const LEGACY = "legacy-api-full";

export default {
  async fetch(request) {
    const u = new URL(request.url);

    if (request.method === "OPTIONS") return new Response(null, {status:204, headers:cors()});

    if (u.pathname === "/health") {
      return json({ok:true,server:"World-Life-Server",proxy:"wl",status:"online"});
    }

    if (u.pathname === "/patch/patch.bin") {
      return fetch(SUPABASE_URL + "/functions/v1/legacy-api-full/patch.bin");
    }

    if (u.pathname === "/resource") {
      return fetch(SUPABASE_URL + "/functions/v1/legacy-api-full/resource");
    }

    if (u.pathname.startsWith("/resource/")) {
      const name = decodeURIComponent(u.pathname.slice("/resource/".length));
      if (!/^[A-Za-z0-9._-]+\.smf$/.test(name))
        return new Response("Invalid resource name",{status:400,headers:cors()});
      // Forward to the server resource endpoint so server-side map transformations
      // (including mapdata000.smf) remain identical through both direct and gateway paths.
      return fetch(SUPABASE_URL + "/functions/v1/legacy-api-full/resource/" + encodeURIComponent(name));
    }

    // Master-compatible JSON API: preserve every path and query string.
    const target = SUPABASE_URL + "/functions/v1/" + LEGACY + u.pathname + u.search;
    const h = new Headers(request.headers);
    h.set("X-World-Life-Server","1");
    const r = await fetch(target,{method:request.method,headers:h,body:["GET","HEAD"].includes(request.method)?undefined:request.body});
    const rh = new Headers(r.headers);
    for (const [k,v] of Object.entries(cors())) rh.set(k,v);
    return new Response(r.body,{status:r.status,headers:rh});
  }
};

function cors(){return {"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"*","Access-Control-Allow-Methods":"GET,HEAD,POST,PUT,PATCH,DELETE,OPTIONS"};}
function json(v){return new Response(JSON.stringify(v),{status:200,headers:{...cors(),"Content-Type":"application/json; charset=utf-8"}});}
