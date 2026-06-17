# Private data bundle

Put the team-only bundle here:

```text
data/annals_private_bundle.zip
```

This directory is intentionally ignored by Git except for this README and `.gitkeep`.

The zip should contain precomputed RAG data:

```text
manifest.json
annals_articles.jsonl
annals_chunks.jsonl
```

After the zip is in place, run:

```bash
docker compose up --build
```
