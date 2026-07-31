"""
Skill & Agent Registry System
=============================
Zentrale Registrierung und Discovery für alle Skills und Agents.
Unterstützt dynamische Erweiterung und semantische Suche.
"""

import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib


class SkillAgentRegistry:
    """
    Zentrale Registry für Skills und Agents.
    Speichert Metadaten in SQLite für schnelle Abfragen.
    """
    
    def __init__(self, db_path: str = "registry.db", base_path: str = None):
        """
        Initialisiert die Registry.
        
        Args:
            db_path: Pfad zur SQLite-Datenbank
            base_path: Basispfad zum Skill/Agent-Verzeichnis
        """
        self.db_path = db_path
        self.base_path = base_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
    
    def _init_db(self):
        """Erstellt die Datenbankstruktur."""
        cursor = self.conn.cursor()
        
        # Haupttabelle für Skills und Agents
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('skill', 'agent')),
                version TEXT NOT NULL,
                description TEXT,
                author TEXT,
                manifest_path TEXT NOT NULL,
                implementation_language TEXT,
                entrypoint TEXT,
                manifest_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tags für Kategorisierung
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
            )
        """)
        
        # Capabilities für semantische Suche
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS capabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id INTEGER NOT NULL,
                capability TEXT NOT NULL,
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
            )
        """)
        
        # Interface-Parameter
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id INTEGER NOT NULL,
                direction TEXT NOT NULL CHECK(direction IN ('input', 'output')),
                name TEXT NOT NULL,
                param_type TEXT NOT NULL,
                description TEXT,
                required BOOLEAN DEFAULT 1,
                default_value TEXT,
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
            )
        """)
        
        # Abhängigkeiten zwischen Entities
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id INTEGER NOT NULL,
                depends_on TEXT NOT NULL,
                version_constraint TEXT,
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
            )
        """)
        
        # Indizes für schnelle Suche
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_capabilities_cap ON capabilities(capability)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type)")
        
        self.conn.commit()
    
    def register(self, manifest_path: str) -> bool:
        """
        Registriert einen Skill oder Agent aus einer manifest.json-Datei.
        
        Args:
            manifest_path: Pfad zur manifest.json
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Hash für Änderungserkennung
            manifest_hash = hashlib.md5(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
            
            cursor = self.conn.cursor()
            
            # Prüfe ob bereits vorhanden
            cursor.execute("SELECT id, manifest_hash FROM entities WHERE name = ?", (manifest['name'],))
            existing = cursor.fetchone()
            
            if existing:
                if existing['manifest_hash'] == manifest_hash:
                    return True  # Keine Änderung
                # Update existierenden Eintrag
                entity_id = existing['id']
                cursor.execute("""
                    UPDATE entities SET
                        version = ?, description = ?, author = ?,
                        implementation_language = ?, entrypoint = ?,
                        manifest_hash = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    manifest['version'],
                    manifest.get('description', ''),
                    manifest.get('author', ''),
                    manifest.get('implementation', {}).get('language', ''),
                    manifest.get('implementation', {}).get('entrypoint', ''),
                    manifest_hash,
                    datetime.now().isoformat(),
                    entity_id
                ))
                # Lösche alte Tags, Capabilities, Parameter
                cursor.execute("DELETE FROM tags WHERE entity_id = ?", (entity_id,))
                cursor.execute("DELETE FROM capabilities WHERE entity_id = ?", (entity_id,))
                cursor.execute("DELETE FROM parameters WHERE entity_id = ?", (entity_id,))
                cursor.execute("DELETE FROM dependencies WHERE entity_id = ?", (entity_id,))
            else:
                # Neuer Eintrag
                cursor.execute("""
                    INSERT INTO entities (name, type, version, description, author,
                        manifest_path, implementation_language, entrypoint, manifest_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    manifest['name'],
                    manifest['type'],
                    manifest['version'],
                    manifest.get('description', ''),
                    manifest.get('author', ''),
                    manifest_path,
                    manifest.get('implementation', {}).get('language', ''),
                    manifest.get('implementation', {}).get('entrypoint', ''),
                    manifest_hash
                ))
                entity_id = cursor.lastrowid
            
            # Tags einfügen
            for tag in manifest.get('tags', []):
                cursor.execute("INSERT INTO tags (entity_id, tag) VALUES (?, ?)", (entity_id, tag))
            
            # Capabilities einfügen
            for cap in manifest.get('capabilities', []):
                cursor.execute("INSERT INTO capabilities (entity_id, capability) VALUES (?, ?)", (entity_id, cap))
            
            # Interface-Parameter einfügen
            interface = manifest.get('interface', {})
            for inp in interface.get('inputs', []):
                cursor.execute("""
                    INSERT INTO parameters (entity_id, direction, name, param_type, description, required, default_value)
                    VALUES (?, 'input', ?, ?, ?, ?, ?)
                """, (entity_id, inp['name'], inp['type'], inp.get('description', ''),
                      inp.get('required', True), json.dumps(inp.get('default'))))
            
            for out in interface.get('outputs', []):
                cursor.execute("""
                    INSERT INTO parameters (entity_id, direction, name, param_type, description, required, default_value)
                    VALUES (?, 'output', ?, ?, ?, 1, NULL)
                """, (entity_id, out['name'], out['type'], out.get('description', '')))
            
            # Abhängigkeiten einfügen
            for dep in manifest.get('dependencies', []):
                cursor.execute("""
                    INSERT INTO dependencies (entity_id, depends_on, version_constraint)
                    VALUES (?, ?, ?)
                """, (entity_id, dep['name'], dep.get('version', '*')))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Fehler bei Registrierung: {e}")
            return False
    
    def scan_and_register(self, directories: List[str] = None):
        """
        Scannt Verzeichnisse nach manifest.json-Dateien und registriert alle.
        
        Args:
            directories: Liste von Verzeichnissen zum Scannen
        """
        if directories is None:
            directories = [
                os.path.join(self.base_path, 'skills'),
                os.path.join(self.base_path, 'agents')
            ]
        
        registered = 0
        for directory in directories:
            if not os.path.exists(directory):
                continue
            for root, dirs, files in os.walk(directory):
                if 'manifest.json' in files:
                    manifest_path = os.path.join(root, 'manifest.json')
                    if self.register(manifest_path):
                        registered += 1
        
        return registered
    
    def search(self, 
               query: str = None,
               entity_type: str = None,
               tags: List[str] = None,
               capabilities: List[str] = None,
               input_types: List[str] = None,
               output_types: List[str] = None) -> List[Dict]:
        """
        Sucht nach Skills/Agents basierend auf verschiedenen Kriterien.
        
        Args:
            query: Freitextsuche in Name und Beschreibung
            entity_type: 'skill' oder 'agent'
            tags: Liste von Tags (OR-Verknüpfung)
            capabilities: Liste von Fähigkeiten (OR-Verknüpfung)
            input_types: Benötigte Input-Typen
            output_types: Benötigte Output-Typen
            
        Returns:
            Liste von passenden Entities
        """
        cursor = self.conn.cursor()
        
        sql = "SELECT DISTINCT e.* FROM entities e"
        joins = []
        conditions = []
        params = []
        
        if tags:
            joins.append("LEFT JOIN tags t ON e.id = t.entity_id")
            placeholders = ','.join(['?' for _ in tags])
            conditions.append(f"t.tag IN ({placeholders})")
            params.extend(tags)
        
        if capabilities:
            joins.append("LEFT JOIN capabilities c ON e.id = c.entity_id")
            placeholders = ','.join(['?' for _ in capabilities])
            conditions.append(f"c.capability IN ({placeholders})")
            params.extend(capabilities)
        
        if input_types:
            joins.append("LEFT JOIN parameters pi ON e.id = pi.entity_id AND pi.direction = 'input'")
            placeholders = ','.join(['?' for _ in input_types])
            conditions.append(f"pi.param_type IN ({placeholders})")
            params.extend(input_types)
        
        if output_types:
            joins.append("LEFT JOIN parameters po ON e.id = po.entity_id AND po.direction = 'output'")
            placeholders = ','.join(['?' for _ in output_types])
            conditions.append(f"po.param_type IN ({placeholders})")
            params.extend(output_types)
        
        if query:
            conditions.append("(e.name LIKE ? OR e.description LIKE ?)")
            params.extend([f'%{query}%', f'%{query}%'])
        
        if entity_type:
            conditions.append("e.type = ?")
            params.append(entity_type)
        
        sql += " " + " ".join(joins)
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        cursor.execute(sql, params)
        results = []
        
        for row in cursor.fetchall():
            entity = dict(row)
            entity['tags'] = self._get_tags(entity['id'])
            entity['capabilities'] = self._get_capabilities(entity['id'])
            entity['interface'] = self._get_interface(entity['id'])
            entity['dependencies'] = self._get_dependencies(entity['id'])
            results.append(entity)
        
        return results
    
    def get_by_name(self, name: str) -> Optional[Dict]:
        """Holt einen Skill/Agent anhand des Namens."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM entities WHERE name = ?", (name,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        entity = dict(row)
        entity['tags'] = self._get_tags(entity['id'])
        entity['capabilities'] = self._get_capabilities(entity['id'])
        entity['interface'] = self._get_interface(entity['id'])
        entity['dependencies'] = self._get_dependencies(entity['id'])
        
        return entity
    
    def list_all(self, entity_type: str = None) -> List[Dict]:
        """Listet alle registrierten Entities auf."""
        return self.search(entity_type=entity_type)
    
    def _get_tags(self, entity_id: int) -> List[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT tag FROM tags WHERE entity_id = ?", (entity_id,))
        return [row['tag'] for row in cursor.fetchall()]
    
    def _get_capabilities(self, entity_id: int) -> List[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT capability FROM capabilities WHERE entity_id = ?", (entity_id,))
        return [row['capability'] for row in cursor.fetchall()]
    
    def _get_interface(self, entity_id: int) -> Dict:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM parameters WHERE entity_id = ?", (entity_id,))
        
        interface = {'inputs': [], 'outputs': []}
        for row in cursor.fetchall():
            param = {
                'name': row['name'],
                'type': row['param_type'],
                'description': row['description'],
                'required': bool(row['required'])
            }
            if row['default_value']:
                param['default'] = json.loads(row['default_value'])
            
            if row['direction'] == 'input':
                interface['inputs'].append(param)
            else:
                interface['outputs'].append(param)
        
        return interface
    
    def _get_dependencies(self, entity_id: int) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT depends_on, version_constraint FROM dependencies WHERE entity_id = ?", (entity_id,))
        return [{'name': row['depends_on'], 'version': row['version_constraint']} for row in cursor.fetchall()]
    
    def export_catalog(self, output_path: str = "catalog.json"):
        """Exportiert den gesamten Katalog als JSON."""
        catalog = {
            'version': '1.0',
            'generated_at': datetime.now().isoformat(),
            'skills': self.list_all('skill'),
            'agents': self.list_all('agent')
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def close(self):
        """Schließt die Datenbankverbindung."""
        self.conn.close()


# CLI-Interface
if __name__ == "__main__":
    import sys
    
    registry = SkillAgentRegistry()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "scan":
            count = registry.scan_and_register()
            print(f"Registriert: {count} Skills/Agents")
        
        elif command == "list":
            entities = registry.list_all()
            for e in entities:
                print(f"[{e['type']}] {e['name']} v{e['version']}: {e['description']}")
        
        elif command == "search" and len(sys.argv) > 2:
            query = sys.argv[2]
            results = registry.search(query=query)
            for r in results:
                print(f"[{r['type']}] {r['name']}: {r['description']}")
        
        elif command == "export":
            path = registry.export_catalog()
            print(f"Katalog exportiert nach: {path}")
        
        else:
            print("Verwendung: registry.py [scan|list|search <query>|export]")
    
    registry.close()
