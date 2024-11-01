import streamlit as st
import base64

# Configure the default theme and page layout
st.set_page_config(
    page_title="Purgo: Smart Data Deduplication & Compliance for Targeted Marketing Outreach",
    page_icon="purgo.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Logo at the very top
st.sidebar.image("purgo.png", use_column_width=True)  # Display the logo at the top of the sidebar

# Convert image to base64 for embedding in CSS
def get_base64_image(file_path):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Get base64 encoding of the background image
background_image = get_base64_image("main_bk.jpg")

# Set up CSS with base64 background image
st.markdown(f"""
    <style>
        /* Hero Section */
        .hero-section {{
            background-image: url("data:image/jpg;base64,{background_image}");
            background-size: cover;
            background-position: center;
            padding: 80px 0;
            text-align: center;
            color: #ffffff;
            border-radius: 10px;
        }}
        .hero-section h2 {{
            font-size: 2.5em;
            font-weight: 800;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
        }}
        .hero-section p {{
            font-size: 1.5em;
            font-weight: 600;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.7);
        }}

        /* Page Layout */
        body {{
            font-family: Arial, sans-serif;
            color: #333;
        }}

        /* Section Styling */
        .section {{
            padding: 40px 0;
            text-align: center;
        }}
        h2 {{
            color: #004aad;
            font-weight: 700;
            margin-bottom: 20px;
        }}

        /* Feature & Benefit Boxes */
        .feature-box, .benefit-box {{
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin: 20px auto;
            max-width: 600px;
            text-align: left;
            color: #333;
        }}
        .feature-box h3, .benefit-box h3 {{
            color: #004aad;
            font-weight: 600;
        }}

        /* Testimonials */
        .testimonials {{
            background-color: #f7f9fc;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin: 20px auto;
            max-width: 600px;
            color: #333;
        }}
        .testimonials p {{
            font-style: italic;
        }}

        /* CTA Buttons */
        .cta-button {{
            background-color: #004aad;
            color: white;
            padding: 12px 20px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            display: inline-block;
            margin: 10px 5px;
        }}
        .cta-button:hover {{
            background-color: #00337f;
        }}

        /* Footer */
        footer {{
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
            color: #888888;
        }}
    </style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
    <div class="hero-section">
        <h2>Unlock Targeted Outreach with Purgo</h2>
        <p>Clean, compliant, and ready-to-use data that empowers your marketing efforts</p>
    </div>
""", unsafe_allow_html=True)

# Key Features Section
st.markdown("<div class='section'><h2>Purgo Features That Simplify Your Workflow</h2>", unsafe_allow_html=True)
features = [
    {"title": "Data Deduplication", "description": "Easily remove duplicates from agency, event, and scraped data sources."},
    {"title": "Master Database Integration", "description": "Cross-check data with our master database to ensure compliance and accuracy."},
    {"title": "Clear Actionable Insights", "description": "Get a clear list of companies you can contact and those restricted, with reasons why."},
    {"title": "Comprehensive Export Options", "description": "Export organized, deduplicated contact lists for outreach planning."}
]
for feature in features:
    st.markdown(f"""
        <div class="feature-box">
            <h3>{feature['title']}</h3>
            <p>{feature['description']}</p>
        </div>
    """, unsafe_allow_html=True)

# How It Works Section
st.markdown("<div class='section'><h2>Effortless Data Processing in Three Steps</h2>", unsafe_allow_html=True)
steps = [
    "Import your data from any source: agency files, web scraping, or event contacts.",
    "The algorithm automatically cross-checks your data with the master database.",
    "Download an organized list showing who you can and can’t reach, with reasons."
]
for idx, step in enumerate(steps, start=1):
    st.markdown(f"""
        <div class="feature-box">
            <h3>Step {idx}</h3>
            <p>{step}</p>
        </div>
    """, unsafe_allow_html=True)

# Benefits Section
st.markdown("<div class='section'><h2>Why Purgo is the Smart Choice for Marketing Teams</h2>", unsafe_allow_html=True)
benefits = [
    {"title": "Efficiency", "description": "Save time on manual data cleanup with intelligent automation."},
    {"title": "Compliance", "description": "Protect your outreach with built-in compliance and visibility into restricted contacts."},
    {"title": "Targeted Outreach", "description": "Gain clarity on which companies to engage, streamlining your marketing efforts."}
]
for benefit in benefits:
    st.markdown(f"""
        <div class="benefit-box">
            <h3>{benefit['title']}</h3>
            <p>{benefit['description']}</p>
        </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
    <footer>
        <p>© 2024 Purgo. All rights reserved. | Privacy Policy | Contact Us</p>
    </footer>
""", unsafe_allow_html=True)
