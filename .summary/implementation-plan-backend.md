 Python Backend with Claude Agent SDK - Implementation Plan

     Overview

     Build FastAPI backend with Claude Agent SDK for Identity Platform. Agents coordinate document verification, fraud detection, and 
     compliance before Solana blockchain interaction.

     User Decisions

     | Decision            | Choice                                               |
     |---------------------|------------------------------------------------------|
     | Transaction signing | Frontend wallet signs (backend prepares unsigned tx) |
     | OCR engine          | Tesseract (self-hosted)                              |
     | API Setu            | Mock first, real later                               |
     | MCP pattern         | In-process @tool decorators                          |

     ---
     Directory Structure

     gateway/
     ├── __init__.py
     ├── main.py                    # FastAPI app entry
     ├── config.py                  # Settings, env vars
     ├── routes/
     │   ├── __init__.py
     │   ├── identity.py            # /api/identity/* endpoints
     │   ├── verification.py        # /api/verification/* endpoints
     │   ├── credentials.py         # /api/credentials/* endpoints
     │   └── transaction.py         # /api/transaction/* endpoints
     ├── agents/
     │   ├── __init__.py
     │   ├── definitions.py         # AgentDefinition configs
     │   └── orchestrator.py        # Main verification workflow
     ├── mcp_tools/
     │   ├── __init__.py
     │   ├── document_processor.py  # OCR, field extraction (Tesseract)
     │   ├── pattern_analyzer.py    # Fraud/tampering detection
     │   ├── compliance_rules.py    # Aadhaar Act, DPDP checks
     │   └── solana_client.py       # Blockchain interaction
     ├── models/
     │   ├── __init__.py
     │   ├── identity.py            # Identity Pydantic models
     │   ├── verification.py        # Verification models
     │   └── credentials.py         # Credential models
     ├── services/
     │   ├── __init__.py
     │   ├── ocr.py                 # Tesseract wrapper
     │   ├── apisetu_mock.py        # Mock API Setu responses
     │   └── solana.py              # solders/anchorpy integration
     └── utils/
         ├── __init__.py
         └── hash.py                # Commitment hash generation

     ---
     API Endpoints (12 total)

     Identity Routes (/api/identity)

     | Method | Endpoint         | Handler                                 |
     |--------|------------------|-----------------------------------------|
     | GET    | /{walletAddress} | Fetch identity from Solana              |
     | POST   | /{walletAddress} | Create identity (returns unsigned tx)   |
     | PATCH  | /{walletAddress} | Update commitment (returns unsigned tx) |

     Verification Routes (/api/verification)

     | Method | Endpoint                 | Handler                    |
     |--------|--------------------------|----------------------------|
     | POST   | /{walletAddress}/aadhaar | Start Aadhaar verification |
     | POST   | /{walletAddress}/pan     | Start PAN verification     |
     | GET    | /status/{verificationId} | Check verification status  |

     Credentials Routes (/api/credentials)

     | Method | Endpoint                        | Handler           |
     |--------|---------------------------------|-------------------|
     | GET    | /{walletAddress}                | List credentials  |
     | POST   | /{walletAddress}                | Issue credential  |
     | DELETE | /{walletAddress}/{credentialId} | Revoke credential |

     Transaction Routes (/api/transaction)

     | Method | Endpoint | Handler                                  |
     |--------|----------|------------------------------------------|
     | POST   | /prepare | Prepare unsigned tx for frontend signing |
     | POST   | /submit  | Submit signed tx to Solana               |

     ---
     Agent Architecture

     Orchestrator (Main Agent)

     options = ClaudeAgentOptions(
         allowed_tools=["Task", "Read"],  # Task required for subagents
         agents={
             "document-validator": AgentDefinition(...),
             "fraud-detection": AgentDefinition(...),
             "compliance-monitor": AgentDefinition(...)
         }
     )

     Subagents

     | Agent              | MCP Tools                                                       | Purpose                |
     |--------------------|-----------------------------------------------------------------|------------------------|
     | document-validator | mcp__doc__ocr, mcp__doc__extract_fields                         | Parse Aadhaar/PAN docs |
     | fraud-detection    | mcp__pattern__detect_tampering, mcp__pattern__check_watchlist   | Security analysis      |
     | compliance-monitor | mcp__compliance__check_aadhaar_act, mcp__compliance__check_dpdp | Regulatory checks      |

     Flow

     POST /api/verification/{wallet}/aadhaar
         → Save uploaded document
         → Orchestrator.verify(doc_path, "aadhaar")
             → Task: document-validator (OCR + extract)
             → Task: fraud-detection (tampering check)
             → Task: compliance-monitor (Aadhaar Act)
             → Aggregate results
         → If passed: prepare Solana tx (set_verification_bit)
         → Return verificationId + unsigned tx

     ---
     MCP Tools (In-Process)

     document_processor.py

     @tool(name="ocr", description="Extract text from document image")
     async def ocr_tool(args):
         # Tesseract OCR
         return {"content": [{"type": "text", "text": extracted}]}

     @tool(name="extract_fields", description="Extract structured fields")
     async def extract_fields_tool(args):
         # Regex parsing for Aadhaar/PAN patterns
         return {"content": [{"type": "text", "text": json.dumps(fields)}]}

     pattern_analyzer.py

     @tool(name="detect_tampering", description="Detect image tampering")
     async def detect_tampering_tool(args):
         # Image hash comparison, metadata analysis
         return {"content": [{"type": "text", "text": risk_score}]}

     @tool(name="check_watchlist", description="Check against fraud watchlist")
     async def check_watchlist_tool(args):
         # Mock watchlist check
         return {"content": [{"type": "text", "text": status}]}

     compliance_rules.py

     @tool(name="check_aadhaar_act", description="Verify Aadhaar Act compliance")
     async def check_aadhaar_act_tool(args):
         # Rule-based compliance check
         return {"content": [{"type": "text", "text": compliance_status}]}

     ---
     Pydantic Models

     models/identity.py

     class Identity(BaseModel):
         did: str
         owner: str  # wallet address
         commitment: str  # hash
         verification_bitmap: int
         created_at: int
         updated_at: int

     class CreateIdentityRequest(BaseModel):
         did: Optional[str] = None  # auto-generate if not provided

     models/verification.py

     class AadhaarVerificationData(BaseModel):
         aadhaar_number: str = Field(..., pattern=r"^\d{12}$")
         otp: str = Field(..., pattern=r"^\d{6}$")
         document_hash: Optional[str] = None

     class VerificationStatus(BaseModel):
         verification_id: str
         status: Literal["pending", "processing", "verified", "failed"]
         progress: int  # 0-100
         steps: List[VerificationStep]
         error: Optional[str] = None

     ---
     Solana Integration

     Transaction Preparation (Frontend Signs)

     # services/solana.py
     from solders.message import MessageV0
     from solana.rpc.api import Client

     async def prepare_create_identity_tx(wallet_pubkey: str, commitment: str):
         # Build instruction via anchorpy
         ix = program.instruction["create_identity"](
             commitment_hash=commitment,
             ctx=Context(accounts={...})
         )

         # Get fresh blockhash
         blockhash = client.get_latest_blockhash().value.blockhash

         # Build unsigned message
         message = MessageV0.try_compile(
             payer=Pubkey.from_string(wallet_pubkey),
             instructions=[ix],
             address_lookup_table_accounts=[],
             recent_blockhash=blockhash
         )

         # Return base64 encoded for frontend
         return base64.b64encode(bytes(message)).decode()

     Transaction Submission

     async def submit_signed_tx(signed_tx_base64: str):
         tx = VersionedTransaction.from_bytes(base64.b64decode(signed_tx_base64))
         response = client.send_transaction(tx)
         return str(response.value)  # signature

     ---
     Dependencies

     # requirements.txt
     fastapi>=0.109.0
     uvicorn>=0.27.0
     pydantic>=2.5.0
     python-multipart>=0.0.6

     # Claude Agent SDK
     claude-agent-sdk>=0.1.0

     # OCR
     pytesseract>=0.3.10
     Pillow>=10.0.0

     # Solana
     solders>=0.27.1
     solana>=0.36.10
     anchorpy>=0.19.0

     # Utils
     python-dotenv>=1.0.0
     httpx>=0.26.0

     ---
     Implementation Order

     | Step | Task                           | Files                                    |
     |------|--------------------------------|------------------------------------------|
     | 1    | Project scaffold               | gateway/, requirements.txt, .env.example |
     | 2    | Pydantic models                | models/*.py                              |
     | 3    | FastAPI app + health           | main.py, config.py                       |
     | 4    | MCP tools (document processor) | mcp_tools/document_processor.py          |
     | 5    | OCR service (Tesseract)        | services/ocr.py                          |
     | 6    | Agent definitions              | agents/definitions.py                    |
     | 7    | Orchestrator workflow          | agents/orchestrator.py                   |
     | 8    | Verification routes            | routes/verification.py                   |
     | 9    | Identity routes                | routes/identity.py                       |
     | 10   | Solana service                 | services/solana.py                       |
     | 11   | Transaction routes             | routes/transaction.py                    |
     | 12   | Credentials routes             | routes/credentials.py                    |
     | 13   | Pattern analyzer MCP           | mcp_tools/pattern_analyzer.py            |
     | 14   | Compliance rules MCP           | mcp_tools/compliance_rules.py            |

     ---
     Key SDK Patterns

     Must Include

     - Task in allowed_tools for orchestrator (required for subagents)
     - Subagents cannot have Task tool (no nested spawning)
     - Tool returns: {"content": [{"type": "text", "text": "..."}]}
     - Use async with ClaudeSDKClient for proper cleanup
     - Never break early from message iteration

     Example Orchestrator Call

     async def verify_aadhaar(doc_path: str) -> VerificationResult:
         async for message in query(
             prompt=f"Verify Aadhaar document at {doc_path}. Use document-validator, then fraud-detection, then compliance-monitor.",
             options=ClaudeAgentOptions(
                 mcp_servers={"doc": doc_processor, "pattern": pattern_analyzer, "compliance": compliance_server},
                 allowed_tools=["Task", "mcp__doc__ocr", "mcp__doc__extract_fields"],
                 agents=agent_definitions
             )
         ):
             if hasattr(message, 'result'):
                 return parse_result(message.result)

     ---
     Environment Variables

     # .env
     ANTHROPIC_API_KEY=sk-ant-...
     SOLANA_RPC_URL=https://api.devnet.solana.com
     IDENTITY_PROGRAM_ID=<program-id>
     CREDENTIAL_PROGRAM_ID=<program-id>

     ---
     Files to Create

     | Priority | File                                    | Lines (est) |
     |----------|-----------------------------------------|-------------|
     | P0       | gateway/main.py                         | 50          |
     | P0       | gateway/config.py                       | 30          |
     | P0       | gateway/models/identity.py              | 40          |
     | P0       | gateway/models/verification.py          | 60          |
     | P0       | gateway/mcp_tools/document_processor.py | 80          |
     | P0       | gateway/agents/definitions.py           | 60          |
     | P0       | gateway/agents/orchestrator.py          | 100         |
     | P0       | gateway/routes/verification.py          | 100         |
     | P1       | gateway/routes/identity.py              | 80          |
     | P1       | gateway/services/solana.py              | 120         |
     | P1       | gateway/routes/transaction.py           | 60          |
     | P2       | gateway/mcp_tools/pattern_analyzer.py   | 60          |
     | P2       | gateway/mcp_tools/compliance_rules.py   | 60          |