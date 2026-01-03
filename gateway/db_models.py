from datetime import datetime, timedelta
from sqlalchemy import Column, String, LargeBinary, DateTime, Boolean, Integer, ForeignKey, Index, JSON, Numeric
from sqlalchemy.orm import relationship
from database import Base


class Identity(Base):
    """Identity account on Solana, mirrored in PostgreSQL for efficient querying."""
    __tablename__ = "identities"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Wallet and blockchain identifiers
    wallet_address = Column(String(44), unique=True, nullable=False, index=True)  # Solana pubkey base58
    pda_address = Column(String(44), unique=True, nullable=False, index=True)  # PDA derived from wallet
    owner_pubkey = Column(String(44), nullable=False)  # Full owner public key

    # Commitment and verification
    commitment_hash = Column(LargeBinary(32), nullable=True)  # 32-byte hash for verification
    verification_bits = Column(Integer, default=0)  # Bitfield for credential verification status
    recovery_counter = Column(Integer, default=0)  # Incremented on recovery

    # Metadata
    metadata_uri = Column(String(512), nullable=True)  # IPFS or external storage URI
    bump = Column(Integer, nullable=False)  # PDA bump seed

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    credentials = relationship("Credential", back_populates="owner", cascade="all, delete-orphan")
    grants_as_grantor = relationship(
        "AccessGrant",
        foreign_keys="AccessGrant.grantor_wallet",
        primaryjoin="Identity.wallet_address==AccessGrant.grantor_wallet",
        back_populates="grantor",
        cascade="all, delete-orphan"
    )
    grants_as_grantee = relationship(
        "AccessGrant",
        foreign_keys="AccessGrant.grantee_wallet",
        primaryjoin="Identity.wallet_address==AccessGrant.grantee_wallet",
        back_populates="grantee",
        cascade="all, delete-orphan"
    )
    verifications = relationship("Verification", back_populates="identity", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_identity_wallet", "wallet_address"),
        Index("idx_identity_pda", "pda_address"),
        Index("idx_identity_created_at", "created_at"),
    )


class Credential(Base):
    """Verifiable credential stored on Solana, mirrored in PostgreSQL."""
    __tablename__ = "credentials"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Credential identifiers
    credential_id = Column(String(128), unique=True, nullable=False, index=True)  # Unique credential identifier
    pda_address = Column(String(44), unique=True, nullable=False, index=True)  # PDA for this credential
    owner_wallet = Column(String(44), ForeignKey("identities.wallet_address"), nullable=False, index=True)
    credential_type = Column(String(50), nullable=False, index=True)  # "aadhaar", "pan", "dl", "land", "education"

    # Claims and verification
    claims_hash = Column(LargeBinary(32), nullable=False)  # 32-byte SHA-256 of claims for ZK proof
    issuer_did = Column(String(128), nullable=True)  # DID of credential issuer
    issued_at = Column(DateTime, nullable=False)
    expiry = Column(DateTime, nullable=True)  # NULL means no expiry

    # Metadata and status
    metadata_uri = Column(String(512), nullable=True)  # IPFS URI for full credential data
    revoked = Column(Boolean, default=False, index=True)
    bump = Column(Integer, nullable=False)  # PDA bump seed

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("Identity", back_populates="credentials")
    grants = relationship("AccessGrant", back_populates="credential", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_credential_owner", "owner_wallet"),
        Index("idx_credential_type", "credential_type"),
        Index("idx_credential_pda", "pda_address"),
        Index("idx_credential_expiry", "expiry"),
        Index("idx_credential_revoked", "revoked"),
    )


class AccessGrant(Base):
    """Time-bound access grant for selective disclosure."""
    __tablename__ = "access_grants"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Grant identifiers
    grant_id = Column(String(128), unique=True, nullable=False, index=True)  # Unique grant identifier
    pda_address = Column(String(44), unique=True, nullable=False, index=True)  # PDA for this grant
    credential_pda = Column(String(44), ForeignKey("credentials.pda_address"), nullable=False, index=True)

    # Grantor and grantee wallets (selective disclosure to services)
    grantor_wallet = Column(String(44), nullable=False, index=True)  # Identity owner granting access
    grantee_wallet = Column(String(44), nullable=False, index=True)  # Service or user receiving access

    # Grant details
    purpose = Column(String(256), nullable=True)  # "kyc", "credit_check", "employment_verification", etc.
    expires_at = Column(DateTime, nullable=False)  # Auto-expire after this time
    field_mask = Column(Numeric(20, 0), default=0)  # u64 bitmap for selective field disclosure
    revoked = Column(Boolean, default=False, index=True)
    bump = Column(Integer, nullable=False)  # PDA bump seed

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    credential = relationship("Credential", back_populates="grants")
    grantor = relationship(
        "Identity",
        foreign_keys=[grantor_wallet],
        primaryjoin="AccessGrant.grantor_wallet==Identity.wallet_address",
        back_populates="grants_as_grantor"
    )
    grantee = relationship(
        "Identity",
        foreign_keys=[grantee_wallet],
        primaryjoin="AccessGrant.grantee_wallet==Identity.wallet_address",
        back_populates="grants_as_grantee"
    )

    # Indexes
    __table_args__ = (
        Index("idx_grant_credential", "credential_pda"),
        Index("idx_grant_grantor", "grantor_wallet"),
        Index("idx_grant_grantee", "grantee_wallet"),
        Index("idx_grant_expires_at", "expires_at"),
        Index("idx_grant_revoked", "revoked"),
    )


class Verification(Base):
    """Verification status tracking for credentials across the system."""
    __tablename__ = "verifications"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Verification identifiers
    verification_id = Column(String(128), unique=True, nullable=False, index=True)  # Unique verification tracking ID
    wallet_address = Column(String(44), ForeignKey("identities.wallet_address"), nullable=False, index=True)
    credential_type = Column(String(50), nullable=False, index=True)  # "aadhaar", "pan", etc.

    # Status tracking
    overall_status = Column(String(50), default="pending", index=True)  # "pending", "in_progress", "verified", "failed", "expired"
    progress = Column(Integer, default=0)  # 0-100 percentage
    error_message = Column(String(512), nullable=True)  # Error details if status is "failed"

    # Steps in verification workflow (stored as JSON for flexibility)
    steps = Column(JSON, default=lambda: {
        "api_setu_fetch": None,  # null, "pending", "success", "failed"
        "document_validation": None,
        "fraud_detection": None,
        "compliance_check": None,
        "tokenization": None,
        "blockchain_confirmation": None,
    })

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationship
    identity = relationship("Identity", back_populates="verifications")

    # Indexes
    __table_args__ = (
        Index("idx_verification_wallet", "wallet_address"),
        Index("idx_verification_type", "credential_type"),
        Index("idx_verification_status", "overall_status"),
        Index("idx_verification_created", "created_at"),
    )
