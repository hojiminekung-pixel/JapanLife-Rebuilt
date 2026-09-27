# World Life — Legacy Resource Delivery

Supabase Edge Function `legacy-resource` is deployed for controlled binary resource delivery.

GET `/functions/v1/legacy-resource?name=<resource filename>`

The function reads enabled rows from `public.legacy_resource_objects`, returns raw bytes, content length, and `X-Resource-SHA256`. It returns 404 until a resource is uploaded and enabled.

Production patch delivery remains disabled until a known Master resource is uploaded and verified end-to-end.