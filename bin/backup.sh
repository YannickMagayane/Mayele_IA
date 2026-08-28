#!/usr/bin/env bash
# ==============================================================================
# Script: bin/backup.sh
# Description: Backup script for SQLite database & Vector database ChromaDB.
# ==============================================================================

set -e

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "=== Backing up Observatory RDC database & ChromaDB vector store ==="

if [ -f "observatory_rdc.db" ]; then
    cp observatory_rdc.db "$BACKUP_DIR/observatory_rdc.db"
    echo "[+] Database backed up to $BACKUP_DIR/observatory_rdc.db"
fi

if [ -d "chroma_db_store" ]; then
    cp -r chroma_db_store "$BACKUP_DIR/chroma_db_store"
    echo "[+] Vector database store backed up to $BACKUP_DIR/chroma_db_store"
fi

echo "=== Backup completed successfully ==="
