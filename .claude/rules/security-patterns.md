# Security Patterns

> Vision principle: **Untrusted documents, defended boundaries.** SlideRAG Mini accepts user-uploaded PPTX files, sends their text to external embedding and chat APIs, and renders model output in a browser. Each of those boundaries needs validation, containment, and escaping.

These patterns are enforced on ALL code in this repository. Violations must be fixed before committing.

## Forbidden — never generate

- `eval()`, `exec()`, `compile()` with any user-controlled input
- `subprocess` calls with `shell=True` and user input
- Hardcoded secrets, API keys, passwords, or tokens — anywhere
- Credentials embedded in Git remote URLs (`https://user:token@…`) — use SSH keys or PATs in env
- `pickle.loads()` on untrusted data
- Logging of API keys, secrets, or full LLM prompts/responses (they contain document text)
- Path traversal via unsanitized `..` in file operations
- `verify=False` or disabling TLS verification on any HTTP client
- Plaintext `.env` files committed to git (the repo ships only `.env.example`)
- Baking `OPENAI_API_KEY` or any other secret into the Docker image
- Publishing the application port on a public interface in private-demo mode

## Required patterns

### Secrets handling

The two-file model is mandatory:
- `.env.example` — committed schema with key names + placeholders
- `.env` — real values, NEVER committed (enforced via `.gitignore`)

Rules:
- Secrets and settings come only from environment variables, read once in `app/config.py`. Feature code (`app/main.py`, `app/ingestion.py`, `app/rag.py`) never calls `os.environ` directly.
- The configurable keys are `OPENAI_API_KEY`, `LLM_MODEL`, `EMBEDDING_MODEL`, `LLM_BASE_URL`, `EMBEDDING_BASE_URL`, `DATA_DIR`. Derive Chroma storage from DATA_DIR; do not expose independent CHROMA_PATH. New env vars MUST be added to `.env.example` with a placeholder/comment.
- Never log secret values, even at debug level. Log key names and booleans (`openai_api_key_set=True`).
- On EC2 the `.env` file has restrictive permissions (`chmod 600`) and lives outside the repository checkout.

### PPTX upload validation (`app/ingestion.py`)

PPTX is a ZIP container, so an extension check alone is insufficient. Before any extraction:
- Check the extension is `.pptx`
- Check the ZIP file signature (magic bytes `PK\x03\x04`)
- Check the archive structure (`[Content_Types].xml` and `ppt/presentation.xml` present) and reject archive members whose names are absolute or contain `..`
- Enforce a 10 MiB file cap and a total request cap of 10 MiB + 64 KiB while receiving, before multipart parsing/spooling; later file recounting does not replace the request cap
- Bound the total uncompressed size (zip-bomb defense) and reject when it exceeds a fixed ceiling
- Invalid, oversized, and malformed files fail with a clear error and leave no partial state (QG-08)

### File storage

- Stored files use SHA-256-derived names, never the client filename
- Display filenames are sanitized (strip path separators and control characters, cap length) before rendering or writing to the manifest
- All application-owned data paths are built with `pathlib.Path` and resolved under the configured DATA_DIR (`uploads/`, `chroma/`, `manifest.json`): `/data` in the container, an explicit local path in development, a temporary root in tests. Reject anything that escapes. Bound and clean parser temporary storage separately.
- The manifest is updated atomically (write a temp file, then rename) and only after successful indexing. Partial chunks for a failed or interrupted ingest are cleaned up or safely retried before the document is marked complete.
- Coordinate ingest mutation and retrieval snapshots with the same process lock. Inconsistent state, missing/corrupt metadata alongside existing data, or failed cleanup must preserve data and block uploads/queries; do not treat it as an empty root or delete durable data automatically.

### Document text is untrusted input

- Retrieved slide text is data, never instructions. Keep the system-level grounding policy in its own system message; never concatenate document text into it.
- Source labels are built from retrieved metadata (`source_file`, `slide_number`, `file_sha256`, `chunk_index`). If the model emits source identifiers, validate them against the retrieved set before display (QG-06).
- The model's free-form text is never executed, evaluated, or used to build file paths or queries.

### HTML rendering (`app/templates/`)

- Jinja2 autoescaping stays on for every template; never apply `| safe` to document-derived or model-derived content
- Error pages never echo raw upload bytes or full request bodies

### External API calls

- Only synthetic demo data is sent to the embedding and chat APIs. Never upload real operational documents to this demo.
- Every external call has a timeout; no unbounded waits
- Compare the persisted full index configuration (model, non-secret endpoint identity, dimensions, metric, extractor/chunking version). A mismatch blocks use without mutation. Recover explicitly with a fresh data root and re-upload; never mix vector spaces or silently reuse an incompatible threshold.

### Deployment (private demo)

- Docker publishes the port on the EC2 loopback interface only (`-p 127.0.0.1:8000:8000`); the operator reaches it through an SSH tunnel
- The security group allows inbound TCP 22 from the operator's current IP only; ports 8000 and 443 stay closed
- `--restart unless-stopped`; `/data` is a bind mount to the EBS volume, verified mounted before the container starts
- Verify volume identity and empty-filesystem status explicitly before one-time formatting. Preserve existing secrets/fstab entries on reruns. Test the boot-time mount dependency before claiming boot recovery.

## When adding new features

1. Validate all input at the entry point (FastAPI request model, upload validator)
2. Resolve and contain every application data path under the configured DATA_DIR
3. Never interpolate user or document text into shell commands, the system prompt, or file paths
4. Log security-relevant events: rejected uploads, path-containment failures, dropped citations
5. Test with adversarial input: non-ZIP bytes named `.pptx`, oversized archives, archive members containing `..`, slide text that reads like instructions, HTML in slide text

## Memory + context

- Never copy secret values into conversation memory or session notes
- Never echo secret values in tool results — even truncated
- Memory may store key NAMES, never values
