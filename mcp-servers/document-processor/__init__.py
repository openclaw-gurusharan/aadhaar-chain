"""Document Processor MCP Server for Aadhaar-chain."""
import asyncio
import json
import base64
from typing import Optional, List, Any

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None


class DocumentProcessorMCP:
    """MCP Server for OCR and document field extraction."""
    
    def __init__(self):
        self.tools = [
            {
                "name": "ocr_document",
                "description": "Extract text from image/PDF documents using OCR",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document_data": {"type": "string", "description": "Base64 encoded document data"},
                        "file_type": {"type": "string", "description": "File type (image, pdf)"},
                        "mime_type": {"type": "string", "description": "MIME type"}
                    }
                }
            },
            {
                "name": "extract_aadhaar_fields",
                "description": "Extract structured fields from Aadhaar card (name, DOB, UID)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ocr_text": {"type": "string", "description": "Raw OCR text from document"}
                        "document_type": {"type": "string", "description": "Type: aadhaar"}
                    }
                }
            },
            {
                "name": "extract_pan_fields",
                "description": "Extract structured fields from PAN card (name, PAN number, DOB)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ocr_text": {"type": "string", "description": "Raw OCR text from document"},
                        "document_type": {"type": "string", "description": "Type: pan"}
                    }
                }
            },
            {
                "name": "detect_document_type",
                "description": "Detect if document is Aadhaar, PAN, DL, etc.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ocr_text": {"type": "string", "description": "Raw OCR text from document"}
                    }
                }
            }
        ]
    
    async def _ocr_document_impl(self, ocr_text: str, file_type: str) -> dict:
        """Internal OCR implementation."""
        if pytesseract is None:
            return {
                "success": False,
                "error": "Tesseract not installed. Please install pytesseract and tesseract-ocr",
                "text": None
            }
        
        try:
            # Run OCR with Tesseract
            if file_type == "image":
                # Decode base64 image
                image_data = base64.b64decode(ocr_text.split(',')[1])
                img = Image.open(image_data)
                text = pytesseract.image_to_string(img, lang='hin+eng')
            elif file_type == "pdf":
                # For PDF, we'd need pdf2image or similar library
                # For now, return text extraction from PDF (simplified)
                text = pytesseract.image_to_string(ocr_text.split(',')[1], lang='eng')  # Fallback
            else:
                text = "Unsupported file type: " + file_type
            
            return {
                "success": True,
                "text": text,
                "file_type": file_type
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": None
            }
    
    async def _extract_aadhaar_fields_impl(self, ocr_text: str) -> dict:
        """Extract structured Aadhaar fields from OCR text."""
        # Pattern matching for Aadhaar number (12 digits)
        aadhaar_pattern = r'\b[0-9]{12}\b'
        aadhaar_match = None
        
        try:
            aadhaar_match = aadhaar_pattern.search(ocr_text)
        except Exception:
            pass
        
        # Pattern for date of birth (DD/MM/YYYY format or similar)
        dob_pattern = r'(?:0[1-9]|[12])[\/-](?:0[1-9]|[12])[\/-](?:19|20)\d{2})\d{2,4}'
        dob_match = None
        try:
            dob_match = dob_pattern.search(ocr_text)
        except Exception:
            pass
        
        # Extract name (look for words that could be names)
        # This is simplified - real implementation would need better NLP
        name_match = None
        try:
            # Assume first word after Government/GOVT/UIDAI is name
            words = ocr_text.split()
            for i, word in enumerate(words):
                if word.upper() in ['GOVERNMENT', 'GOVT', 'UIDAI']:
                    # Get next few words as name candidates
                    candidates = words[i+1:i+4]
                    name_match = ' '.join(candidates)
                    break
        except Exception:
            pass
        
        return {
            "success": True,
            "fields": {
                "name": name_match or "Not detected",
                "aadhaar_number": aadhaar_match.group(0) if aadhaar_match else None,
                "date_of_birth": dob_match.group(0) if dob_match else None,
                "raw_ocr_text": ocr_text
            }
        }
    
    async def _extract_pan_fields_impl(self, ocr_text: str) -> dict:
        """Extract structured PAN fields from OCR text."""
        # Pattern: 10 characters, 5 letters + 4 numbers
        # Format: ABCDE1234F
        pan_pattern = r'\b[A-Z]{5}\d{4}[A-Z]{1}\b'
        pan_match = None
        
        try:
            pan_match = pan_pattern.search(ocr_text)
        except Exception:
            pass
        
        # Extract name (look for words before PAN)
        name_match = None
        try:
            words = ocr_text.split()
            pan_index = ocr_text.find(pan_match.group(0)) if pan_match else -1
            if pan_index > 0:
                name_match = ' '.join(words[:pan_index])
        except Exception:
            pass
        
        # Extract DOB (similar to Aadhaar but different format)
        dob_pattern = r'(?:0[1-9]|[12])[\/-](?:0[1-9]|[12])[\/-](?:19|20)\d{2})\d{2,4}'
        dob_match = None
        try:
            dob_match = dob_pattern.search(ocr_text)
        except Exception:
            pass
        
        return {
            "success": True,
            "fields": {
                "name": name_match or "Not detected",
                "pan_number": pan_match.group(0) if pan_match else None,
                "date_of_birth": dob_match.group(0) if dob_match else None,
                "raw_ocr_text": ocr_text
            }
        }
    
    async def _detect_document_type_impl(self, ocr_text: str) -> dict:
        """Detect document type based on OCR text patterns."""
        document_type = "unknown"
        confidence = 0.0
        
        # Aadhaar patterns
        aadhaar_keywords = ['government', 'aadhaar', 'uidai', 'identification', 'unique identification']
        if any(keyword.lower() in ocr_text.lower() for keyword in aadhaar_keywords):
            document_type = "aadhaar"
            confidence += 0.4
        
        # PAN patterns
        pan_keywords = ['permanent account number', 'pan', 'income tax', 'account number']
        if any(keyword.lower() in ocr_text.lower() for keyword in pan_keywords):
            if confidence < 0.4:  # PAN is more specific than Aadhaar
                document_type = "pan"
                confidence = 0.6
        
        # Driving License patterns
        dl_keywords = ['driving license', 'dl', 'transport', 'vehicle']
        if any(keyword.lower() in ocr_text.lower() for keyword in dl_keywords):
            if confidence < 0.6:
                document_type = "driving_license"
                confidence = 0.5
        
        # Other indicators
        if 'uidai' in ocr_text.lower():
            if confidence < 0.5:
                document_type = "aadhaar"
                confidence = 0.8
        
        return {
            "success": True,
            "document_type": document_type,
            "confidence": confidence,
            "indicators": list(kw.lower() for kw in ['government', 'aadhaar', 'pan', 'uidai'] if kw.lower() in ocr_text.lower())
        }
    
    def _parse_tool_args(self, tool_name: str, args: dict) -> tuple:
        """Parse tool arguments and extract file data."""
        if tool_name == "ocr_document":
            return args.get("document_data"), args.get("file_type", "image"), args.get("mime_type")
        elif tool_name in ["extract_aadhaar_fields", "extract_pan_fields"]:
            return args.get("ocr_text")
        elif tool_name == "detect_document_type":
            return args.get("ocr_text")
        else:
            return None
    
    def _create_response(self, tool_name: str, result: dict) -> dict:
        """Create MCP response."""
        if result.get("success", False):
            return {
                "result": None,
                "error": result.get("error", "Unknown error"),
                "isError": True
            }
        else:
            return {
                "result": result.get("text") or result.get("fields") or result.get("document_type"),
                "error": None,
                "isError": False
            }
    
    async def _handle_tool_call(self, tool_name: str, args: dict) -> dict:
        """Handle individual tool call."""
        try:
            if tool_name == "ocr_document":
                document_data, file_type, mime_type = self._parse_tool_args(tool_name, args)
                result = await self._ocr_document_impl(document_data, file_type, mime_type)
                return self._create_response(tool_name, result)
            
            elif tool_name == "extract_aadhaar_fields":
                ocr_text = self._parse_tool_args(tool_name, args)
                result = await self._extract_aadhaar_fields_impl(ocr_text)
                return self._create_response(tool_name, result)
            
            elif tool_name == "extract_pan_fields":
                ocr_text = self._parse_tool_args(tool_name, args)
                result = await self._extract_pan_fields_impl(ocr_text)
                return self._create_response(tool_name, result)
            
            elif tool_name == "detect_document_type":
                ocr_text = self._parse_tool_args(tool_name, args)
                result = await self._detect_document_type_impl(ocr_text)
                return self._create_response(tool_name, result)
            
            else:
                return {
                    "result": None,
                    "error": f"Unknown tool: {tool_name}",
                    "isError": True
                }
        except Exception as e:
            return {
                "result": None,
                "error": f"{tool_name} failed: {str(e)}",
                    "isError": True
            }
    
    async def handle_tool_call(self, tool_name: str, arguments: dict) -> dict:
        """Handle tool call from Claude Agent SDK."""
        return await self._handle_tool_call(tool_name, arguments)


def create_server() -> DocumentProcessorMCP:
    """Factory function to create MCP server instance."""
    return DocumentProcessorMCP()
