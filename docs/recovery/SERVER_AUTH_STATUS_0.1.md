# World Life Server — Authentication/Server Status

Project: World-Life-Server
Target game version: 0.1

## Current database

Core tables already exist:
- profiles
- approval_requests
- legacy_game_accounts
- legacy_server_settings
- legacy_resource_manifest
- legacy_resource_objects
- patch_releases

The server settings already identify the game as World Life 0.1 and resource delivery as Supabase Storage.

## Authentication design

Target flow:
Email/Gmail signup -> email verification -> profile status pending -> owner review -> approved/rejected -> approved player can use the game service.

The old social-login integration remains backed up in the APK until the email path is proven end-to-end. It must not be deleted first.

## Hardening completed

- approval_requests now has status, decided_by and decided_at fields.
- Approval/rejection database functions were aligned with profile_id/status.
- Public/authenticated EXECUTE was revoked from legacy_get_account and legacy_upsert_account.
- Public authenticated EXECUTE was revoked from approve_user/reject_user; service_role remains available for controlled server-side use.
- approval-action Edge Function was updated to mark requests approved/rejected/expired and prevent replay.

## Remaining production gate

1. Confirm the owner account is actually present and approved in profiles.
2. Run a real signup with a test email.
3. Confirm verification email arrives.
4. Confirm the new profile is pending.
5. Confirm owner receives the approval message.
6. Click approve.
7. Confirm profile becomes approved.
8. Sign in again.
9. Only after this passes should the APK's old social-login UI be removed from the live client.

## Important

The native client still contains legacy social-login symbols. This is intentional until the replacement path is proven.
