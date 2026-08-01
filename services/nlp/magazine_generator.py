import asyncio
import os
import uuid
from datetime import datetime, timezone
from calendar import month_name
from fpdf import FPDF
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from shared.database import AsyncSessionLocal
from shared.models.articles import Article
from shared.models.magazines import Magazine
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

class PDFMagazine(FPDF):
    def header(self):
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
    print("Starting Monthly Magazine Generation...")
    
    now = datetime.now(timezone.utc)
    month = now.month
    year = now.year
    month_str = month_name[month]
    
    async with AsyncSessionLocal() as db:
        stmt = (
            select(Article)
            .options(selectinload(Article.ai_summary), selectinload(Article.trust_signal))
            .filter(Article.status == 'published')
            .order_by(Article.published_time.desc())
            .limit(10)
        )
        result = await db.execute(stmt)
        articles = result.scalars().all()
        
        if not articles:
            print("No articles found to generate magazine.")
            return

        pdf = PDFMagazine()
        pdf.add_page()
        
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
        
        for article in articles:
            pdf.add_page()
            pdf.set_y(40)
            
            pdf.set_font('Helvetica', 'B', 18)
            pdf.set_text_color(30, 30, 30)
            # Encode for fpdf
            title = article.title.encode('latin-1', 'ignore').decode('latin-1')
            pdf.multi_cell(0, 10, title)
            pdf.ln(5)
            
            pdf.set_font('Helvetica', 'I', 10)
            pdf.set_text_color(100, 100, 100)
            date_str = article.published_time.strftime("%B %d, %Y") if article.published_time else "Unknown Date"
            trust_score = int((article.trust_signal.confidence_score or 0) * 100) if article.trust_signal else 0
            pdf.cell(0, 5, f'Published: {date_str} | Evidence Strength: {trust_score}%', 0, 1)
            pdf.ln(10)
            
            pdf.set_font('Helvetica', '', 12)
            pdf.set_text_color(50, 50, 50)
            # Use ai_summary if exists, else description
            content = "No content available."
            if article.ai_summary and article.ai_summary.summary_medium:
                content = article.ai_summary.summary_medium
            elif article.description:
                content = article.description
                
            content = content.encode('latin-1', 'ignore').decode('latin-1')
            pdf.multi_cell(0, 8, content)
            
            pdf.ln(10)
            pdf.set_font('Helvetica', 'U', 10)
            pdf.set_text_color(0, 102, 204)
            pdf.cell(0, 10, f'Read full story online: {article.url}', 0, 1)

        filename = f"bvn_magazine_{year}_{month:02d}.pdf"
        output_path = f"/tmp/{filename}"
        
        os.makedirs("/tmp", exist_ok=True)
        pdf.output(output_path)
        print(f"PDF generated at {output_path}")

        if SUPABASE_URL and SUPABASE_SERVICE_KEY:
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
            
            try:
                supabase.storage.get_bucket("magazines")
            except Exception:
                supabase.storage.create_bucket("magazines", options={"public": True})
            
            with open(output_path, "rb") as f:
                path_on_supa = f"{year}/{month:02d}/{filename}"
                supabase.storage.from_("magazines").upload(path_on_supa, f, {"upsert": "true", "content-type": "application/pdf"})
                
            public_url = supabase.storage.from_("magazines").get_public_url(path_on_supa)
            print(f"Uploaded to Supabase: {public_url}")
            
            stmt = select(Magazine).where(Magazine.year == year, Magazine.month == month)
            res = await db.execute(stmt)
            existing = res.scalars().first()
            
            title_text = f"{month_str} {year} Edition"
            summary_text = "Our AI has compiled the most critical events and verified news stories from this month."
            
            if existing:
                existing.pdf_url = public_url
                existing.title = title_text
                existing.summary = summary_text
            else:
                new_mag = Magazine(
                    title=title_text,
                    month=month,
                    year=year,
                    summary=summary_text,
                    pdf_url=public_url
                )
                db.add(new_mag)
                
            await db.commit()
            print("Magazine saved to Database successfully.")
        else:
            print("Supabase credentials not found. Skipping upload.")

if __name__ == "__main__":
    asyncio.run(generate_monthly_magazine())
