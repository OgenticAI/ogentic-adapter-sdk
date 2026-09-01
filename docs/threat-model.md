# Threat Model — Adapter Configuration

This document describes the security guarantees enforced by ogentic-adapter-sdk at adapter construction time.

## Threat 1: Base URL Exfiltration

### The Threat

When configuring an adapter with a custom `base_url` (e.g., for a self-hosted or proxy endpoint), a typo, misconfiguration, or supply-chain attack could redirect LLM traffic—including prompts, completions, and any credentials passed with the request—to an attacker-controlled server.

**Example:** An operator intends to route to their corporate proxy at `api.internal.company.com` but misconfigures it as `api.openai.com.evil.invalid`. Without validation, the SDK silently sends all requests to the attacker's server.

### The Mitigation: Allow-List

The adapter SDK enforces an **allow-list of permitted hosts** at adapter construction time. If a `base_url` host is not on the allow-list, construction **fails loudly** with an `AdapterConfigError` before any network request is attempted.

**Default allow-list:**
- OpenAI: `api.openai.com`
- Anthropic: `api.anthropic.com`
- (Other providers: provider-specific defaults, to be documented per adapter)

### Extending the Allow-List

To use a self-hosted or proxy endpoint, the operator sets environment variables to extend the allow-list:

- `OGENTIC_ROUTER_ALLOWED_OPENAI_HOSTS` — comma-separated additional hosts for OpenAI adapter
- `OGENTIC_ROUTER_ALLOWED_ANTHROPIC_HOSTS` — comma-separated additional hosts for Anthropic adapter
- (Per-provider pattern continues for other adapters)

**Example:**
```bash
export OGENTIC_ROUTER_ALLOWED_OPENAI_HOSTS="api.internal.company.com,openai-proxy.k8s.local"
```

These values are **additive** to the defaults — they do not replace the default allow-list.

**What does NOT happen:**
- Allow-list is not retrieved from a config file at runtime (immutable at adapter construction time).
- Allow-list cannot be modified after adapter construction.
- No wildcard or regex patterns — exact hostname matching only.

### Check Ordering

The allow-list check runs **before** any optional provider SDK is imported or instantiated. This means:

1. Adapter configuration is validated (`_validate_host()` is called)
2. If the host is not allowed, construction fails with `AdapterConfigError`
3. **Only if validation passes**, the optional provider SDK (e.g., `from openai import AsyncOpenAI`) is imported
4. Only then is an actual client instantiated

This ordering ensures that a disallowed `base_url` is rejected before any provider-specific code can execute, closing off code-injection or information-disclosure attacks that might be hidden in provider SDK internals.

---

## Threat 2: Loopback-Only Guarantee for Local Adapters

### The Threat

When using a local LLM adapter (e.g., Ollama), misconfiguration could point the adapter at an attacker-controlled server on the internal network (e.g., `10.0.0.50`, `192.168.1.100`, or `ollama.internal`). Without validation, the SDK could send traffic to an attacker-controlled endpoint masquerading as a local service.

**Example:** An operator intends to connect to their local Ollama instance at `localhost:11434` but mistakenly sets `base_url` to `ollama.internal`, which resolves to a compromised machine on the corporate network.

### The Mitigation: Loopback-Only Allow-List

The adapter SDK enforces that local adapters **only accept loopback addresses**. If a local adapter's `base_url` resolves to a non-loopback host, construction fails with a `LocalhostOnlyError` before any network request is attempted.

**Accepted loopback hosts (exact literal match):**
- `localhost`
- `127.0.0.1`
- `::1` (IPv6 loopback, unbracketed)
- `[::1]` (IPv6 loopback, bracketed for port-inclusive URLs)

**Note:** The check matches these literals exactly. DNS resolution to a loopback address (e.g., a hostname that resolves to `127.0.0.1`) is **not** accepted — only the literal strings above are allowed.

### Check Ordering

Like the base_url allow-list check, the loopback-only check runs **before** any optional provider SDK is imported. The ordering is:

1. Adapter configuration is validated (`_validate_localhost()` is called)
2. If the host is not loopback-only, construction fails with `LocalhostOnlyError`
3. **Only if validation passes**, provider SDK imports and instantiation proceed

### Port Considerations

The loopback check validates **hostname only**. Port numbers are not validated by this check (that is the responsibility of the local service itself to respond or reject).

---

## What These Checks Do NOT Protect Against

### Out of Scope

1. **DNS Rebinding Attacks:** If a hostname initially resolves to an allowed host but later re-resolves to a different IP during connection, this check cannot catch that. The check validates the initial configuration only; runtime DNS changes are outside this scope.

2. **SSRF via Redirects:** If an allowed endpoint responds with an HTTP redirect to a disallowed host, this check does not re-validate the redirect target. Redirect handling is the responsibility of the HTTP client library.

3. **Compromised Loopback Process:** If a malicious process on the same host is listening on `127.0.0.1:11434` (or any loopback port), this check cannot distinguish it from a legitimate local service. Loopback-only guarantee assumes the local machine itself is trusted.

4. **Multi-Tenant Isolation:** The adapter SDK itself has no tenant concept. If a downstream service (e.g., ogentic-router) layers multi-tenant configuration on top of this SDK, that service is responsible for enforcing tenant-scoped allow-lists. This SDK's checks do not provide tenant isolation.

5. **TLS/Certificate Validation:** These checks do not validate TLS certificates or hostnames. That is the responsibility of the underlying HTTP client and TLS libraries.

---

## Implementation Notes

### Source of Truth

The `_localhost` check logic (the function and constants) is a **verbatim port** of the corresponding check in [ogentic-shield](https://github.com/OgenticAI/ogentic-shield), specifically the `llm_client.py` implementation. This ensures consistency across the OgenticAI ecosystem: the same security boundary is enforced whether you use Shield directly or the Adapter SDK.

**Important:** The `_localhost` implementation in this SDK **must not drift** from the Shield version. Any update to Shield's loopback validation must be back-ported here, and any future change to this SDK's implementation must be synchronized back into Shield. Code review and CI discipline are required to prevent divergence.

### Failure Modes

- **Allow-list validation failure:** Raises `AdapterConfigError` with a message that includes (a) the disallowed host, (b) the reason (not in allow-list), and (c) how to fix it (set env var or use default endpoint).
- **Loopback-only validation failure:** Raises `LocalhostOnlyError` with a message that includes (a) the non-loopback host, (b) the accepted loopback set, and (c) how to fix it.

Both errors are raised **at adapter construction time** (not at first request), so operators catch configuration errors immediately during application startup or in CI/CD validation pipelines.

---

## References

- [ogentic-router adapters/_allowlist.py](https://github.com/OgenticAI/ogentic-router) — current implementation of allow-list enforcement
- [ogentic-router adapters/_localhost.py](https://github.com/OgenticAI/ogentic-router) — current implementation of loopback-only check
- [ogentic-shield llm_client.py](https://github.com/OgenticAI/ogentic-shield) — original loopback-only check (source of truth for _localhost.py)
