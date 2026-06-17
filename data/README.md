# Private data bundle

Put the team-only bundle here:

```text
data/annals_private_bundle.zip
```

This repository includes `annals_private_bundle.zip` so teammates can run RAG immediately after cloning.

Other generated data files in this directory are still ignored by Git.

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
