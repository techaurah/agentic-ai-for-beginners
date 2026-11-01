# Solution 27: Put a key on the door

**The change (`server.py`).** Twelve lines at the top of `do_POST`, after the route check and before the body is read. The expected key is read from `CLINIC_API_KEY` on every request (cheap, and it means rotating the key is a restart, not a redeploy). A missing or wrong `X-API-Key` header gets a 401 with a JSON error and a log line that says 401, so the Lesson 28 habit applies: the rejection is observable, not silent.

Verified behaviour, with the key set: `GET /health` answers 200 with no key, `POST /chat` answers 401 with no key and 401 with a wrong key, and 200 with a real reply when the key matches. Restarted without the variable, `/chat` answers with no key again.

**Why /health stays open.** The health endpoint is a contract with the platform, not with users. Probes do not carry your key; a 401 there reads as "dead service" and the platform restarts you in a loop. Lock the endpoints that hold data or spend money. Leave the heartbeat public, and make sure the heartbeat reveals nothing worth stealing (ours returns a status and a version, which is the right amount).

**Why the Dockerfile does not change.** The image's job is to carry code and defaults. Secret values are injected by whoever runs the container: a compose file, a platform secret store, a CI variable. Putting the real key in the Dockerfile would bake it into every copy of the image forever, which is the one place a secret must never be. `ENV` in the lesson's Dockerfile sets non-secret defaults (host, port). Keys are a different species.

An API key is the floor, not the ceiling: it identifies a calling system, not a person, and it does nothing about rate limits or abuse from a leaked key. It is, however, the correct first lock, and it costs twelve lines.
