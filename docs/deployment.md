# Deployment and recovery runbook (EC2, private demo)

One non-root container on one EC2 `t3.small` in `eu-central-1`. Its data root
lives on an EBS volume mounted at `/data`. Access is only through an SSH tunnel.
This runbook implements EXEC-01 §§ 3–4 and 6. **Nothing in it has been executed
on EC2 yet.** Every named check below is an unchecked procedure with evidence
fields to fill.

Conventions: run commands on the instance as a sudo-capable operator unless
marked *operator machine*. Values in `<angle brackets>` are placeholders and always sit inside quotes, so a
pasted placeholder cannot act as a shell redirection. Never
paste secret values into commands, logs, issues or this file.

## Host layout

| Host path | Owner / mode | Purpose |
|---|---|---|
| `/data` | root, 755; mountpoint made immutable while unmounted | EBS filesystem root (holds the ext4 `lost+found`) |
| `/data/sliderag` | 10001:10001, 750 | Active application data root, bind-mounted at container `/data` |
| `/data/sliderag-<UTC timestamp>` | 10001:10001, 750 | Fresh roots created by recovery; older roots stay preserved beside them |
| `/etc/sliderag/sliderag.env` | root, 600 (directory 700) | Secret environment file, outside the checkout and the image |

The application root is a subdirectory, not the mountpoint itself, so a fresh
root can sit beside the preserved one on the same volume. Ownership goes to the
image user (uid/gid 10001) only after the mount has been verified. The container
uses `--mount type=bind`, which fails if the source is missing; `-v` would
silently create the directory, possibly on the root disk.

## A. One-time volume initialisation

Do this once per new, empty volume. A failed, ambiguous or surprising probe is
**not** permission to format: stop and investigate. Never use a
`blkid || mkfs` style sequence, which formats whenever the probe merely fails.

1. In the EC2 console, note the volume ID attached to this instance, for example
   `vol-0123456789abcdef0`. Do not guess it from size.
2. Find the device whose serial matches it. On Nitro instances the serial is the
   volume ID without the dash.

   ```bash
   lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,SERIAL
   CANDIDATE="<device name from lsblk, e.g. nvme1n1>"
   sudo nvme id-ctrl -v "/dev/$CANDIDATE" | grep -E '^sn'     # needs nvme-cli
   ```

3. Set both values in your shell and run the read-only probe. It prints a
   verdict and changes nothing.

   ```bash
   EXPECTED_VOL="<vol-id from the console>"
   DEV="/dev/<candidate, e.g. nvme1n1>"

   blank_volume() {
     : "${EXPECTED_VOL:?set EXPECTED_VOL}" "${DEV:?set DEV}"
     [ "$(lsblk -dno SERIAL "$DEV")" = "${EXPECTED_VOL/-/}" ] || { echo "serial mismatch"; return 1; }
     [ -z "$(lsblk -no MOUNTPOINTS "$DEV" | tr -d '[:space:]')" ] || { echo "mounted"; return 1; }
     [ "$(lsblk -no NAME "$DEV" | wc -l)" -eq 1 ] || { echo "has partitions"; return 1; }
     sudo blkid -p "$DEV" >/dev/null 2>&1
     [ $? -eq 2 ] || { echo "blkid did not report 'nothing found' (exit 2)"; return 1; }
     local sigs
     sigs=$(sudo wipefs --no-act --noheadings "$DEV") || { echo "wipefs failed"; return 1; }
     [ -z "$sigs" ] || { echo "signatures present"; return 1; }
   }
   if blank_volume; then echo "VERDICT: blank volume confirmed"; else echo "VERDICT: STOP - do not format"; fi
   ```

   `blkid -p` exits 2 only when it probed the device and found no signature. Any
   other exit code (for example an I/O or permission error) stops the procedure.

4. Format only on a positive verdict. The function runs again in the same
   command, so the decision cannot rely on stale shell state.

   ```bash
   if blank_volume; then sudo mkfs.ext4 -L sliderag-data "$DEV"; else echo "STOP: not formatted"; fi
   ```

5. Prepare the mountpoint, add the fstab entry once and mount by UUID. Existing
   fstab entries are kept; on a rerun nothing is appended.

   ```bash
   UUID=$(sudo blkid -s UUID -o value "$DEV"); echo "UUID=$UUID"
   sudo cp -n /etc/fstab /etc/fstab.pre-sliderag            # first backup only, never overwritten
   sudo mkdir -p /data
   # While /data is NOT mounted, make the bare mountpoint immutable: nothing can then
   # write to the root disk through it if the volume is ever missing.
   if mountpoint -q /data; then echo "already mounted: skip chattr"; else sudo chattr +i /data; fi
   if grep -qsE '^[^#]*[[:space:]]/data[[:space:]]' /etc/fstab; then
     echo "fstab already has a /data entry: keep it, do not add another"
   else
     echo "UUID=$UUID /data ext4 defaults,nofail,x-systemd.device-timeout=30s 0 2" | sudo tee -a /etc/fstab
   fi
   sudo systemctl daemon-reload && sudo mount /data && findmnt /data
   ```

   `nofail` keeps the instance bootable (and reachable over SSH) if the volume is
   missing. The Docker dependency in section B stops the application in that case.

