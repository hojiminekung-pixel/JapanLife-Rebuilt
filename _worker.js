const S="https://hgsugqaswxxkrsalvkci.supabase.co";
const API=S+"/functions/v1/legacy-api-full";
const RES=S+"/functions/v1/legacy-resource";
const C={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"*","Access-Control-Allow-Methods":"GET,HEAD,POST,PUT,PATCH,DELETE,OPTIONS"};
function H(h=new Headers()){for(const[k,v]of Object.entries(C))h.set(k,v);return h}
async function F(req){
  const u=new URL(req.url),p=u.pathname;
  if(req.method==="OPTIONS")return new Response(null,{status:204,headers:H()});
  if(p==="/health")return new Response(JSON.stringify({ok:true,server:"World-Life-Server",status:"online",revision:"pages-legacy-1"}),{headers:H(new Headers({"content-type":"application/json"}))});
  if(p==="/patch.bin"||p==="/patch/patch.bin")return fetch(API+"/patch.bin"+u.search);
  if(p==="/resource")return fetch(RES+"?name=font.smf");
  if(p.startsWith("/resource/")){
    const n=decodeURIComponent(p.slice(10));
    if(!/^[A-Za-z0-9._-]+\.smf$/.test(n))return new Response("Invalid resource name",{status:400,headers:H()});
    return fetch(RES+"?name="+encodeURIComponent(n));
  }
  const h=new Headers(req.headers);h.set("X-World-Life-Server","1");
  const r=await fetch(API+p+u.search,{method:req.method,headers:h,body:["GET","HEAD"].includes(req.method)?undefined:req.body});
  return new Response(r.body,{status:r.status,headers:H(new Headers(r.headers))});
}
export default{fetch:F};