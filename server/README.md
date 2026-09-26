# Japan Life Server

This directory defines the first server layer for the Japan Life rebuild.

## Roles

- OWNER: bomsronthai@gmail.com
- PLAYER: email/password account, email verified, then manually approved by OWNER.

## Security flow

1. User signs up with email/password.
2. Email confirmation is required.
3. A profile is created as `pending`.
4. The OWNER reviews the account.
5. OWNER changes status to `approved` or `rejected`.
6. Only approved users can read protected patch metadata.
7. Suspended users lose access.

Supabase Auth provides email/password authentication and JWT access tokens. Database Row Level Security (RLS) is used to enforce authorization.

## Patch layer

The legacy game contains a native Patch Manager and a legacy patch URL. We will keep the successful font APK unchanged while implementing the new server separately.

Planned endpoints:

- GET /patch/manifest.json
- GET /patch/patch.bin
- GET /patch/files/<path>
- GET /api/version
- authenticated patch metadata API

The exact legacy `patch.bin` container/hash format is still being reverse-engineered. Do not publish a fabricated `patch.bin` as a real game patch until its format is verified.

## Secrets

Never commit:

- Supabase secret/service keys
- SMTP passwords
- signing keys
- APK keystores
- production database passwords

Only public client configuration belongs in an Android client.