6. Create the application root only on the verified mount.

   ```bash
   if mountpoint -q /data; then
     sudo install -d -o 10001 -g 10001 -m 750 /data/sliderag
   else
     echo "STOP: /data is not mounted"
   fi
   ```

## B. Mount dependency (no fallback writes to the root disk)

Docker restarts `unless-stopped` containers itself when the daemon starts, so the
dependency is attached to `docker.service`. If `/data` cannot be mounted, Docker
does not start and no container can write anywhere.

```bash
sudo mkdir -p /etc/systemd/system/docker.service.d
printf '[Unit]\nRequiresMountsFor=/data\n' | sudo tee /etc/systemd/system/docker.service.d/10-sliderag-data.conf
sudo systemctl daemon-reload
systemctl show docker.service -p Requires -p After | grep -o 'data.mount' | sort -u   # expect: data.mount
```

The layers are: the `RequiresMountsFor` drop-in, the immutable bare mountpoint,
`--mount type=bind` (no auto-created source), and the `mountpoint -q /data`
pre-check in the run block below. `mount-boot-safety` must verify them before any
boot-recovery claim.

## C. Repeatable deployment

### Secret environment file (preserved on reruns)

```bash
sudo install -d -m 700 /etc/sliderag
[ -e /etc/sliderag/sliderag.env ] || sudo install -m 600 /dev/null /etc/sliderag/sliderag.env
sudoedit /etc/sliderag/sliderag.env
sudo stat -c '%a %U %n' /etc/sliderag/sliderag.env                # expect: 600 root
```

Use the keys from `.env.example` with `DATA_DIR=/data` (the container path).
Docker's `--env-file` takes values literally: no quotes, no `export`. The file
is root-only, so run the Docker commands below with `sudo`.

### Image

Build from a tagged checkout (releases are tagged by hand, see the versioning
rule), or load an image built from that tag. Record the image ID.

```bash
TAG="<release tag, e.g. v0.1.0>"
CHECKOUT="<path to the repository checkout>"
git -C "$CHECKOUT" fetch --tags && git -C "$CHECKOUT" checkout "$TAG"
sudo docker build -t "sliderag-mini:$TAG" "$CHECKOUT"
sudo docker image inspect -f '{{.Id}}' "sliderag-mini:$TAG"
```

### Run or recreate

```bash
TAG="<release tag>"
APP_ROOT="/data/sliderag"        # the active root; recovery changes this
sudo docker rm -f sliderag 2>/dev/null   # recreate: removes the container only, never data
if mountpoint -q /data && [ -d "$APP_ROOT" ]; then
  sudo docker run -d --name sliderag --restart unless-stopped \
    -p 127.0.0.1:8000:8000 \
    --env-file /etc/sliderag/sliderag.env \
    --mount type=bind,source="$APP_ROOT",target=/data \
    "sliderag-mini:$TAG"
else
  echo "STOP: /data is not mounted or $APP_ROOT is missing; not starting"
fi
```

### Access and network

- Security group: inbound TCP 22 from the operator's current IP (`/32`) only.
  Ports 8000 and 443 stay closed; there is no public application endpoint.
  Update the rule when the operator IP changes.
- Tunnel (*operator machine*): `ssh -N -L 8000:127.0.0.1:8000 "$SSH_TARGET"` with `SSH_TARGET="<user>@<instance host>"`,
  then open <http://127.0.0.1:8000>.
- `/health` through the tunnel: `curl -s http://127.0.0.1:8000/health`.

## D. Named manual checks (unchecked)

Record redacted outputs only. No secret values, account IDs or home paths go in
public evidence.

### `ec2-private-access`

