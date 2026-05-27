import streamlit as st
import sys
import os
import asyncio

# Set page config
st.set_page_config(page_title="Executive Report", page_icon="📄", layout="wide")

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.db import cached_query, get_engine
from app.services.export_service import generate_executive_pdf
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

st.title("Executive Business Report")
st.markdown("Download a professionally styled executive summary PDF containing performance benchmarks and segment characteristics.")

st.subheader("Report Content Preview")
st.markdown("""
The compiled report contains:
1. **High-Level Performance KPIs:** Total Customer Count, Enterprise Revenue, Average CLV, and Churn Risk index.
2. **Customer Segment Profile Table:** Sizes, revenue shares, average CLVs, and target marketing strategies per segment.
3. **Strategic Marketing Recommendations:** Tailored business suggestions for each customer cohort.
""")

# Download button
if st.button("Generate & Download Executive PDF Report"):
    with st.spinner("Compiling PDF flows and styles..."):
        try:
            # We need an async session to pass to generate_executive_pdf
            # Let's create an async session from the database setting
            # But wait! We can also write a simple sync version or wrap the async generator
            from app.database import AsyncSessionLocal
            
            async def get_pdf_bytes():
                async with AsyncSessionLocal() as session:
                    return await generate_executive_pdf(session)
                    
            try:
                loop = asyncio.get_running_loop()
                future = asyncio.run_coroutine_threadsafe(get_pdf_bytes(), loop)
                pdf_io = future.result()
            except RuntimeError:
                pdf_io = asyncio.run(get_pdf_bytes())
                
            pdf_bytes = pdf_io.getvalue()
            
            st.success("PDF Report generated successfully!")
            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name="customeriq_executive_report.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Failed to generate report: {str(e)}")
            import traceback
            traceback.print_exc()
