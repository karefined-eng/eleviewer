use pyo3::prelude::*;
use pyo3::types::PyList;
use rayon::prelude::*;
use rusqlite::{params, Connection};
use std::fs;
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

const INDEX_EXTENSIONS: &[&str] = &[".md", ".txt", ".csv"];

fn init_schema(conn: &Connection) -> rusqlite::Result<()> {
    conn.execute_batch(
        "CREATE VIRTUAL TABLE IF NOT EXISTS document_index USING fts5(
            filename,
            content,
            path UNINDEXED,
            vault UNINDEXED,
            tokenize='porter unicode61'
        );
        CREATE TABLE IF NOT EXISTS file_meta (
            path TEXT PRIMARY KEY,
            vault TEXT NOT NULL,
            mtime REAL NOT NULL
        );",
    )
}

fn extract_text(path: &Path) -> Option<String> {
    let ext = path.extension()?.to_str()?.to_lowercase();
    if !INDEX_EXTENSIONS.iter().any(|e| *e == ext) {
        return None;
    }
    let bytes = fs::read(path).ok()?;
    if bytes.len() > 2_000_000 {
        return Some(String::from_utf8_lossy(&bytes[..2_000_000]).into_owned());
    }
    Some(String::from_utf8_lossy(&bytes).into_owned())
}

fn vault_boundary_ok(vault_root: &Path, entry_path: &Path) -> bool {
    entry_path.starts_with(vault_root)
}

struct IndexedDoc {
    path: String,
    vault: String,
    filename: String,
    content: String,
    mtime: f64,
}

fn collect_vault_docs(vault_path: &Path) -> PyResult<Vec<IndexedDoc>> {
    let vault_root = vault_path
        .canonicalize()
        .map_err(|e| pyo3::exceptions::PyOSError::new_err(e.to_string()))?;
    let vault_str = vault_root.to_string_lossy().into_owned();
    let vault_name = vault_root
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_else(|| vault_str.clone());

    let entries: Vec<PathBuf> = WalkDir::new(&vault_root)
        .follow_links(false)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.file_type().is_file())
        .map(|e| e.into_path())
        .collect();

    let docs: Vec<IndexedDoc> = entries
        .par_iter()
        .filter_map(|path| {
            let name = path.file_name()?.to_str()?;
            if name.starts_with('.') {
                return None;
            }
            if !vault_boundary_ok(&vault_root, path) {
                return None;
            }
            let ext = path.extension()?.to_str()?.to_lowercase();
            if !INDEX_EXTENSIONS.iter().any(|e| *e == ext) {
                return None;
            }
            let meta = fs::metadata(path).ok()?;
            let mtime = meta
                .modified()
                .ok()?
                .duration_since(std::time::UNIX_EPOCH)
                .ok()?
                .as_secs_f64();
            let content = extract_text(path).unwrap_or_default();
            Some(IndexedDoc {
                path: path.to_string_lossy().into_owned(),
                vault: vault_name.clone(),
                filename: name.to_owned(),
                content,
                mtime,
            })
        })
        .collect();

    Ok(docs)
}

#[pyfunction]
fn index_vault(db_path: String, vault_path: String) -> PyResult<usize> {
    let vault = PathBuf::from(&vault_path);
    if !vault.is_dir() {
        return Ok(0);
    }

    let docs = collect_vault_docs(&vault)?;
    let conn = Connection::open(&db_path)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    init_schema(&conn).map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    let vault_key = vault
        .canonicalize()
        .map_err(|e| pyo3::exceptions::PyOSError::new_err(e.to_string()))?
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();

    conn.execute(
        "DELETE FROM document_index WHERE vault = ?1",
        params![vault_key],
    )
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    conn.execute("DELETE FROM file_meta WHERE vault = ?1", params![vault_key])
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    let mut count = 0usize;
    for doc in docs {
        conn.execute(
            "INSERT INTO document_index (filename, content, path, vault) VALUES (?1, ?2, ?3, ?4)",
            params![doc.filename, doc.content, doc.path, doc.vault],
        )
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        conn.execute(
            "INSERT INTO file_meta (path, vault, mtime) VALUES (?1, ?2, ?3)",
            params![doc.path, doc.vault, doc.mtime],
        )
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        count += 1;
    }
    Ok(count)
}

fn fts_query(raw: &str) -> String {
    let tokens: Vec<String> = raw
        .split(|c: char| !c.is_alphanumeric())
        .filter(|t| !t.is_empty())
        .map(|t| format!("\"{}\"*", t.replace('"', "\"\"")))
        .collect();
    tokens.join(" AND ")
}

#[pyfunction]
fn search_documents(
    py: Python<'_>,
    db_path: String,
    query: String,
    vaults: Vec<String>,
    limit: usize,
) -> PyResult<Py<PyList>> {
    let fts = fts_query(&query);
    if fts.is_empty() {
        return Ok(PyList::empty_bound(py).into());
    }

    let conn = Connection::open(&db_path)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    init_schema(&conn).map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    let vault_names: std::collections::HashSet<String> = vaults
        .iter()
        .filter_map(|v| {
            Path::new(v)
                .canonicalize()
                .ok()
                .and_then(|p| p.file_name().map(|n| n.to_string_lossy().into_owned()))
        })
        .collect();

    let mut stmt = conn
        .prepare(
            "SELECT path, vault, filename,
                    snippet(document_index, 1, '', '', '...', 40) AS snip,
                    bm25(document_index) AS rank
             FROM document_index
             WHERE document_index MATCH ?1
             ORDER BY rank
             LIMIT ?2",
        )
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    let rows = stmt
        .query_map(params![fts, (limit * 4) as i64], |row| {
            Ok((
                row.get::<_, String>(0)?,
                row.get::<_, String>(1)?,
                row.get::<_, String>(2)?,
                row.get::<_, String>(3)?,
            ))
        })
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    let list = PyList::empty_bound(py);
    let mut count = 0usize;
    for row in rows.flatten() {
        let (full_path, vault_name, filename, snippet) = row;
        if !vault_names.is_empty() && !vault_names.contains(&vault_name) {
            continue;
        }
        let display_dir = vaults
            .iter()
            .find_map(|v| {
                let root = Path::new(v).canonicalize().ok()?;
                Path::new(&full_path).parent()?.strip_prefix(&root).ok().map(|rel| {
                    if rel.as_os_str().is_empty() {
                        String::new()
                    } else {
                        format!(" ({})", rel.display())
                    }
                })
            })
            .unwrap_or_default();
        let tuple = (filename, display_dir, vault_name, full_path, snippet);
        list.append(tuple)?;
        count += 1;
        if count >= limit {
            break;
        }
    }
    Ok(list.into())
}

#[pymodule]
fn eleviewer_native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(index_vault, m)?)?;
    m.add_function(wrap_pyfunction!(search_documents, m)?)?;
    Ok(())
}
