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
- Chroma 1.5.9 stores embedding-function configs in two channels and builds them
  when `collection.configuration` or `collection.schema` is read (the schema is
  read on every upsert and on some query paths). Before that can happen,
  `open_store` reads both channels raw: `collection.configuration_json` and the
  library-private model field `collection._model.serialized_schema`. It walks
  every nested `embedding_function` entry (dense and sparse, `defaults` and
  `keys`) and accepts only absent, `null`, `{"type": "legacy"}` or
  `{"type": "unknown"}`, which are the nameless markers Chroma writes for our
  collection. Anything else, or a non-object document, raises
  `IndexMismatchError`. The guard fails closed and only reads: it does not reset,
  migrate or modify the collection.
- A temporary or operator-owned `DATA_DIR` is required. Do not import untrusted
  Chroma databases, share a writable root with another process, or expose a Chroma
  server. Local filesystem write access is not made safe by the JSON guard.
- The locked environment does not include `sentence-transformers`, `transformers`
  or `torch`. This is an additional constraint, not the primary defense.

## Verification and remaining work

`test_open_store_schema_embedding_function_refused_before_construction` creates
a real collection through `open_store`. It then stores a named function in the
raw schema (dense `#embedding` key, dense `defaults`, sparse `defaults`) and
reopens the collection in a fresh process with an inert spy registered under
that name. It asserts the refusal, zero spy calls and unchanged rows and records.
Against the previous configuration-only guard, the `defaults` cases fail, and
the following upload builds the spy. An untampered reopen-and-upsert test guards
against false positives. The double-based
`test_stored_embedding_configuration_is_rejected_without_deserialization` covers
the configuration channel.

Remaining limits:

- Both advisories are still unpatched upstream in 1.5.9. This is a mitigation,
  not a fixed dependency.
- The protection depends on the operator owning `DATA_DIR`.
- Any future read of `.configuration` or `.schema`, or a call to
  `similarity_search_with_relevance_scores` (LangChain reads `.configuration`),
  that runs before this guard would bypass it.
- The guard relies on a private model field. Other unknown deserialization paths
  in Chroma are not covered by tests.
- The spy tests prove that construction is refused, not resistance to a real
  payload. They are not penetration tests.

The package remains advisory-affected. Keep the alerts visible. Before deployment
and each Chroma upgrade, re-check both advisories, the released fix status and
these source-level assumptions. Repeat the regression and persistence checks;
verify that no Chroma server or user-controlled embedding configuration has been
introduced. Changes to these boundaries require a new assessment. M1 live OpenAI
proof and all M4 operational evidence remain separate, unperformed gates.
