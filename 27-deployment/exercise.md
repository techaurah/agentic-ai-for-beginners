# Exercise 27: Put a key on the door

The lesson's service answers anyone who can reach the port. That is fine on your laptop and careless on a server. Add the smallest real access control: an API key on the chat endpoint, configured the way the lesson taught you to configure everything, from the environment.

Work in copies: `my_server.py` (keep `agent.py` as it is; your server imports it).

1. **Require a key on POST /chat.** When the environment variable `CLINIC_API_KEY` is set, a /chat request must carry the header `X-API-Key` with the same value. A missing or wrong key gets a 401 and a JSON error, and the log line records the 401. When the variable is not set, the service behaves exactly as before (local development stays frictionless; say so in a comment, because that default is a decision, not an oversight).

2. **Keep /health open.** Health checks come from the platform, which does not have your key. A 401 on /health would make the platform mark a healthy service as dead and restart it forever. The exercise is partly about knowing which door to lock.

3. **Prove it with requests.** Run your server with the key set and make four requests: /health without a key (200), /chat without a key (401), /chat with the wrong key (401), /chat with the right key (200 and a real reply). Then restart without the variable and show /chat answering with no key again.

Acceptance checks:
- All four keyed-mode responses match the list above, and the server log shows the two 401s.
- No key value appears anywhere in the code. It arrives from the environment or not at all.
- The Dockerfile needs no change. If you think it does, write down why in your solution notes; the interesting answer involves who injects environment variables at deploy time.

The worked solution is in `solution/`. Try it yourself first; the lesson is in the attempt.
