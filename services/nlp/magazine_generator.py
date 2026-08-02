import asyncio
import os
from datetime import datetime, timezone
from calendar import month_name
from collections import defaultdict
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
        if self.page_no() == 1:
            return  # No header on cover page
        # Sleek top bar
        self.set_fill_color(30, 41, 59) # Slate 800
        self.rect(0, 0, 210, 20, 'F')
        self.set_y(6)
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(248, 250, 252) # Slate 50
        self.cell(0, 8, ' BHARAT VANGUARD NEWS', new_x="LMARGIN", new_y="NEXT", align='L')
        # Accent line
        self.set_fill_color(56, 189, 248) # Sky 400
        self.rect(0, 19, 210, 1, 'F')
        
    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-20)
        self.set_draw_color(203, 213, 225)
        self.line(15, self.get_y(), 195, self.get_y())
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f'- Page {self.page_no()} -', new_x="RIGHT", new_y="TOP", align='C')

    def chapter_title(self, title):
        # Creative geometric section header
        self.set_y(30)
        self.set_fill_color(241, 245, 249) # Slate 100
        self.rect(0, 20, 210, 30, 'F')
        self.set_fill_color(14, 165, 233) # Sky 500
        self.rect(0, 20, 5, 30, 'F') # Left accent
        
        self.set_y(32)
        self.set_x(15)
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(15, 23, 42) # Slate 900
        self.cell(0, 5, title.upper(), new_x="LMARGIN", new_y="NEXT", align='L')
        self.ln(15)

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
            .limit(20)
        )
        result = await db.execute(stmt)
        articles = result.scalars().all()
        
        if not articles:
            print("No articles found to generate magazine.")
            return
            
        categories = defaultdict(list)
        for article in articles:
            cat = article.category or "Top Stories"
            categories[cat].append(article)

        pdf = PDFMagazine()
        pdf.set_auto_page_break(auto=True, margin=25)
        
        # --- COVER PAGE ---
        pdf.add_page()
        # Rich deep background
        pdf.set_fill_color(2, 6, 23) # Slate 950
        pdf.rect(0, 0, 210, 297, 'F')
        
        # Creative background graphics
        pdf.set_fill_color(15, 23, 42) # Slate 900
        pdf.polygon([(0, 0), (210, 0), (210, 150), (0, 100)], style='F')
        pdf.set_fill_color(56, 189, 248) # Sky 400
        pdf.polygon([(0, 100), (210, 150), (210, 155), (0, 105)], style='F')
        
        pdf.set_y(40)
        pdf.set_font('Helvetica', 'B', 56)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 20, 'BHARAT', new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.set_font('Helvetica', '', 32)
        pdf.set_text_color(186, 230, 253) # Sky 200
        pdf.cell(0, 15, 'VANGUARD NEWS', new_x="LMARGIN", new_y="NEXT", align='C')
        
        pdf.set_y(120)
        pdf.set_font('Helvetica', 'B', 22)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, f'{month_str.upper()} {year}', new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.set_font('Helvetica', '', 14)
        pdf.set_text_color(148, 163, 184) # Slate 400
        pdf.cell(0, 8, 'Monthly Intelligence Briefing', new_x="LMARGIN", new_y="NEXT", align='C')
        
        # Publisher's Note Box
        pdf.set_y(170)
        pdf.set_fill_color(30, 41, 59) # Slate 800
        pdf.set_draw_color(56, 189, 248) # Sky 400
        pdf.set_line_width(0.5)
        pdf.rect(25, 170, 160, 50, 'FD')
        
        pdf.set_y(175)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 8, "PUBLISHER's NOTE", new_x="LMARGIN", new_y="NEXT", align='C')
        
        pdf.set_x(35)
        pdf.set_font('Helvetica', 'I', 11)
        pdf.set_text_color(203, 213, 225)
        pdf.multi_cell(140, 6, f"Our AI engine has curated and verified {len(articles)} critical events and breaking stories across {len(categories)} global categories. Read the truth, uncompromised.", align='C')
        
        # --- TABLE OF CONTENTS ---
        pdf.add_page()
        pdf.set_y(40)
        pdf.set_font('Helvetica', 'B', 28)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 15, 'TABLE OF CONTENTS', new_x="LMARGIN", new_y="NEXT", align='L')
        pdf.set_draw_color(226, 232, 240)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(15)
        
        pdf.set_font('Helvetica', '', 16)
        for cat in categories.keys():
            pdf.set_text_color(2, 132, 199) # Light Blue
            cat_name = str(cat).capitalize()
            pdf.cell(0, 12, f'  >  {cat_name}', new_x="LMARGIN", new_y="NEXT", align='L')
            
        # --- SECTIONS & ARTICLES ---
        for cat_name, cat_articles in categories.items():
            pdf.add_page()
            pdf.chapter_title(str(cat_name).capitalize())
            
            pdf.set_margins(15, 20, 15)
            
            for article in cat_articles:
                if pdf.get_y() > 240: 
                    pdf.add_page()
                    pdf.chapter_title(str(cat_name).capitalize() + " (Cont.)")
                    
                # Article Title
                pdf.set_font('Helvetica', 'B', 16)
                pdf.set_text_color(15, 23, 42)
                title = article.title.encode('latin-1', 'ignore').decode('latin-1')
                pdf.multi_cell(0, 8, title)
                pdf.ln(2)
                
                # Meta Data (Date & Score)
                pdf.set_font('Helvetica', 'B', 9)
                pdf.set_text_color(100, 116, 139)
                date_str = article.published_time.strftime("%b %d, %Y") if article.published_time else "Unknown Date"
                trust_score = int((article.trust_signal.confidence_score or 0) * 100) if article.trust_signal else 0
                
                # Trust Badge simulation
                pdf.set_fill_color(240, 253, 244) if trust_score > 80 else pdf.set_fill_color(255, 247, 237)
                pdf.set_text_color(21, 128, 61) if trust_score > 80 else pdf.set_text_color(194, 65, 12)
                pdf.cell(60, 6, f'  VERIFIED: {trust_score}% EVIDENCE  ', new_x="RIGHT", new_y="TOP", border=0, fill=True)
                pdf.set_text_color(100, 116, 139)
                pdf.cell(0, 6, f'     |     {date_str}', new_x="LMARGIN", new_y="NEXT", align='L')
                pdf.ln(6)
                
                # Article Body
                pdf.set_font('Helvetica', '', 11)
                pdf.set_text_color(51, 65, 85)
                content = "No content available."
                if article.ai_summary and article.ai_summary.summary_medium:
                    content = article.ai_summary.summary_medium
                elif article.description:
                    content = article.description
                    
                content = content.encode('latin-1', 'ignore').decode('latin-1')
                pdf.multi_cell(0, 6, content)
                
                # Link
                pdf.ln(4)
                pdf.set_font('Helvetica', 'U', 9)
                pdf.set_text_color(2, 132, 199)
                pdf.cell(0, 5, f'Read original source: {article.url[:80]}...', new_x="LMARGIN", new_y="NEXT")
                
                # Separator Line
                pdf.ln(10)
                pdf.set_draw_color(226, 232, 240)
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(10)

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
            summary_text = f"The {month_str} edition features {len(articles)} verified stories across {len(categories)} categories. Dive into our exclusive AI-curated briefings."
            
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
