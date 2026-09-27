# World Life Server — Auth + Legacy Server Status

## Supabase project
Project: World-Life-Server
Project ref: hgsugqaswxxkrsalvkci
Region: ap-southeast-1

## Authentication

Active Edge Functions:
- send-auth-email v6
- approval-action v7
- auth-portal v1

The Send Email Hook uses Standard Webhooks verification. Only signature failures return HTTP 401. Valid hook processing returns HTTP 200; delivery/internal failures return HTTP 500.

The signup flow:
1. Supabase Auth creates the user.
2. send-auth-email upserts profiles with status=pending.
3. It constructs the confirmation URL from token_hash, redirect_to and the project Auth verify endpoint.
4. It creates one approve and one reject request for each configured owner.
5. Owner approval changes profiles.status to approved; rejection changes it to rejected.

A previous test account currently exists in profiles with pending status and no approval request. This is a stale pre-v6 test state and is not used as proof of the current hook behavior. A fresh signup is required to exercise the new signup hook path.

## Legacy game server foundation

Created tables:
- legacy_game_accounts
- legacy_server_settings

Initial server settings:
- game: World Life / 0.1
- API contract: legacy-v1
- patch: disabled until exact patch contract and binary hosting are verified

The original Master still points to the historical japanlife.nubee.com/json/ service. The APK has NOT been retargeted to the new server yet.

## Native legacy API contract already recovered

Critical endpoints:
- util/version_check
- get/get_game_data_url
- get/get_user_id
- get/get_user
- save/save_user
- move/set_password
- save/save_version
- get/get_setting

Important native request fields recovered include:
- udid
- udid_faker_flag
- os_version
- game_version
- password
- device_token
- device_type
- model
- display_size
- timezone
- telephony_id
- lang

The exact response schemas and patch binary contract must be recovered before the client URL is changed.

## Rule

Never point the verified World Life 0.1 APK at a partially implemented legacy server. First complete the compatibility endpoints and binary data hosting, then build a separate server-test APK.