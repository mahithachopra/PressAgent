import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import time

# Configure Google Gemini API (Replace with your actual key)
genai.configure(api_key="AIzaSyA0HFhv_AaT3-HLCzHKJw17ItRTqQwAJI4")

def safe_generate_content(model, prompt):
    """Handles API call errors gracefully."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error: {e}")
        if "429" in str(e):
            st.warning("Quota exceeded. Waiting before retrying...")
            time.sleep(10)  # Wait for quota reset
        return "Quota exceeded. Please try again later."

# Streamlit UI
st.set_page_config(page_title="PressAgent - AI Press Kit Generator", layout="wide")
st.title("📢 PressAgent: AI-powered Press Kit Generator")
st.write("Generate high-quality press kits with AI-driven quality assessment.")

# User Inputs
st.header("Step 1: Enter Company & Press Release Details")
company_name = st.text_input("Company Name:")
flagship_product = st.text_input("Flagship Product/Service:")
achievements = st.text_area("Major Achievements:")
brand_attributes = st.text_area("Brand Attributes (e.g., innovative, customer-focused):")
press_topic = st.text_area("Press Kit Focus (e.g., new product launch, funding, awards):")
target_media = st.text_input("Target Media (e.g., TechCrunch, Forbes):")
tone = st.selectbox("Preferred Tone:", ["Professional", "Creative", "Formal"])

# Confirmation Step
if st.button("Confirm Input & Generate Press Kit"):
    if not company_name or not flagship_product or not press_topic:
        st.error("Please fill in all required fields (Company Name, Flagship Product, Press Kit Focus).")
    else:
        st.session_state['confirmed'] = True
        st.success("Input confirmed! Proceeding to press kit generation...")
        time.sleep(1)  # Simulate processing time
        st.experimental_rerun()

if 'confirmed' in st.session_state:
    with st.spinner("Generating press kit..."):
        prompt = f"""
        Generate a professional press release for {company_name}, highlighting their flagship product {flagship_product}.
        Include achievements: {achievements}, brand attributes: {brand_attributes}, and press kit focus: {press_topic}.
        The tone should be {tone}.
        """
        model = genai.GenerativeModel("gemini-pro")
        press_kit_content = safe_generate_content(model, prompt)
        
        if press_kit_content:
            st.success("Press Kit Generated!")
            st.text_area("Generated Press Kit:", press_kit_content, height=300)

            # Supplementary Data Inclusion
            st.header("Step 2: Include Supplementary Data?")
            supplementary_data = "New AI analysis platform drives data innovation."  # Example data
            include_data = st.radio("Include supplementary data in Press Kit?", ("Yes", "No"))
            if include_data == "Yes":
                press_kit_content += f"\n\nSupplementary Data: {supplementary_data}"
                st.success("Supplementary data added.")

            # AI Quality Review
            st.header("Step 3: AI Quality Review")
            review_prompt = f"""
            Review the following press release for clarity, engagement, SEO optimization, and consistency:
            {press_kit_content}
            """
            review_feedback = safe_generate_content(model, review_prompt)
            st.text_area("AI Review Feedback:", review_feedback, height=200)

            def generate_pdf(content):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", '', 12)
                # Encode content in UTF-8 and replace problematic characters
                content = content.encode("latin-1", "replace").decode("latin-1")
                pdf.multi_cell(0, 10, content)
                pdf_file = "press_kit.pdf"
                pdf.output(pdf_file, "F")
                return pdf_file


            if st.button("Download Press Kit as PDF"):
                pdf_file = generate_pdf(press_kit_content)
                with open(pdf_file, "rb") as file:
                    st.download_button(label="Download PDF", data=file, file_name="Press_Kit.pdf", mime="application/pdf")
