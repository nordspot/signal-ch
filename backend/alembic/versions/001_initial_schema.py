"""Initial schema — all Phase 0 tables

Revision ID: 001
Revises:
Create Date: 2026-03-11
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Publishers
    op.create_table(
        "publishers",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("slug", sa.Text(), unique=True, nullable=False),
        sa.Column("publisher_type", sa.String(50), nullable=False),
        sa.Column("media_group", sa.Text()),
        sa.Column("country", sa.String(5), server_default="CH"),
        sa.Column("languages", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("estimated_monthly_reach", sa.Integer()),
        sa.Column("reliability_score", sa.Float(), server_default="0.5"),
        sa.Column("claims_verified_count", sa.Integer(), server_default="0"),
        sa.Column("claims_contradicted_count", sa.Integer(), server_default="0"),
        sa.Column("correction_rate", sa.Float()),
        sa.Column("license_type", sa.String(50)),
        sa.Column("license_expires_at", sa.Date()),
        sa.Column("license_allows_synthesis", sa.Boolean(), server_default="false"),
        sa.Column("license_allows_full_text", sa.Boolean(), server_default="false"),
        sa.Column("political_lean", postgresql.JSONB(), server_default="{}"),
        sa.Column("editorial_independence_score", sa.Float()),
        sa.Column("rss_feeds", postgresql.JSONB(), server_default="[]"),
        sa.Column("api_endpoint", sa.Text()),
        sa.Column("api_key_encrypted", sa.Text()),
        sa.Column("scrape_config", postgresql.JSONB(), server_default="{}"),
    )

    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("email", sa.Text(), unique=True),
        sa.Column("password_hash", sa.Text()),
        sa.Column("auth_provider", sa.String(20)),
        sa.Column("display_name", sa.Text()),
        sa.Column("preferred_language", sa.String(5), server_default="de"),
        sa.Column("canton", sa.String(5)),
        sa.Column("commune_bfs_number", sa.Integer()),
        sa.Column("tier", sa.String(20), server_default="free"),
        sa.Column("stripe_customer_id", sa.Text()),
        sa.Column("tier_expires_at", sa.DateTime(timezone=True)),
        sa.Column("interests", postgresql.JSONB(), server_default="[]"),
        sa.Column("followed_entities", postgresql.ARRAY(sa.Uuid())),
        sa.Column("followed_ios", postgresql.ARRAY(sa.Uuid())),
        sa.Column("blind_spot_sensitivity", sa.Float(), server_default="0.5"),
        sa.Column("notification_config", postgresql.JSONB(), server_default="{}"),
        sa.Column("reputation_score", sa.Float(), server_default="0.0"),
        sa.Column("verified_expertise", postgresql.ARRAY(sa.Text())),
        sa.Column("annotation_accuracy", sa.Float()),
        sa.Column("data_deletion_requested_at", sa.DateTime(timezone=True)),
        sa.Column("consent_personalization", sa.Boolean(), server_default="false"),
        sa.Column("consent_analytics", sa.Boolean(), server_default="false"),
        sa.Column("is_admin", sa.Boolean(), server_default="false"),
        sa.Column("is_editor", sa.Boolean(), server_default="false"),
    )

    # Intelligence Objects
    op.create_table(
        "intelligence_objects",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("status", sa.String(20), server_default="draft"),
        sa.Column("category", sa.String(30), nullable=False),
        sa.Column("subcategory", sa.Text()),
        sa.Column("scope", sa.String(20), server_default="national"),
        sa.Column("canton_codes", postgresql.ARRAY(sa.Text())),
        sa.Column("commune_bfs_numbers", postgresql.ARRAY(sa.Integer())),
        sa.Column("confirmation_density", sa.Float()),
        sa.Column("source_diversity", sa.Float()),
        sa.Column("temporal_freshness", sa.Float()),
        sa.Column("completeness_score", sa.Float()),
        sa.Column("editorial_independence", sa.Float()),
        sa.Column("bias_spectrum", postgresql.JSONB(), server_default="{}"),
        sa.Column("missing_elements", postgresql.ARRAY(sa.Text())),
        sa.Column("current_version_id", sa.Uuid()),
        sa.Column("version_count", sa.Integer(), server_default="0"),
        sa.Column("embedding", Vector(1024)),
        sa.Column("first_reported_at", sa.DateTime(timezone=True)),
        sa.Column("last_source_added_at", sa.DateTime(timezone=True)),
    )
    op.create_index("idx_io_status", "intelligence_objects", ["status"])
    op.create_index("idx_io_category", "intelligence_objects", ["category"])
    op.create_index("idx_io_scope", "intelligence_objects", ["scope"])
    op.create_index("idx_io_created", "intelligence_objects", [sa.text("created_at DESC")])
    op.create_index("idx_io_cantons", "intelligence_objects", ["canton_codes"], postgresql_using="gin")

    # IO Versions
    op.create_table(
        "io_versions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("io_id", sa.Uuid(), sa.ForeignKey("intelligence_objects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("content_de", postgresql.JSONB()),
        sa.Column("content_fr", postgresql.JSONB()),
        sa.Column("content_it", postgresql.JSONB()),
        sa.Column("content_en", postgresql.JSONB()),
        sa.Column("trigger_type", sa.String(30), nullable=False),
        sa.Column("trigger_source_ids", postgresql.ARRAY(sa.Uuid())),
        sa.Column("diff_summary", postgresql.JSONB()),
        sa.Column("reviewed_by", sa.Uuid(), sa.ForeignKey("users.id")),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("review_status", sa.String(20), server_default="pending"),
        sa.UniqueConstraint("io_id", "version_number"),
    )
    op.create_index("idx_io_versions_io_id", "io_versions", ["io_id"])

    # Sources
    op.create_table(
        "sources",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("source_type", sa.String(30), nullable=False),
        sa.Column("license_status", sa.String(30), nullable=False),
        sa.Column("can_display_full_text", sa.Boolean(), server_default="false"),
        sa.Column("can_synthesize_from", sa.Boolean(), server_default="false"),
        sa.Column("requires_link_back", sa.Boolean(), server_default="true"),
        sa.Column("original_url", sa.Text(), nullable=False),
        sa.Column("original_title", sa.Text()),
        sa.Column("original_language", sa.String(10)),
        sa.Column("original_published_at", sa.DateTime(timezone=True)),
        sa.Column("full_text_encrypted", sa.Text()),
        sa.Column("snippet", sa.Text()),
        sa.Column("publisher_id", sa.Uuid(), sa.ForeignKey("publishers.id")),
        sa.Column("attribution_text", sa.Text(), nullable=False),
        sa.Column("author_name", sa.Text()),
        sa.Column("publisher_reliability_score", sa.Float()),
        sa.Column("processed", sa.Boolean(), server_default="false"),
        sa.Column("assigned_io_id", sa.Uuid(), sa.ForeignKey("intelligence_objects.id")),
        sa.Column("embedding", Vector(1024)),
        sa.Column("extracted_entities", postgresql.JSONB(), server_default="[]"),
    )
    op.create_index("idx_sources_publisher", "sources", ["publisher_id"])
    op.create_index("idx_sources_published", "sources", [sa.text("original_published_at DESC")])
    op.create_index("idx_sources_unprocessed", "sources", ["processed"], postgresql_where=sa.text("processed = false"))

    # Entities
    op.create_table(
        "entities",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("entity_type", sa.String(30), nullable=False),
        sa.Column("canonical_name", sa.Text(), nullable=False),
        sa.Column("names_de", postgresql.ARRAY(sa.Text())),
        sa.Column("names_fr", postgresql.ARRAY(sa.Text())),
        sa.Column("names_it", postgresql.ARRAY(sa.Text())),
        sa.Column("names_en", postgresql.ARRAY(sa.Text())),
        sa.Column("aliases", postgresql.ARRAY(sa.Text())),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
        sa.Column("wikidata_id", sa.Text()),
        sa.Column("lobbywatch_id", sa.Text()),
        sa.Column("sogc_uid", sa.Text()),
        sa.Column("bfs_number", sa.Integer()),
        sa.Column("embedding", Vector(1024)),
        sa.Column("mention_count", sa.Integer(), server_default="0"),
        sa.Column("last_mentioned_at", sa.DateTime(timezone=True)),
        sa.Column("coi_data", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("idx_entities_type", "entities", ["entity_type"])
    op.create_index("idx_entities_wikidata", "entities", ["wikidata_id"], postgresql_where=sa.text("wikidata_id IS NOT NULL"))
    op.create_index("idx_entities_sogc", "entities", ["sogc_uid"], postgresql_where=sa.text("sogc_uid IS NOT NULL"))

    # Entity Relations
    op.create_table(
        "entity_relations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("source_entity_id", sa.Uuid(), sa.ForeignKey("entities.id"), nullable=False),
        sa.Column("target_entity_id", sa.Uuid(), sa.ForeignKey("entities.id"), nullable=False),
        sa.Column("relation_type", sa.String(30), nullable=False),
        sa.Column("confidence", sa.Float(), server_default="0.5"),
        sa.Column("source_io_ids", postgresql.ARRAY(sa.Uuid())),
        sa.Column("valid_from", sa.Date()),
        sa.Column("valid_to", sa.Date()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("idx_er_source", "entity_relations", ["source_entity_id"])
    op.create_index("idx_er_target", "entity_relations", ["target_entity_id"])

    # IO-Source mapping
    op.create_table(
        "io_sources",
        sa.Column("io_id", sa.Uuid(), sa.ForeignKey("intelligence_objects.id"), primary_key=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), primary_key=True),
        sa.Column("added_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("relevance_score", sa.Float(), server_default="0.5"),
        sa.Column("contribution_type", sa.String(30), nullable=False),
    )

    # IO-Entity mapping
    op.create_table(
        "io_entities",
        sa.Column("io_id", sa.Uuid(), sa.ForeignKey("intelligence_objects.id"), primary_key=True),
        sa.Column("entity_id", sa.Uuid(), sa.ForeignKey("entities.id"), primary_key=True),
        sa.Column("role", sa.Text()),
        sa.Column("sentiment", sa.Float()),
        sa.Column("mention_count", sa.Integer(), server_default="1"),
    )

    # User IO Interactions
    op.create_table(
        "user_io_interactions",
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("io_id", sa.Uuid(), sa.ForeignKey("intelligence_objects.id"), primary_key=True),
        sa.Column("first_read_version_id", sa.Uuid()),
        sa.Column("first_read_at", sa.DateTime(timezone=True)),
        sa.Column("last_read_version_id", sa.Uuid()),
        sa.Column("last_read_at", sa.DateTime(timezone=True)),
        sa.Column("shared_version_id", sa.Uuid()),
        sa.Column("shared_at", sa.DateTime(timezone=True)),
        sa.Column("shared_via", sa.Text()),
        sa.Column("reading_time_seconds", sa.Integer()),
        sa.Column("scroll_depth", sa.Float()),
        sa.Column("bookmarked", sa.Boolean(), server_default="false"),
        sa.Column("clipped_to_mindmap", sa.Boolean(), server_default="false"),
        sa.Column("notified_of_update", sa.Boolean(), server_default="false"),
        sa.Column("notified_at", sa.DateTime(timezone=True)),
    )

    # Annotations
    op.create_table(
        "annotations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("io_id", sa.Uuid(), sa.ForeignKey("intelligence_objects.id"), nullable=False),
        sa.Column("io_version_id", sa.Uuid(), sa.ForeignKey("io_versions.id"), nullable=False),
        sa.Column("annotation_level", sa.String(20), nullable=False),
        sa.Column("target_selector", postgresql.JSONB()),
        sa.Column("annotation_type", sa.String(30), nullable=False),
        sa.Column("author_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("evidence_urls", postgresql.ARRAY(sa.Text())),
        sa.Column("useful_votes", sa.Integer(), server_default="0"),
        sa.Column("not_useful_votes", sa.Integer(), server_default="0"),
        sa.Column("status", sa.String(20), server_default="active"),
        sa.Column("moderation_reason", sa.Text()),
        sa.Column("fact_check_verdict", sa.String(20)),
    )
    op.create_index("idx_annotations_io", "annotations", ["io_id"])
    op.create_index("idx_annotations_author", "annotations", ["author_id"])

    # Votes and Initiatives
    op.create_table(
        "votes_and_initiatives",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("vote_type", sa.String(30), nullable=False),
        sa.Column("level", sa.String(20), nullable=False),
        sa.Column("canton", sa.String(5)),
        sa.Column("commune_bfs_number", sa.Integer()),
        sa.Column("title_de", sa.Text()),
        sa.Column("title_fr", sa.Text()),
        sa.Column("title_it", sa.Text()),
        sa.Column("official_url", sa.Text()),
        sa.Column("vote_date", sa.Date()),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("result", postgresql.JSONB()),
        sa.Column("synthesized_io_id", sa.Uuid()),
        sa.Column("pro_arguments", postgresql.JSONB()),
        sa.Column("contra_arguments", postgresql.JSONB()),
        sa.Column("financial_impact", postgresql.JSONB()),
        sa.Column("historical_precedents", postgresql.ARRAY(sa.Uuid())),
        sa.Column("curia_vista_id", sa.Text()),
    )

    # Agency Publications
    op.create_table(
        "agency_publications",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("agency_id", sa.Uuid(), sa.ForeignKey("publishers.id"), nullable=False),
        sa.Column("title_de", sa.Text()),
        sa.Column("title_fr", sa.Text()),
        sa.Column("title_it", sa.Text()),
        sa.Column("original_url", sa.Text(), nullable=False),
        sa.Column("publication_date", sa.Date()),
        sa.Column("publication_type", sa.String(30)),
        sa.Column("raw_content_path", sa.Text()),
        sa.Column("synthesized_io_id", sa.Uuid()),
        sa.Column("synthesis_status", sa.String(20), server_default="pending"),
        sa.Column("views_count", sa.Integer(), server_default="0"),
        sa.Column("unique_readers", sa.Integer(), server_default="0"),
        sa.Column("avg_reading_time_seconds", sa.Float()),
        sa.Column("shares_count", sa.Integer(), server_default="0"),
    )
    op.create_index("idx_agency_pub_agency", "agency_publications", ["agency_id"])

    # Mindmap tables
    op.create_table(
        "mindmap_boards",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("is_shared", sa.Boolean(), server_default="false"),
        sa.Column("shared_with", postgresql.ARRAY(sa.Uuid())),
    )

    op.create_table(
        "mindmap_nodes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("board_id", sa.Uuid(), sa.ForeignKey("mindmap_boards.id", ondelete="CASCADE"), nullable=False),
        sa.Column("node_type", sa.String(20), nullable=False),
        sa.Column("io_id", sa.Uuid()),
        sa.Column("entity_id", sa.Uuid()),
        sa.Column("title", sa.Text()),
        sa.Column("body", sa.Text()),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
        sa.Column("position_x", sa.Float(), server_default="0"),
        sa.Column("position_y", sa.Float(), server_default="0"),
        sa.Column("width", sa.Float()),
        sa.Column("height", sa.Float()),
        sa.Column("color", sa.Text()),
    )

    op.create_table(
        "mindmap_edges",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("board_id", sa.Uuid(), sa.ForeignKey("mindmap_boards.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_node_id", sa.Uuid(), sa.ForeignKey("mindmap_nodes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_node_id", sa.Uuid(), sa.ForeignKey("mindmap_nodes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("label", sa.Text()),
        sa.Column("edge_type", sa.String(20), server_default="manual"),
    )


def downgrade() -> None:
    op.drop_table("mindmap_edges")
    op.drop_table("mindmap_nodes")
    op.drop_table("mindmap_boards")
    op.drop_table("agency_publications")
    op.drop_table("votes_and_initiatives")
    op.drop_table("annotations")
    op.drop_table("user_io_interactions")
    op.drop_table("io_entities")
    op.drop_table("io_sources")
    op.drop_table("sources")
    op.drop_table("entity_relations")
    op.drop_table("entities")
    op.drop_table("io_versions")
    op.drop_table("intelligence_objects")
    op.drop_table("users")
    op.drop_table("publishers")
    op.execute("DROP EXTENSION IF EXISTS vector")
