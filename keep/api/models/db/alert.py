from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import JSON, Column, Field, Relationship, SQLModel

from keep.api.models.db.tenant import Tenant


class Alert(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: str = Field(foreign_key="tenant.id")
    tenant: Tenant = Relationship()
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    provider_type: str
    provider_id: str | None
    event: dict = Field(sa_column=Column(JSON))
    fingerprint: str = Field(index=True)  # Add the fingerprint field with an index

    # Define a one-to-one relationship to AlertEnrichment using alert_fingerprint
    alert_enrichment: "AlertEnrichment" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "and_(Alert.fingerprint == foreign(AlertEnrichment.alert_fingerprint), Alert.tenant_id == AlertEnrichment.tenant_id)",
            "uselist": False,
        }
    )

    class Config:
        arbitrary_types_allowed = True


class AlertEnrichment(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: str = Field(foreign_key="tenant.id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    alert_fingerprint: str = Field(unique=True)
    enrichments: dict = Field(sa_column=Column(JSON))

    alerts: list[Alert] = Relationship(
        back_populates="alert_enrichment",
        sa_relationship_kwargs={
            "primaryjoin": "and_(Alert.fingerprint == AlertEnrichment.alert_fingerprint, Alert.tenant_id == AlertEnrichment.tenant_id)",
            "foreign_keys": "[AlertEnrichment.alert_fingerprint, AlertEnrichment.tenant_id]",
            "uselist": True,
        },
    )

    class Config:
        arbitrary_types_allowed = True
