# ChromaDB advisory assessment

Checked 2026-11-16 against the locked `chromadb==1.5.9` source and the primary
sources below. This records application-level mitigations, not a patched
dependency or a blanket acceptance of the Socket alerts.

| Advisory | Reported entry point | Release status checked |
|---|---|---|
| [CVE-2026-45829 / GHSA-f4j7-r4q5-qw2c](https://github.com/advisories/GHSA-f4j7-r4q5-qw2c) | Python server collection creation accepts model configuration with `trust_remote_code` | 1.5.9 is affected; no patched version listed |
| [CVE-2026-45833 / GHSA-36p7-vc44-83pf](https://github.com/advisories/GHSA-36p7-vc44-83pf) | Collection update accepts malicious model configuration | 1.5.9 is affected; no patched version listed |

[Upstream issue 6717](https://github.com/chroma-core/chroma/issues/6717) also
describes client-side execution when a stored embedding configuration is loaded.
[Upstream PR 7237](https://github.com/chroma-core/chroma/pull/7237) was merged,
but that alone does not establish a fixed published package or resolve both
advisories. Do not install an arbitrary development revision or suppress the
alerts to make a check green.

## Application boundary

- SlideRAG uses an embedded `PersistentClient`; it does not run the Chroma Python
  HTTP server, mount its collection routes, or accept collection configurations
  from HTTP requests or document text. The container starts only our FastAPI app.
- Embeddings are computed by the explicitly injected application client. Stored
  embedding functions are not part of the supported index format.
- `app/rag.py` validates `collection.configuration_json` directly. It must not
  read `collection.configuration`, which constructs embedding functions in the
  locked Chroma implementation. A non-null configuration other than the inert
  `{"type": "legacy"}` marker is rejected before construction.
- A temporary or operator-owned `DATA_DIR` is required. Do not import untrusted
  Chroma databases, share a writable root with another process, or expose a Chroma
  server. Local filesystem write access is not made safe by the JSON guard.
- The locked environment does not include `sentence-transformers`, `transformers`
  or `torch`. This is an additional constraint, not the primary defense.

## Verification and remaining work

The offline regression
`test_stored_embedding_configuration_is_rejected_without_deserialization`
uses an inert collection double whose deserializing property fails if accessed.
It verifies rejection without executing model code or contacting a provider.
The existing fresh-process persistence test verifies the supported embedded
path. Neither test is a penetration test or proof that Chroma itself is fixed.

The package remains advisory-affected. Keep the alerts visible. Before deployment
and each Chroma upgrade, re-check both advisories, the released fix status and
these source-level assumptions. Repeat the regression and persistence checks;
verify that no Chroma server or user-controlled embedding configuration has been
introduced. Changes to these boundaries require a new assessment. M1 live OpenAI
proof and all M4 operational evidence remain separate, unperformed gates.
