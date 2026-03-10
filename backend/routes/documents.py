"""Health check, patent documents, and user manual download routes."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from datetime import datetime, timezone

from database import db, logger

router = APIRouter()

# Project root where patent/manual files live
PROJECT_ROOT = Path(__file__).parent.parent.parent  # /app/

# ==================== HEALTH CHECK ====================

@router.get("/")
async def root():
    return {"message": "Semantic Vision API is running", "version": "1.0.0"}


@router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/patent-document")
async def get_patent_document():
    """Serve the Provisional Patent Application document as Markdown"""
    from fastapi.responses import FileResponse
    doc_path = PROJECT_ROOT / "PROVISIONAL_PATENT_APPLICATION.md"
    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="Patent document not found")
    return FileResponse(doc_path, media_type="text/markdown", filename="Semantic_Vision_Provisional_Patent_Application.md")


@router.get("/patent-document/pdf")
async def get_patent_document_pdf():
    """Serve the Provisional Patent Application as PDF with CONFIDENTIAL watermark"""
    from fastapi.responses import FileResponse
    pdf_path = PROJECT_ROOT / "Semantic_Vision_Provisional_Patent_Application.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Patent PDF not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename="Semantic_Vision_Provisional_Patent_Application_CONFIDENTIAL.pdf")


@router.get("/patent-strategy/pdf")
async def get_patent_strategy_pdf():
    """Serve the Strategic Patent Analysis as PDF with CONFIDENTIAL watermark"""
    from fastapi.responses import FileResponse
    pdf_path = PROJECT_ROOT / "Semantic_Vision_Patent_Strategy_Analysis.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Strategy PDF not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename="Semantic_Vision_Patent_Strategy_Analysis_CONFIDENTIAL.pdf")


@router.get("/patent-filing-roadmap/pdf")
async def get_patent_filing_roadmap_pdf():
    """Serve the Filing Cost Roadmap as PDF with CONFIDENTIAL watermark"""
    from fastapi.responses import FileResponse
    pdf_path = PROJECT_ROOT / "Semantic_Vision_Filing_Cost_Roadmap.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Filing roadmap PDF not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename="Semantic_Vision_Filing_Cost_Roadmap_CONFIDENTIAL.pdf")


@router.get("/patent-filing-2026/pdf")
async def get_patent_filing_2026_pdf():
    """Serve the Final v4 Patent Filing as PDF"""
    from fastapi.responses import FileResponse
    pdf_path = PROJECT_ROOT / "PATENT_FILING_FINAL_v4.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Patent filing PDF not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename="Semantic_Vision_Provisional_Patent_FINAL_v4_CONFIDENTIAL.pdf")

@router.get("/patent-filing-2026/md")
async def get_patent_filing_2026_md():
    """Serve the Final v4 Patent Filing as Markdown"""
    from fastapi.responses import FileResponse
    md_path = PROJECT_ROOT / "PATENT_FILING_FINAL_v4.md"
    if not md_path.exists():
        raise HTTPException(status_code=404, detail="Patent filing markdown not found")
    return FileResponse(md_path, media_type="text/markdown", filename="Semantic_Vision_Provisional_Patent_FINAL_v4.md")

@router.get("/patent-filing-2026/bundle")
async def get_patent_filing_bundle():
    """Download complete patent filing bundle (MD, PDF, and all screenshots) as ZIP"""
    from fastapi.responses import FileResponse
    zip_path = PROJECT_ROOT / "patent_filing_complete.zip"
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Patent filing bundle not found")
    return FileResponse(zip_path, media_type="application/zip", filename="Semantic_Vision_Patent_Filing_Complete.zip")



@router.get("/user-manual/pdf")
async def get_user_manual_pdf():
    """Serve the Semantic Vision User Manual as PDF"""
    from fastapi.responses import FileResponse
    pdf_path = PROJECT_ROOT / "SEMANTIC_VISION_USER_MANUAL.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="User manual PDF not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename="Semantic_Vision_User_Manual.pdf")

@router.get("/user-manual/md")
async def get_user_manual_md():
    """Serve the User Manual as Markdown"""
    from fastapi.responses import FileResponse
    md_path = PROJECT_ROOT / "SEMANTIC_VISION_USER_MANUAL.md"
    if not md_path.exists():
        raise HTTPException(status_code=404, detail="User manual markdown not found")
    return FileResponse(md_path, media_type="text/markdown", filename="Semantic_Vision_User_Manual.md")


@router.get("/patent/definitive-pdf")
async def get_patent_definitive_pdf():
    """Serve the Definitive v6 Patent Filing as PDF"""
    from fastapi.responses import FileResponse
    pdf_path = PROJECT_ROOT / "PROVISIONAL_PATENT_DEFINITIVE_v6.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Patent PDF not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename="Semantic_Vision_Provisional_Patent_DEFINITIVE_v6.pdf")

@router.get("/patent/definitive-md")
async def get_patent_definitive_md():
    """Serve the Definitive v6 Patent Filing as Markdown"""
    from fastapi.responses import FileResponse
    md_path = PROJECT_ROOT / "PROVISIONAL_PATENT_DEFINITIVE_v6.md"
    if not md_path.exists():
        raise HTTPException(status_code=404, detail="Patent markdown not found")
    return FileResponse(md_path, media_type="text/markdown", filename="Semantic_Vision_Provisional_Patent_DEFINITIVE_v6.md")

@router.get("/patent/definitive-bundle")
async def get_patent_definitive_bundle():
    """Serve the Definitive v6 Patent Filing Bundle (ZIP)"""
    from fastapi.responses import FileResponse
    zip_path = PROJECT_ROOT / "patent_filing_definitive_v6.zip"
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Patent bundle not found")
    return FileResponse(zip_path, media_type="application/zip", filename="Semantic_Vision_Patent_Filing_DEFINITIVE_v6.zip")

@router.get("/patent/screenshots-pdf")
async def get_patent_screenshots_pdf():
    """Serve all 31 patent screenshots as a single PDF"""
    from fastapi.responses import FileResponse
    pdf_path = PROJECT_ROOT / "PATENT_SCREENSHOTS_ALL_FIGURES.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Screenshots PDF not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename="Semantic_Vision_Patent_Screenshots_31_Figures.pdf")


@router.get("/user-manual/master-pdf")
async def get_master_user_manual_pdf():
    """Serve the Master User Manual as PDF"""
    from fastapi.responses import FileResponse
    pdf_path = PROJECT_ROOT / "SEMANTIC_VISION_MASTER_USER_MANUAL.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="User Manual PDF not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename="Semantic_Vision_Master_User_Manual.pdf")

@router.get("/user-manual/master-md")
async def get_master_user_manual_md():
    """Serve the Master User Manual as Markdown"""
    from fastapi.responses import FileResponse
    md_path = PROJECT_ROOT / "SEMANTIC_VISION_MASTER_USER_MANUAL.md"
    if not md_path.exists():
        raise HTTPException(status_code=404, detail="User Manual markdown not found")
    return FileResponse(md_path, media_type="text/markdown", filename="Semantic_Vision_Master_User_Manual.md")




