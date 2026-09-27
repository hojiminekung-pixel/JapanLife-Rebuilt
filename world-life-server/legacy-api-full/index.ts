import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

const url = Deno.env.get("SUPABASE_URL")!;
const key = Deno.env.get("SUPABASE_ANON_KEY")!;
const db = createClient(url, key);
const H = {"content-type":"application/json; charset=utf-8","cache-control":"no-store","access-control-allow-origin":"*","access-control-allow-methods":"GET,POST,OPTIONS","access-control-allow-headers":"content-type,authorization"};
const out=(x:unknown,s=200)=>new Response(JSON.stringify(x),{status:s,headers:H});
const env=(x:unknown)=>x==null?"":String(x);
const pack=(x:unknown)=>[0,x];

async function params(req:Request){
  const o:Record<string,string>={};
  const u=new URL(req.url);
  u.searchParams.forEach((v,k)=>o[k]=v);
  if(req.method==="POST"){
    const c=req.headers.get("content-type")||"";
    if(c.includes("application/x-www-form-urlencoded")){
      const q=new URLSearchParams(await req.text()); q.forEach((v,k)=>o[k]=v);
    } else if(c.includes("application/json")){
      try{const b=await req.json(); for(const[k,v] of Object.entries(b||{})) o[k]=env(v)}catch{}
    }
  }
  return o;
}

async function hash(s:string){
  const b=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(s));
  return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,"0")).join("");
}

async function getAccount(p:Record<string,string>){
  const gid=p.user_id||p.game_id||"";
  const device=p.device_info||p.udid||p.telephony_id||"";
  const uh=device?await hash(device):"";
  const {data,error}=await db.rpc("legacy_get_account",{p_game_id:gid,p_udid_hash:uh});
  if(error) throw error;
  return data?.[0]||null;
}

Deno.serve(async req=>{
  if(req.method==="OPTIONS")return new Response(null,{status:204,headers:H});
  const u=new URL(req.url);
  const path=u.pathname.replace(/^\/functions\/v1\/legacy-api-full/,"")||"/";
  const p=await params(req);
  try{
    if(path==="/"||path==="/health") return out({service:"World Life Server",api:"legacy-v1",status:"ready",game:"World Life",patch_enabled:false});
    if(path==="/json/util/version_check") return out(pack({major:"1",minor:"5",maintenance:false,client_version:p.game_version||""}));
    if(path==="/json/get/get_setting") return out(pack([
      {name:"get_user_rotate",value:"0"},
      {name:"get_game_data_rotate",value:"0"},
      {name:"temple_energy_chance",value:"0"},
      {name:"random_energy_chance",value:"0"},
      {name:"exp_gain_2_chance",value:"0"},
      {name:"exp_gain_3_chance",value:"0"},
      {name:"post_timeout",value:"30"},
      {name:"server_unix_datatime",value:String(Math.floor(Date.now()/1000))},
      {name:"monggi_chance",value:"0"}
    ]));
    if(path==="/json/get/get_user_id"){
      const a=await getAccount(p);
      return out(pack({user_id:a?.game_id||"",found:!!a}));
    }
    if(path==="/json/get/get_user"){
      const a=await getAccount(p);
      return out(pack({user_detail:{user_id:a?.game_id||p.user_id||"",status:a?.status||"active",client_version:a?.client_version||p.game_version||""}}));
    }
    if(path==="/json/move/set_password"){
      const gid=p.user_id||p.game_id||"";
      const device=p.device_info||p.udid||p.telephony_id||"";
      const uh=device?await hash(device):"";
      const {data,error}=await db.rpc("legacy_upsert_account",{p_game_id:gid,p_udid_hash:uh,p_password_hash:p.password||"",p_client_version:p.game_version||""});
      if(error)throw error;
      const a=data?.[0];
      return out(pack({ok:!!a,user_id:a?.game_id||gid,status:a?.status||"active",new_device_id:a?.game_id||gid}));
    }
    if(path==="/json/get/get_game_data_url") return out(pack({dl_id:"",dl_path:"",dl_size:0,response_checksum:"",map_size:0}));
    if(path==="/json/save/save_user"||path==="/json/save/save_user_frequent"||path==="/json/save/save_version"||path==="/json/save/save_udid_migration") return out(pack({ok:true}));
    if(path==="/json/rollback/get_game_data") return out(pack({ok:false,error:"rollback_disabled"}));
    return out(pack({ok:false,error:"endpoint_not_implemented",path}),404);
  }catch(e){
    return out(pack({ok:false,error:"server_error",message:e instanceof Error?e.message:String(e)}),500);
  }
});