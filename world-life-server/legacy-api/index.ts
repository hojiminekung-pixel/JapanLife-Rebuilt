import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

const db = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
);

const headers = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET,POST,OPTIONS",
  "access-control-allow-headers": "content-type,authorization",
};

const response = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers });

const envelope = (payload: unknown) => [0, payload];

async function sha256(text: string) {
  const bytes = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(text),
  );
  return [...new Uint8Array(bytes)]
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

async function readParams(req: Request) {
  const out: Record<string, string> = {};
  const url = new URL(req.url);
  url.searchParams.forEach((value, key) => (out[key] = value));

  if (req.method !== "POST") return out;

  const contentType = req.headers.get("content-type") ?? "";

  if (contentType.includes("application/x-www-form-urlencoded")) {
    const form = new URLSearchParams(await req.text());
    form.forEach((value, key) => (out[key] = value));
  } else if (contentType.includes("application/json")) {
    try {
      const body = await req.json();
      if (body && typeof body === "object") {
        for (const [key, value] of Object.entries(body)) {
          out[key] = value == null ? "" : String(value);
        }
      }
    } catch {
      // Legacy clients may send an empty body.
    }
  }

  return out;
}

async function findAccount(params: Record<string, string>) {
  const gameId = params.user_id || params.game_id || "";
  const device = params.device_info || params.udid || params.telephony_id || "";

  if (gameId) {
    const { data } = await db
      .from("legacy_game_accounts")
      .select("*")
      .eq("game_id", gameId)
      .maybeSingle();
    if (data) return data;
  }

  if (device) {
    const hash = await sha256(device);
    const { data } = await db
      .from("legacy_game_accounts")
      .select("*")
      .eq("udid_hash", hash)
      .maybeSingle();
    if (data) return data;
  }

  return null;
}

async function upsertAccount(params: Record<string, string>) {
  const gameId = params.user_id || params.game_id || "";
  if (!gameId) return null;

  const device = params.device_info || params.udid || params.telephony_id || "";
  const row: Record<string, unknown> = {
    game_id: gameId,
    status: "active",
    updated_at: new Date().toISOString(),
    last_login_at: new Date().toISOString(),
  };

  if (device) row.udid_hash = await sha256(device);
  if (params.password) row.password_hash = params.password;
  if (params.game_version) row.client_version = params.game_version;

  const { data, error } = await db
    .from("legacy_game_accounts")
    .upsert(row, { onConflict: "game_id" })
    .select("*")
    .single();

  if (error) throw error;
  return data;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers });
  }

  const url = new URL(req.url);
  const path =
    url.pathname.replace(/^\/functions\/v1\/legacy-api/, "") || "/";
  const params = await readParams(req);

  try {
    if (path === "/" || path === "/health") {
      return response({
        service: "World Life Server",
        api: "legacy-v1",
        status: "ready",
        game: "World Life",
        patch_enabled: false,
      });
    }

    if (path === "/json/util/version_check") {
      return response(
        envelope({
          major: "1",
          minor: "5",
          client_version: params.game_version || "",
          maintenance: false,
        }),
      );
    }

    if (path === "/json/get/get_setting") {
      const defaults = [
        ["get_user_rotate", "0"],
        ["get_game_data_rotate", "0"],
        ["temple_energy_chance", "0"],
        ["random_energy_chance", "0"],
        ["exp_gain_2_chance", "0"],
        ["exp_gain_3_chance", "0"],
        ["post_timeout", "30"],
        ["server_unix_datatime", String(Math.floor(Date.now() / 1000))],
        ["monggi_chance", "0"],
      ];

      const { data } = await db
        .from("legacy_server_settings")
        .select("key,value_json");

      const settings = new Map(defaults);
      for (const row of data ?? []) {
        settings.set(
          row.key,
          typeof row.value_json === "string"
            ? row.value_json
            : JSON.stringify(row.value_json),
        );
      }

      return response(
        envelope(
          [...settings].map(([name, value]) => ({ name, value })),
        ),
      );
    }

    if (path === "/json/move/set_password") {
      const account = await upsertAccount(params);
      if (!account) {
        return response(
          envelope({ ok: false, error: "missing user_id" }),
          400,
        );
      }

      return response(
        envelope({
          ok: true,
          user_id: account.game_id,
          status: account.status,
          new_device_id: account.game_id,
        }),
      );
    }

    if (path === "/json/get/get_user_id") {
      const account = await findAccount(params);
      return response(
        envelope({
          user_id: account?.game_id || "",
          found: Boolean(account),
        }),
      );
    }

    if (path === "/json/get/get_user") {
      const account = await findAccount(params);
      return response(
        envelope({
          user_detail: {
            user_id: account?.game_id || params.user_id || "",
            status: account?.status || "active",
            client_version:
              account?.client_version || params.game_version || "",
          },
        }),
      );
    }

    if (
      path === "/json/save/save_user" ||
      path === "/json/save/save_user_frequent"
    ) {
      const account = await findAccount(params);
      if (account) {
        await db
          .from("legacy_game_accounts")
          .update({
            client_version:
              params.game_version || account.client_version,
            updated_at: new Date().toISOString(),
          })
          .eq("id", account.id);
      }
      return response(envelope({ ok: true }));
    }

    if (path === "/json/save/save_version") {
      const account = await findAccount(params);
      if (account) {
        await db
          .from("legacy_game_accounts")
          .update({
            client_version:
              params.version || params.game_version || account.client_version,
            updated_at: new Date().toISOString(),
          })
          .eq("id", account.id);
      }
      return response(envelope({ ok: true }));
    }

    if (path === "/json/get/get_game_data_url") {
      // Deliberately empty until the recovered 44.8 MB Master resource
      // package is hosted and checksum-compatible.
      return response(
        envelope({
          dl_id: "",
          dl_path: "",
          dl_size: 0,
          response_checksum: "",
          map_size: 0,
        }),
      );
    }

    if (path === "/json/save/save_udid_migration") {
      return response(envelope({ ok: true }));
    }

    if (path === "/json/rollback/get_game_data") {
      return response(
        envelope({ ok: false, error: "rollback_disabled" }),
      );
    }

    return response(
      envelope({
        ok: false,
        error: "endpoint_not_implemented",
        path,
      }),
      404,
    );
  } catch (error) {
    return response(
      envelope({
        ok: false,
        error: "server_error",
        message: error instanceof Error ? error.message : String(error),
      }),
      500,
    );
  }
});
