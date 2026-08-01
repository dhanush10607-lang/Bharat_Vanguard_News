import asyncio
import os
import uuid
from datetime import datetime
from calendar import month_name
from fpdf import FPDF
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from shared.database import AsyncSessionLocal
from shared.models.articles import Article
from shared.models.magazines import Magazine
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

class PDFMagazine(FPDF):
    def header(self):
        # Header banner
        self.set_fill_color(15, 22, 41) # Dark blue
        self.rect(0, 0, 210, 30, 'F')
        self.set_y(10)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'BHARAT VANGUARD NEWS', 0, 1, 'C')
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

async def generate_monthly_magazine():
    """Generates a PDF magazine for the current month's top news and uploads it."""
    print("Starting Monthly Magazine Generation...")
    
    now = datetime.utcnow()
    month = now.month
    year = now.year
    month_str = month_name[month]
    
    # 1. Fetch top articles from DB
    async with AsyncSessionLocal() as db:
        stmt = (
            select(Article)
            .filter(Article.status == 'published')
            .order_by(Article.published_at.desc())
            .limit(10)
        )
        result = await db.execute(stmt)
        articles = result.scalars().all()
        
        if not articles:
            print("No articles found to generate magazine.")
            return

        # 2. Generate PDF
        pdf = PDFMagazine()
        pdf.add_page()
        
        # Cover Page
        pdf.set_y(60)
        pdf.set_font('Helvetica', 'B', 36)
        pdf.set_text_color(20, 20, 20)
        pdf.cell(0, 20, f'THE {month_str.upper()} ISSUE', 0, 1, 'C')
        pdf.set_font('Helvetica', '', 16)
        pdf.cell(0, 10, f'{year} Edition', 0, 1, 'C')
        
        pdf.set_y(100)
        pdf.set_font('Helvetica', 'I', 14)
        pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(0, 10, 'An AI-curated collection of the most important stories verified by Bharat Vanguard News.', align='C')
        
        # Articles
        for article in articles:
            pdf.add_page()
            pdf.set_y(40)
            
            # Title
            pdf.set_font('Helvetica', 'B', 18)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 10, article.title)
            pdf.ln(5)
            
            # Meta
            pdf.set_font('Helvetica', 'I', 10)
            pdf.set_text_color(100, 100, 100)
            date_str = article.published_at.strftime("%B %d, %Y") if article.published_at else "Unknown Date"
            pdf.cell(0, 5, f'Published: {date_str} | Evidence Strength: {int((article.confidence_score or 0)*100)}%', 0, 1)
            pdf.ln(10)
            
            # Content (using AI summary if available, else snippet)
            pdf.set_font('Helvetica', '', 12)
            pdf.set_text_color(50, 50, 50)
            content = article.summary_medium or article.snippet or "No content available."
            # Remove unsupported chars for fpdf basic fonts
            content = content.encode('latin-1', 'ignore').decode('latin-1')
            pdf.multi_cell(0, 8, content)
            
            pdf.ln(10)
            pdf.set_font('Helvetica', 'U', 10)
            pdf.set_text_color(0, 102, 204)
            pdf.cell(0, 10, f'Read full story online: {article.url}', 0, 1)

        # Save to file
        filename = f"bvn_magazine_{year}_{month:02d}.pdf"
        output_path = f"/tmp/{filename}"
        
        # Ensure /tmp/ exists
        os.makedirs("/tmp", exist_ok=True)
        pdf.output(output_path)
        print(f"PDF generated at {output_path}")

        # 3. Upload to Supabase Storage
        if SUPABASE_URL and SUPABASE_SERVICE_KEY:
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
            
            # Ensure bucket exists
            try:
                supabase.storage.get_bucket("magazines")
            except Exception:
                supabase.storage.create_bucket("magazines", options={"public": True})
            
            with open(output_path, "rb") as f:
                path_on_supa = f"{year}/{month:02d}/{filename}"
                # Overwrite if exists
                supabase.storage.from_("magazines").upload(path_on_supa, f, {"upsert": "true", "content-type": "application/pdf"})
                
            public_url = supabase.storage.from_("magazines").get_public_url(path_on_supa)
            print(f"Uploaded to Supabase: {public_url}")
            
            # 4. Save to DB
            # Check if exists
            stmt = select(Magazine).where(Magazine.year == year, Magazine.month == month)
            res = await db.execute(stmt)
            existing = res.scalars().first()
            
            title = f"{month_str} {year} Edition"
            summary = "Our AI has compiled the most critical events and verified news stories from this month."
            
            if existing:
                existing.pdf_url = public_url
                existing.title = title
                existing.summary = summary
            else:
                new_mag = Magazine(
                    title=title,
                    month=month,
                    year=year,
                    summary=summary,
                    pdf_url=public_url
                )
                db.add(new_mag)
                
            await db.commit()
            print("Magazine saved to Database successfully.")
        else:
            print("Supabase credentials not found. Skipping upload.")

if __name__ == "__main__":
    asyncio.run(generate_monthly_magazine())
