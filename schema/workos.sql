PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS customers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_code TEXT NOT NULL UNIQUE,
  customer_type TEXT NOT NULL CHECK (customer_type IN ('company','private')),
  name TEXT NOT NULL,
  legal_name TEXT,
  website TEXT,
  industry TEXT,
  country TEXT,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive','archived')),
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  UNIQUE(customer_type, name)
);

CREATE TABLE IF NOT EXISTS contacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  first_name TEXT,
  last_name TEXT,
  role TEXT,
  email TEXT,
  phone TEXT,
  linkedin TEXT,
  is_primary INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0,1)),
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY CHECK (id GLOB 'PR[0-9][0-9][0-9][0-9]'),
  slug TEXT NOT NULL,
  customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
  title TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','blocked','completed','archived')),
  objective TEXT,
  summary TEXT,
  folder_path TEXT NOT NULL UNIQUE,
  owner TEXT,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS project_events (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL CHECK (event_type IN ('created','updated','note','blocked','completed','reopened','status_changed','artifact_added','subagent_handoff')),
  note TEXT,
  metadata_json TEXT,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS offers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  offer_code TEXT NOT NULL UNIQUE,
  customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  project_id TEXT REFERENCES projects(id) ON DELETE SET NULL,
  contact_id INTEGER REFERENCES contacts(id) ON DELETE SET NULL,
  title TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','sent','accepted','rejected','expired','revised','archived')),
  currency TEXT NOT NULL DEFAULT 'EUR',
  amount_subtotal REAL,
  amount_tax REAL,
  amount_total REAL,
  sent_at TEXT,
  valid_until TEXT,
  decision_at TEXT,
  summary TEXT,
  assumptions TEXT,
  current_version_no INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS offer_versions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  offer_id INTEGER NOT NULL REFERENCES offers(id) ON DELETE CASCADE,
  version_no INTEGER NOT NULL,
  change_summary TEXT NOT NULL,
  snapshot_json TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  UNIQUE(offer_id, version_no)
);

CREATE TABLE IF NOT EXISTS offer_line_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  offer_id INTEGER NOT NULL REFERENCES offers(id) ON DELETE CASCADE,
  version_no INTEGER NOT NULL,
  billing_type TEXT NOT NULL CHECK (billing_type IN ('one_time','recurring')),
  name TEXT NOT NULL,
  description TEXT,
  quantity REAL NOT NULL DEFAULT 1,
  unit TEXT,
  unit_price REAL NOT NULL,
  tax_rate REAL,
  line_subtotal REAL NOT NULL,
  line_tax REAL NOT NULL,
  line_total REAL NOT NULL,
  currency TEXT NOT NULL DEFAULT 'EUR',
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS activities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  project_id TEXT REFERENCES projects(id) ON DELETE SET NULL,
  offer_id INTEGER REFERENCES offers(id) ON DELETE SET NULL,
  contact_id INTEGER REFERENCES contacts(id) ON DELETE SET NULL,
  activity_type TEXT NOT NULL CHECK (activity_type IN ('note','email','call','meeting','whatsapp','telegram','decision','summary','task','other')),
  direction TEXT CHECK (direction IN ('inbound','outbound','internal')),
  subject TEXT,
  body TEXT NOT NULL,
  source_ref TEXT,
  thread_id TEXT,
  message_id TEXT,
  dedup_hash TEXT,
  happened_at TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS aliases (
  alias_id INTEGER PRIMARY KEY AUTOINCREMENT,
  entity_type TEXT NOT NULL CHECK (entity_type IN ('customer','project','offer')),
  entity_ref TEXT NOT NULL,
  alias TEXT NOT NULL,
  alias_type TEXT NOT NULL DEFAULT 'keyword' CHECK (alias_type IN ('client','keyword','tag','legacy')),
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  UNIQUE(entity_type, entity_ref, alias, alias_type)
);

CREATE TABLE IF NOT EXISTS attachments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entity_type TEXT NOT NULL CHECK (entity_type IN ('activity','offer','customer','contact','project')),
  entity_ref TEXT NOT NULL,
  file_path TEXT NOT NULL,
  mime_type TEXT,
  checksum TEXT,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE INDEX IF NOT EXISTS idx_contacts_customer ON contacts(customer_id);
