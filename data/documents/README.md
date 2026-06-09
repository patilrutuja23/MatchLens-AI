# MatchLens AI - Document Repository

This folder contains official football documents for RAG-enhanced explanations.

## Folder Structure

```
documents/
├── fifa_rules/          # FIFA Laws of the Game PDFs
├── var_guidelines/      # VAR Protocol and Guidelines PDFs
└── processed/           # Auto-generated markdown files
```

## Adding Documents

### FIFA Rules
Place FIFA Laws of the Game PDFs in the `fifa_rules/` folder:
- `Laws_of_the_Game_2023-24.pdf`
- `IFAB_Laws_of_the_Game.pdf`

Download from: https://www.theifab.com/laws

### VAR Guidelines
Place VAR protocol documents in the `var_guidelines/` folder:
- `VAR_Protocol.pdf`
- `VAR_Handbook.pdf`

Download from: https://www.theifab.com/laws/var-protocol

## Document Ingestion

After adding PDFs, run the ingestion pipeline:

```bash
python -m src.utils.ingest
```

This will:
1. Convert PDFs to structured markdown using Docling
2. Chunk documents intelligently
3. Generate embeddings using sentence-transformers
4. Store in FAISS vector database
5. Save processed markdown in `processed/` folder

## Processed Files

The `processed/` folder contains:
- `.md` files: Markdown versions of PDFs
- FAISS indices in `../vector_db/`
- Metadata JSON files

## Usage in MatchLens AI

Once ingested, documents are automatically used for:
- **VAR Explanations**: Retrieves relevant FIFA rules and VAR guidelines
- **Rule Citations**: Shows exact rule text with source
- **Confidence Scores**: Based on retrieval quality
- **Evidence Display**: Shows retrieved context

## Requirements

Install dependencies:
```bash
pip install docling PyPDF2
```

## Notes

- PDFs should be text-based (not scanned images)
- Larger documents may take longer to process
- Re-run ingestion after adding new documents
- Processed files are cached for faster startup

## Made with Bob