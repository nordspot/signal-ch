-- Government publishers (Phase 0 - zero licensing cost)
INSERT OR IGNORE INTO publishers (id, name, slug, publisher_type, languages, reliability_score, license_type, license_allows_synthesis, license_allows_full_text, rss_feeds, scrape_config, created_at) VALUES
('gov-admin-ch', 'Schweizerische Eidgenossenschaft', 'admin-ch', 'government', '["de","fr","it"]', 0.95, 'open_government', 1, 1, '[]', '{}', datetime('now')),
('gov-parlament', 'Schweizer Parlament', 'parlament-ch', 'government', '["de","fr","it"]', 0.95, 'open_government', 1, 1, '[{"url":"https://www.parlament.ch/de/rss/Pages/mm.aspx","language":"de"}]', '{}', datetime('now')),
('gov-bk', 'Bundeskanzlei', 'bk-admin-ch', 'government', '["de","fr","it"]', 0.95, 'open_government', 1, 1, '[]', '{}', datetime('now')),
('gov-eda', 'EDA', 'eda-admin-ch', 'government', '["de","fr","it","en"]', 0.95, 'open_government', 1, 1, '[]', '{}', datetime('now')),
('gov-edi', 'EDI', 'edi-admin-ch', 'government', '["de","fr","it"]', 0.95, 'open_government', 1, 1, '[]', '{}', datetime('now')),
('gov-ejpd', 'EJPD', 'ejpd-admin-ch', 'government', '["de","fr","it"]', 0.95, 'open_government', 1, 1, '[]', '{}', datetime('now')),
('gov-vbs', 'VBS', 'vbs-admin-ch', 'government', '["de","fr","it"]', 0.95, 'open_government', 1, 1, '[]', '{}', datetime('now')),
('gov-efd', 'EFD', 'efd-admin-ch', 'government', '["de","fr","it"]', 0.95, 'open_government', 1, 1, '[]', '{}', datetime('now')),
('gov-wbf', 'WBF', 'wbf-admin-ch', 'government', '["de","fr","it"]', 0.95, 'open_government', 1, 1, '[]', '{}', datetime('now')),
('gov-uvek', 'UVEK', 'uvek-admin-ch', 'government', '["de","fr","it"]', 0.95, 'open_government', 1, 1, '[]', '{}', datetime('now')),
('gov-bfs', 'Bundesamt für Statistik', 'bfs-admin-ch', 'government', '["de","fr","it","en"]', 0.95, 'open_government', 1, 1, '[{"url":"https://www.bfs.admin.ch/bfs/de/home/aktuell/neue-veroeffentlichungen.gnpdetail.2019-374.rss.xml","language":"de"}]', '{}', datetime('now')),
('gov-seco', 'SECO', 'seco-admin-ch', 'government', '["de","fr","it"]', 0.95, 'open_government', 1, 1, '[]', '{}', datetime('now')),
('gov-bag', 'BAG', 'bag-admin-ch', 'government', '["de","fr","it"]', 0.95, 'open_government', 1, 1, '[]', '{}', datetime('now')),
('gov-bafu', 'BAFU', 'bafu-admin-ch', 'government', '["de","fr","it"]', 0.95, 'open_government', 1, 1, '[]', '{}', datetime('now')),
('gov-snb', 'Schweizerische Nationalbank', 'snb', 'government', '["de","fr","it","en"]', 0.95, 'open_government', 1, 1, '[{"url":"https://www.snb.ch/de/rss/mmNewsletter","language":"de"}]', '{}', datetime('now')),
('gov-finma', 'FINMA', 'finma', 'government', '["de","fr","it","en"]', 0.90, 'open_government', 1, 1, '[]', '{}', datetime('now')),
('gov-shab', 'SHAB', 'shab', 'government', '["de","fr","it"]', 0.90, 'open_government', 1, 1, '[]', '{}', datetime('now')),
('gov-opendata', 'opendata.swiss', 'opendata-swiss', 'government', '["de","fr","it","en"]', 0.90, 'open_government', 1, 1, '[]', '{}', datetime('now')),
('gov-fedlex', 'Fedlex', 'fedlex', 'government', '["de","fr","it"]', 0.95, 'open_government', 1, 1, '[]', '{}', datetime('now'));

-- Media publishers (Phase 1 - require license review)
INSERT OR IGNORE INTO publishers (id, name, slug, publisher_type, media_group, languages, reliability_score, license_type, license_allows_synthesis, license_allows_full_text, rss_feeds, scrape_config, created_at) VALUES
('media-srf', 'SRF', 'srf', 'public_media', 'SRG SSR', '["de"]', 0.85, 'restricted', 0, 0, '[{"url":"https://www.srf.ch/news/bnf/rss/1646","language":"de","category":"news"}]', '{}', datetime('now')),
('media-rts', 'RTS', 'rts', 'public_media', 'SRG SSR', '["fr"]', 0.85, 'restricted', 0, 0, '[{"url":"https://www.rts.ch/info/rss","language":"fr","category":"news"}]', '{}', datetime('now')),
('media-rsi', 'RSI', 'rsi', 'public_media', 'SRG SSR', '["it"]', 0.85, 'restricted', 0, 0, '[]', '{}', datetime('now')),
('media-nzz', 'Neue Zürcher Zeitung', 'nzz', 'private_media', 'NZZ Mediengruppe', '["de"]', 0.85, 'paywall', 0, 0, '[{"url":"https://www.nzz.ch/recent.rss","language":"de"}]', '{}', datetime('now')),
('media-tagi', 'Tages-Anzeiger', 'tagi', 'private_media', 'TX Group', '["de"]', 0.80, 'paywall', 0, 0, '[{"url":"https://www.tagesanzeiger.ch/rss","language":"de"}]', '{}', datetime('now')),
('media-blick', 'Blick', 'blick', 'private_media', 'Ringier', '["de"]', 0.70, 'restricted', 0, 0, '[{"url":"https://www.blick.ch/news/rss","language":"de"}]', '{}', datetime('now')),
('media-tdg', 'Tribune de Genève', 'tdg', 'private_media', 'TX Group', '["fr"]', 0.80, 'paywall', 0, 0, '[]', '{}', datetime('now')),
('media-letemps', 'Le Temps', 'letemps', 'private_media', 'Ringier', '["fr"]', 0.85, 'paywall', 0, 0, '[]', '{}', datetime('now')),
('media-watson', 'Watson', 'watson', 'private_media', 'CH Media', '["de","fr"]', 0.70, 'restricted', 0, 0, '[]', '{}', datetime('now')),
('media-swissinfo', 'swissinfo.ch', 'swissinfo', 'public_media', 'SRG SSR', '["de","fr","it","en"]', 0.85, 'cc_by_nc_nd', 1, 0, '[{"url":"https://www.swissinfo.ch/ger/alle-news-in-kuerze/rss","language":"de"}]', '{}', datetime('now')),
('wire-sda', 'Keystone-SDA', 'sda', 'wire_service', NULL, '["de","fr","it"]', 0.90, 'licensed', 0, 0, '[]', '{}', datetime('now'));