CREATE INDEX IF NOT EXISTS idx_projects_customer_updated ON projects(customer_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_project_events_project_created ON project_events(project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_offers_customer_updated ON offers(customer_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_offers_project_updated ON offers(project_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_offers_status ON offers(status);
CREATE INDEX IF NOT EXISTS idx_offer_versions_offer_version ON offer_versions(offer_id, version_no DESC);
CREATE INDEX IF NOT EXISTS idx_offer_line_items_offer_version ON offer_line_items(offer_id, version_no, sort_order, id);
CREATE INDEX IF NOT EXISTS idx_activities_customer_happened ON activities(customer_id, happened_at DESC);
CREATE INDEX IF NOT EXISTS idx_activities_project_happened ON activities(project_id, happened_at DESC);
CREATE INDEX IF NOT EXISTS idx_activities_offer_happened ON activities(offer_id, happened_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_activities_dedup_hash ON activities(dedup_hash) WHERE dedup_hash IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_aliases_alias ON aliases(alias);

CREATE VIRTUAL TABLE IF NOT EXISTS activity_search USING fts5(subject, body, content='activities', content_rowid='id');
CREATE VIRTUAL TABLE IF NOT EXISTS offer_search USING fts5(title, summary, assumptions, content='offers', content_rowid='id');

CREATE TRIGGER IF NOT EXISTS activities_ai AFTER INSERT ON activities BEGIN
  INSERT INTO activity_search(rowid, subject, body) VALUES (new.id, new.subject, new.body);
END;
CREATE TRIGGER IF NOT EXISTS activities_ad AFTER DELETE ON activities BEGIN
  INSERT INTO activity_search(activity_search, rowid, subject, body) VALUES('delete', old.id, old.subject, old.body);
END;
CREATE TRIGGER IF NOT EXISTS activities_au AFTER UPDATE ON activities BEGIN
  INSERT INTO activity_search(activity_search, rowid, subject, body) VALUES('delete', old.id, old.subject, old.body);
  INSERT INTO activity_search(rowid, subject, body) VALUES (new.id, new.subject, new.body);
END;

CREATE TRIGGER IF NOT EXISTS offers_ai AFTER INSERT ON offers BEGIN
  INSERT INTO offer_search(rowid, title, summary, assumptions) VALUES (new.id, new.title, new.summary, new.assumptions);
END;
CREATE TRIGGER IF NOT EXISTS offers_ad AFTER DELETE ON offers BEGIN
  INSERT INTO offer_search(offer_search, rowid, title, summary, assumptions) VALUES('delete', old.id, old.title, old.summary, old.assumptions);
END;
CREATE TRIGGER IF NOT EXISTS offers_au AFTER UPDATE ON offers BEGIN
  INSERT INTO offer_search(offer_search, rowid, title, summary, assumptions) VALUES('delete', old.id, old.title, old.summary, old.assumptions);
  INSERT INTO offer_search(rowid, title, summary, assumptions) VALUES (new.id, new.title, new.summary, new.assumptions);
END;

CREATE TRIGGER IF NOT EXISTS trg_customers_updated_at AFTER UPDATE ON customers BEGIN
  UPDATE customers SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id = NEW.id;
END;
CREATE TRIGGER IF NOT EXISTS trg_contacts_updated_at AFTER UPDATE ON contacts BEGIN
  UPDATE contacts SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id = NEW.id;
END;
CREATE TRIGGER IF NOT EXISTS trg_projects_updated_at AFTER UPDATE ON projects BEGIN
  UPDATE projects SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id = NEW.id;
END;
CREATE TRIGGER IF NOT EXISTS trg_offers_updated_at AFTER UPDATE ON offers BEGIN
  UPDATE offers SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id = NEW.id;
END;
CREATE TRIGGER IF NOT EXISTS trg_offer_line_items_updated_at AFTER UPDATE ON offer_line_items BEGIN
  UPDATE offer_line_items SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id = NEW.id;
END;
CREATE TRIGGER IF NOT EXISTS trg_activities_updated_at AFTER UPDATE ON activities BEGIN
  UPDATE activities SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id = NEW.id;
END;
