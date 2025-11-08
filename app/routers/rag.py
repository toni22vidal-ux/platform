from fastapi import APIRouter, HTTPException
from typing import List, Dict
import os
import psycopg

router = APIRouter(prefix="/rag", tags=["rag"])

# DSN prioritario: variable de entorno. Si no hay, intenta 'db' (Docker) y luego 127.0.0.1 (local).
DEFAULTS = [
    os.getenv("DB_DSN"),
    "postgresql://postgres:postgres@db:5432/multinicho",
    "postgresql://postgres:postgres@127.0.0.1:5432/multinicho",
]
DB_DSN = next(d for d in DEFAULTS if d)  # primer valor no vacío


def ensure_table(conn: "psycopg.Connection") -> None:
    """Crea la tabla y el índice único si no existen."""
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS rag_docs (
              id SERIAL PRIMARY KEY,
              content TEXT NOT NULL
            );
            """
        )
        cur.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_rag_docs_content ON rag_docs(content)"
        )
        conn.commit()


def get_conn() -> "psycopg.Connection":
    """Devuelve una conexión funcional.
    Si el DSN usa @db: y falla (modo local), hace fallback a 127.0.0.1.
    """
    try:
        return psycopg.connect(DB_DSN)
    except Exception:
        if "@db:" in DB_DSN:
            local = DB_DSN.replace("@db:", "@127.0.0.1:")
            return psycopg.connect(local)
        raise


@router.post("/ingest")
def ingest(payload: Dict):
    """Inserta textos. Evita duplicados vía índice único + ON CONFLICT DO NOTHING."""
    texts: List[str] = payload.get("texts", [])
    if not texts:
        raise HTTPException(400, "texts required")
    with get_conn() as conn:
        ensure_table(conn)
        with conn.cursor() as cur:
            for t in texts:
                cur.execute(
                    "INSERT INTO rag_docs(content) VALUES(%s) ON CONFLICT (content) DO NOTHING",
                    (t,),
                )
        conn.commit()
    return {"ok": True, "ingested": len(texts)}


@router.get("/query")
def query(q: str):
    """Búsqueda simple por LIKE (demo)."""
    if not q:
        raise HTTPException(400, "q required")
    with get_conn() as conn, conn.cursor() as cur:
        ensure_table(conn)
        cur.execute(
            "SELECT content FROM rag_docs WHERE content ILIKE %s LIMIT 5",
            (f"%{q}%",),
        )
        rows = [r[0] for r in cur.fetchall()]
    return {"ok": True, "results": rows}


@router.post("/reset")
def reset():
    """Borra todos los documentos (útil para pruebas)."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE rag_docs RESTART IDENTITY")
        conn.commit()
    return {"ok": True}
