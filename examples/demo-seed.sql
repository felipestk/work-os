-- Work OS demo seed data
-- Safe generic fixture data for local testing and screenshots.

INSERT INTO customers (customer_code, customer_type, name, legal_name, website, industry, country, status, notes)
VALUES
  ('CUST0001', 'private', 'Internal Lab', NULL, NULL, 'Internal', 'PT', 'active', 'Private/internal testing customer'),
  ('CUST0002', 'company', 'Northwind Systems', 'Northwind Systems Ltd.', 'https://northwind.example', 'Industrial Software', 'PT', 'active', 'Demo B2B customer');

INSERT INTO contacts (customer_id, first_name, last_name, role, email, phone, linkedin, is_primary, notes)
VALUES
  (2, 'Ana', 'Silva', 'Operations Lead', 'ana.silva@northwind.example', '+351000000001', 'https://linkedin.example/ana-silva', 1, 'Primary demo contact'),
  (2, 'Rui', 'Costa', 'Finance Manager', 'rui.costa@northwind.example', '+351000000002', 'https://linkedin.example/rui-costa', 0, 'Secondary demo contact');

INSERT INTO projects (id, slug, customer_id, title, status, objective, summary, folder_path, owner)
VALUES
  ('PR0001', 'internal-work-os-validation', 1, 'Internal Work OS validation', 'active', 'Validate the base Work OS workflow', 'Generic internal validation project for testing.', './work/projects/PR0001-internal-work-os-validation', 'demo'),
  ('PR0002', 'northwind-pilot-offer', 2, 'Northwind pilot offer', 'active', 'Prepare pilot commercial proposal', 'Demo customer project connecting customer, offer, and activity records.', './work/projects/PR0002-northwind-pilot-offer', 'demo');

INSERT INTO project_events (project_id, event_type, note, metadata_json)
VALUES
  ('PR0001', 'created', 'Project created from demo seed', '{"actor":"demo-seed"}'),
  ('PR0001', 'updated', 'Validated core setup for internal flow', '{"actor":"demo-seed"}'),
  ('PR0002', 'created', 'Project created from demo seed', '{"actor":"demo-seed"}'),
  ('PR0002', 'updated', 'Drafted pilot scope and offer path', '{"actor":"demo-seed"}');

INSERT INTO offers (offer_code, customer_id, project_id, contact_id, title, status, currency, amount_subtotal, amount_tax, amount_total, valid_until, summary, assumptions, current_version_no)
VALUES
  ('QDEMO001', 2, 'PR0002', 1, 'Northwind Pilot Proposal', 'draft', 'EUR', 8000, 1840, 9840, '2026-04-15T00:00:00Z', 'Pilot scope for process automation and reporting.', 'Assumes shared access to sample operational data.', 1);

INSERT INTO offer_versions (offer_id, version_no, change_summary, snapshot_json)
VALUES
  (1, 1, 'Initial demo version', '{"offer_code":"QDEMO001","title":"Northwind Pilot Proposal","status":"draft","currency":"EUR","amount_subtotal":8000,"amount_tax":1840,"amount_total":9840,"summary":"Pilot scope for process automation and reporting.","assumptions":"Assumes shared access to sample operational data.","line_items":[]}');

INSERT INTO offer_line_items (offer_id, version_no, billing_type, name, description, quantity, unit, unit_price, tax_rate, line_subtotal, line_tax, line_total, currency, sort_order)
VALUES
  (1, 1, 'one_time', 'Discovery and setup', 'Kickoff, discovery, and initial environment setup', 1, 'project', 2500, 23, 2500, 575, 3075, 'EUR', 1),
  (1, 1, 'one_time', 'Workflow implementation', 'Initial automation and reporting implementation', 1, 'project', 5500, 23, 5500, 1265, 6765, 'EUR', 2);

INSERT INTO activities (customer_id, project_id, offer_id, contact_id, activity_type, direction, subject, body, source_ref, thread_id, message_id, dedup_hash, happened_at)
VALUES
  (1, 'PR0001', NULL, NULL, 'note', 'internal', 'Validation note', 'Confirmed that customer, project, and event creation work end-to-end.', 'demo-seed', NULL, NULL, 'demo-activity-1', '2026-03-11T09:00:00Z'),
  (2, 'PR0002', NULL, 1, 'meeting', 'outbound', 'Pilot scoping meeting', 'Discussed pilot scope, timeline, and next commercial step.', 'demo-seed', NULL, NULL, 'demo-activity-2', '2026-03-11T09:10:00Z'),
  (2, 'PR0002', 1, 2, 'email', 'outbound', 'Sent draft pricing summary', 'Shared first-pass pricing summary for review before formal send.', 'demo-seed', NULL, NULL, 'demo-activity-3', '2026-03-11T09:20:00Z');

INSERT INTO aliases (entity_type, entity_ref, alias, alias_type)
VALUES
  ('customer', 'CUST0002', 'northwind', 'keyword'),
  ('project', 'PR0002', 'pilot', 'keyword'),
  ('offer', 'QDEMO001', 'northwind-pilot', 'keyword');
