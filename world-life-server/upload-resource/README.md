# World Life binary resource uploader

This uploader is intentionally separate from GitHub text-file APIs.

Usage on a machine that has the Master resource file:

```bash
export SUPABASE_URL="https://hgsugqaswxxkrsalvkci.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="YOUR_SERVICE_ROLE_KEY"
./upload-resource.sh /path/to/mapdata000.smf mapdata000.smf
```

The script uploads the bytes directly to the private Supabase Storage bucket:
`world-life-resources/resources/<filename>`.

It computes SHA-256 locally before upload and verifies the stored object with a download afterwards.

Never commit the service-role key.