- [ ] Exactly one app container: `sudo docker ps --filter name=sliderag --format '{{.Names}} {{.Status}}'`
- [ ] Non-root: `sudo docker exec sliderag id -u` → `10001`
- [ ] Loopback-only port: `sudo docker port sliderag` → only `8000/tcp -> 127.0.0.1:8000`, and `sudo ss -ltn | grep ':8000'` shows only `127.0.0.1`
- [ ] Not reachable publicly (*operator machine*): `curl -m 5 "http://$PUBLIC_IP:8000/"` (with `PUBLIC_IP="<instance public IP>"`) times out or is refused
- [ ] Security group inbound rules: only TCP 22 from the operator `/32`
- [ ] Restart policy: `sudo docker inspect -f '{{.HostConfig.RestartPolicy.Name}}' sliderag` → `unless-stopped`
- [ ] Verified mount: `findmnt -no SOURCE,FSTYPE /data` is the identified volume, and `sudo docker inspect -f '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{end}}' sliderag` → `/data/sliderag -> /data`
- [ ] Secret only outside image and checkout: the env-file `stat` shows 600 root; `sudo docker image inspect -f '{{.Config.Env}}' sliderag-mini:$TAG` has no `OPENAI_API_KEY`; `sudo docker run --rm --entrypoint sh sliderag-mini:$TAG -c 'ls -a /app'` shows only `.venv` and `app`
- [ ] `/health` through the tunnel → 200 `ok`

Evidence (date, image ID, outputs): `______`

### `ec2-recreation` (QG-09)

- [ ] Upload the synthetic deck and record the document's slide and chunk counts (page list or `sudo docker exec sliderag python -c "import json; d=json.load(open('/data/manifest.json')); print([(x['source_file'], x['slide_count'], x['chunk_count']) for x in d['documents']])"`)
- [ ] A supported question answers with its slide source; the unsupported question returns the fallback
- [ ] Recreate with the run block (`docker rm -f` + run), then `/health` → 200
- [ ] Same document and counts listed; the same question answers with the same source; unsupported still refused
- [ ] Re-upload the same deck → "Already indexed …"; chunk count unchanged

Evidence (counts before/after, answers, sources, timestamps): `______`

### `mount-boot-safety`

- [ ] Dependency loaded: `systemctl show docker.service -p Requires -p After | grep -o data.mount`
- [ ] No fallback writes through the bare mountpoint, with the app stopped:
  `sudo docker stop sliderag && sudo systemctl stop docker.socket docker.service && sudo umount /data`,
  then `lsattr -d /data` shows `i` and `sudo touch /data/probe` fails;
  then `sudo mount /data && sudo systemctl start docker && sudo docker start sliderag` (a manually stopped
  container is not restarted by `unless-stopped`) and confirm `/health` returns
- [ ] Normal reboot: `sudo reboot`; afterwards `findmnt /data`, container `Up`, `/health` 200, documents present
- [ ] Missing-volume boot (needs explicit operator authorisation for the AWS detach): stop the instance, detach the volume, start; expect SSH reachable, `data.mount` failed, `docker.service` not running, no container, `ls -A /data` empty; then stop, reattach, start, and verify recovery
- [ ] No historical `blkid || mkfs` sequence anywhere in host scripts or history used for this setup

Evidence: `______`

### Memory and latency sampling

A single `docker stats --no-stream` reading is not peak usage. Sample repeatedly
across the whole demo (upload, five questions, recreation, duplicate upload),
then report the sampled maximum, the sample count and the interval. The result
is a sampled maximum, not a true peak.

```bash
( while true; do
    printf '%s %s\n' "$(date -u +%T)" \
      "$(sudo docker stats --no-stream --format '{{.MemUsage}}' sliderag 2>/dev/null | cut -d/ -f1)"
    sleep 1
  done ) > /tmp/sliderag-mem.log &
SAMPLER=$!
# ... run the demo operations ...
kill "$SAMPLER"
awk 'NF==2 { v=$2; u=v; sub(/^[0-9.]+/, "", u); n=v+0;
       if (u=="GiB") n*=1024; else if (u=="KiB") n/=1024; else if (u=="B") n/=1048576;
       if (n>m) { m=n; t=$1 } }
     END { printf "sampled max %.1f MiB at %s over %d samples\n", m, t, NR }' /tmp/sliderag-mem.log
```

Latency: time each question through the tunnel (*operator machine*), for example
`curl -s -o /dev/null -w '%{http_code} %{time_total}s\n' -d 'question=<text>' http://127.0.0.1:8000/ask`.

Evidence (sampled max, samples, interval, per-question latencies): `______`

## E. Recovery

### Degraded reasons

`/health` returns 503 with these codes. Upload and ask also return 503, and the
data is preserved: nothing is repaired or deleted automatically except the app's
own abandoned temporary files.

