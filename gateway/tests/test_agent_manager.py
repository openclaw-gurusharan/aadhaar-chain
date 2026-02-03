"""Tests for agent manager and verification workflows."""
import pytest
from datetime import datetime

from app.agent_manager import AgentManager, AgentType
from app.models import (
    VerificationStatus,
    VerificationStep,
    AadhaarVerificationData,
    PanVerificationData,
)


@pytest.fixture
async def agent_manager():
    """Create agent manager instance for testing."""
    manager = AgentManager()
    await manager.initialize_agents()
    return manager


@pytest.mark.asyncio
async def test_create_verification(agent_manager):
    """Test creating a new verification request."""
    wallet_address = "test_wallet_123"
    document_type = "aadhaar"
    
    verification_id = await agent_manager.create_verification(
        wallet_address,
        document_type,
    )
    
    assert verification_id == f"{document_type}_{wallet_address}"
    assert verification_id in agent_manager.verification_records
    
    status = agent_manager.verification_records[verification_id]
    assert status.current_step == VerificationStep.document_received
    assert status.progress == 0.0
    assert len(status.steps) == 1


@pytest.mark.asyncio
async def test_get_verification_status(agent_manager):
    """Test getting verification status by ID."""
    wallet_address = "test_wallet_456"
    document_type = "pan"
    
    # Create verification
    verification_id = await agent_manager.create_verification(
        wallet_address,
        document_type,
    )
    
    # Get status
    status = await agent_manager.get_verification_status(verification_id)
    
    assert status is not None
    assert status.verification_id == verification_id
    assert status.wallet_address == wallet_address


@pytest.mark.asyncio
async def test_validate_document_mock(agent_manager):
    """Test document validation (mock)."""
    document_data = b"mock_aadhaar_data"
    document_type = "aadhaar"
    
    result = await agent_manager.validate_document(document_data, document_type)
    
    assert result["success"] is True
    assert result["document_type"] == document_type
    assert "fields" in result
    assert "uid" in result["fields"]  # Aadhaar-specific field
    assert result["fields"]["confidence"] > 0.0


@pytest.mark.asyncio
async def test_detect_fraud_mock(agent_manager):
    """Test fraud detection (mock)."""
    document_fields = {
        "name": "John Doe",
        "dob": "01/01/1985",
        "uid": "123456789012",
    }
    document_type = "aadhaar"
    
    result = await agent_manager.detect_fraud(document_fields, document_type)
    
    assert "risk_score" in result
    assert "risk_level" in result
    assert "recommendation" in result
    assert result["risk_score"] >= 0.0
    assert result["risk_score"] <= 1.0


@pytest.mark.asyncio
async def test_check_compliance_mock(agent_manager):
    """Test compliance check (mock)."""
    document_fields = {
        "name": "John Doe",
        "dob": "01/01/1985",
        "uid": "123456789012",
    }
    document_type = "aadhaar"
    purpose = "kyc_verification"
    
    result = await agent_manager.check_compliance(document_fields, document_type, purpose)
    
    assert "aadhaar_act_compliant" in result
    assert "dpdp_compliant" in result
    assert "violations" in result
    assert "recommendation" in result


@pytest.mark.asyncio
async def test_orchestrate_verification_mock(agent_manager):
    """Test verification workflow orchestration (mock)."""
    wallet_address = "test_wallet_789"
    document_type = "aadhaar"
    document_data = b"mock_aadhaar_data"
    verification_data = AadhaarVerificationData(
        name="John Doe",
        dob="01/01/1985",
        uid="123456789012",
        address="123 Main Street",
    )
    
    status = await agent_manager.orchestrate_verification(
        wallet_address,
        document_type,
        document_data,
        verification_data,
    )
    
    assert status.verification_id == f"{document_type}_{wallet_address}"
    assert status.current_step == VerificationStep.complete
    assert status.progress == 1.0
    assert status.wallet_address == wallet_address
    assert "decision" in status.metadata


@pytest.mark.asyncio
async def test_update_verification_progress(agent_manager):
    """Test updating verification progress."""
    wallet_address = "test_wallet_012"
    document_type = "pan"
    
    # Create verification
    verification_id = await agent_manager.create_verification(
        wallet_address,
        document_type,
    )
    
    # Update progress to parsing
    await agent_manager.update_verification_progress(
        verification_id,
        VerificationStep.parsing,
        0.2,
    )
    
    status = agent_manager.verification_records[verification_id]
    assert status.current_step == VerificationStep.parsing
    assert status.progress == 0.2
    assert VerificationStep.parsing in status.steps


@pytest.mark.asyncio
async def test_cleanup_expired_verifications(agent_manager):
    """Test cleanup of expired verification records."""
    wallet_address = "test_wallet_345"
    document_type = "aadhaar"
    
    # Create old verification (would be expired in production)
    verification_id = await agent_manager.create_verification(
        wallet_address,
        document_type,
    )
    
    # Cleanup (should remove expired records)
    cleaned_count = await agent_manager.cleanup_expired_verifications(days=7)
    
    # In mock implementation, returns 0 (no cleanup yet)
    assert cleaned_count == 0


@pytest.mark.asyncio
async def test_agent_initialization(agent_manager):
    """Test that agents are initialized correctly."""
    assert AgentType.DOCUMENT_VALIDATOR in agent_manager.agents
    assert AgentType.FRAUD_DETECTION in agent_manager.agents
    assert AgentType.COMPLIANCE_MONITOR in agent_manager.agents
    assert AgentType.ORCHESTRATOR in agent_manager.agents
    
    # Check that all agents have status
    for agent_id in agent_manager.agents:
        assert "status" in agent_manager.agents[agent_id]
        assert "name" in agent_manager.agents[agent_id]