| Reason | Meaning | Operator action |
|---|---|---|
| `openai_api_key_missing` | No key in the environment | Fix the env file, recreate the container |
| `provider_client_unavailable` | A provider client could not be built (for example an endpoint the HTTP client refuses) | Check `LLM_BASE_URL` / `EMBEDDING_BASE_URL`, recreate |
| `structured_output_unsupported` | `LLM_MODEL` lacks native json_schema output | Use a supported model (default `gpt-4.1-mini`), recreate |
| `data_root_unavailable` | The root cannot be created or written | Check the mount and 10001 ownership; never use `chmod 777` |
| `storage_unavailable` | Unexpected error opening the manifest or Chroma (logs name the type only) | Preserve the root and investigate; otherwise use a fresh root |
| `index_config_mismatch` | Settings or image differ from the root's index configuration (model, endpoint, dimensions, schema/extractor/chunking version) | Restore the matching settings or image, or use a fresh root |
| `manifest_missing` | Chunks or uploads exist without a manifest | Fresh root |
| `manifest_corrupt`, `manifest_version_unknown` | The manifest is unreadable or from another version | Fresh root (or restore a known-good copy of the whole root) |
| `chunks_missing`, `unexplained_chunks`, `upload_missing`, `unexplained_uploads` | Manifest, Chroma and uploads disagree (for example an interrupted ingest) | Fresh root |
| `unexplained_entries` | No manifest, but the directory holds other files: wrong bind source or foreign data | Check `APP_ROOT`; never point the app at a non-empty directory; fresh empty root |
| `cleanup_failed` | Runtime: a failed upload could not be rolled back verifiably | Fresh root (a restart will usually report an inconsistency) |
| `invalid_chunk_metadata` | Stored chunk metadata failed validation during a query | Fresh root |

An empty `lost+found` (or one the app user cannot list) is ignored. A non-empty
one means fsck recovered files there: investigate the volume before reuse.

### Fresh-root recovery

Keep the old root untouched for diagnosis; deleting it is a separate, explicit
decision. Then start on a new empty root and re-upload.

```bash
sudo docker rm -f sliderag                       # container only
NEW="/data/sliderag-$(date -u +%Y%m%dT%H%M%SZ)"
if mountpoint -q /data; then sudo install -d -o 10001 -g 10001 -m 750 "$NEW"; echo "$NEW"; fi
# Set APP_ROOT="$NEW" in the run block above, run it, then re-upload the deck.
```

Record which root is active. There is no automatic migration, collection switch
or reindex.

### Image rollback

Run the previous image tag with the run block (set `TAG`). An image only accepts
a data root whose index configuration it shares. If it reports
`index_config_mismatch`, set `APP_ROOT` to a preserved root that this version
created, or to a fresh root. Keep each version's roots until the rollback window
closes. The EBS volume is not a backup: snapshot it, or copy a root, only while
the container is stopped.

### Pre-deployment ChromaDB check

Before every deployment and every Chroma upgrade, follow
[`docs/security/chromadb-advisories.md`](security/chromadb-advisories.md):

- re-check both advisories and their released fix status, and the `chromadb`
  version in `uv.lock`;
- run the guard and persistence tests:
  `uv run pytest -m "not integration" -k "embedding_function or stored_embedding or untampered or fresh_process"`;
- confirm that no Chroma server or extra port is exposed and that the operator
  owns the data root.

Record the date and result: `______`

## Local container smoke check (no key, disposable data)

This checks the image's degraded path and persistence across recreation without
credentials. It uses a Docker-managed volume, because a bind-mounted temporary
directory would need `sudo` to be owned by uid 10001. Every resource is named
so it can be removed afterwards.

```bash
docker build -t sliderag-mini:smoke .
docker volume create sliderag-smoke
docker run -d --name sliderag-smoke -p 127.0.0.1:8723:8000 \
  --mount type=volume,source=sliderag-smoke,target=/data sliderag-mini:smoke
docker exec sliderag-smoke id                      # uid=10001(app)
docker port sliderag-smoke                         # 8000/tcp -> 127.0.0.1:8723
curl -s -w ' %{http_code}\n' http://127.0.0.1:8723/health          # degraded, openai_api_key_missing, 503
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8723/    # 200
curl -s -o /dev/null -w '%{http_code}\n' -F "file=@demo/5G_RAN_Operations_Demo.pptx" http://127.0.0.1:8723/upload  # 503
curl -s -o /dev/null -w '%{http_code}\n' -d 'question=test' http://127.0.0.1:8723/ask                              # 503
docker exec sliderag-smoke sha256sum /data/manifest.json           # root initialised
docker rm -f sliderag-smoke
docker run -d --name sliderag-smoke -p 127.0.0.1:8723:8000 \
  --mount type=volume,source=sliderag-smoke,target=/data sliderag-mini:smoke
docker exec sliderag-smoke sha256sum /data/manifest.json           # same hash; /health still only key-missing
docker run --rm --entrypoint sh sliderag-mini:smoke -c 'ls -a /app'   # .venv and app only
docker rm -f sliderag-smoke && docker volume rm sliderag-smoke && docker rmi sliderag-mini:smoke
```

Generate the deck first with `uv run python demo/generate_pptx.py`. This check
does not exercise real answers, the EBS mount or the boot behaviour.
