import streamlit as st
import requests
import json

# Page configuration
st.set_page_config(
    page_title="MergenX - B2B SaaS Dashboard",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .hotel-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f9f9f9;
    }
    .hotel-name {
        font-size: 18px;
        font-weight: bold;
        color: #1f77b4;
    }
    .hotel-location {
        color: #666;
        font-size: 14px;
    }
    .hotel-price {
        font-size: 20px;
        font-weight: bold;
        color: #2ca02c;
    }
    .hotel-rating {
        color: #ff7f0e;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar for API Key Authentication
st.sidebar.title("🔐 Authentication")
api_key = st.sidebar.text_input("API Key", type="password", help="Enter your API key")

if api_key:
    st.sidebar.success("✅ API Key configured")
else:
    st.sidebar.warning("⚠️ Please enter your API Key")

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info("MergenX - B2B SaaS Tenant Management Dashboard")

# Main content - require API key
if not api_key:
    st.title("🏨 MergenX - B2B SaaS Dashboard")
    st.error("⛔ Access Denied: Please enter your API Key in the sidebar to continue")
    st.stop()

# Main dashboard with API key authenticated
st.title("🏨 MergenX - B2B SaaS Dashboard")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Otel Yönetimi", "Paketler", "API & Test Alanı"])

# Tab 1: Dashboard
with tab1:
    st.header("📊 Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Toplam Otel", value="1,234", delta="12")
    
    with col2:
        st.metric(label="Aktif Paket", value="89", delta="5")
    
    with col3:
        st.metric(label="Bugünkü Arama", value="456", delta="23")
    
    with col4:
        st.metric(label="API Kullanımı", value="85%", delta="-5%")

# Tab 2: Otel Yönetimi
with tab2:
    st.header("🏨 Otel Yönetimi")
    
    st.markdown("### Otel Verisi Yükle")
    
    uploaded_file = st.file_uploader(
        "CSV veya JSON dosyası seçin",
        type=["csv", "json"],
        help="Otel verilerini içeren dosyayı yükleyin"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ Dosya yüklendi: {uploaded_file.name}")
        
        # Show file details
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📄 Dosya Adı: {uploaded_file.name}")
        with col2:
            st.info(f"📦 Dosya Boyutu: {uploaded_file.size} bytes")
    
    if st.button("🚀 Sisteme Yükle", type="primary", use_container_width=True):
        if uploaded_file is not None:
            with st.spinner("Veriler sisteme yükleniyor..."):
                # Simulate database sync
                import time
                time.sleep(2)
                st.success("✅ Otel verileri başarıyla sisteme yüklendi!")
                st.balloons()
        else:
            st.warning("⚠️ Lütfen önce bir dosya yükleyin")

# Tab 3: Paketler
with tab3:
    st.header("📦 Paketler")
    st.info("Tur paketleri CRUD operasyonları yakında eklenecektir.")

# Tab 4: API & Test Alanı
with tab4:
    st.header("🔧 API & Test Alanı")
    
    # API Limit Progress Bar
    st.markdown("### API Kullanım Limiti")
    api_usage = 750
    api_limit = 1000
    progress_value = api_usage / api_limit
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(progress_value)
    with col2:
        st.metric("Kullanım", f"{api_usage}/{api_limit}")
    
    st.markdown("---")
    
    # Hybrid Search Interface
    st.markdown("### 🔍 Hybrid Search Test")
    st.markdown("Search for hotels using natural language queries")
    
    # Search form
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Search Query",
            placeholder="e.g., 5 yıldızlı lüks otel deniz manzaralı",
            help="Enter your search query in natural language"
        )
    
    with col2:
        limit = st.slider("Results Limit", min_value=1, max_value=20, value=5, help="Number of results to return")
    
    city_filter = st.text_input(
        "City Filter (Optional)",
        placeholder="e.g., Istanbul, Antalya, Izmir",
        help="Filter results by city"
    )
    
    # Search button
    search_button = st.button("🔍 Search", type="primary", use_container_width=True, key="search_btn")
    
    # Handle search
    if search_button:
        if not query:
            st.warning("⚠️ Please enter a search query")
        else:
            with st.spinner("🔄 Searching for hotels..."):
                try:
                    # Prepare request
                    url = "http://127.0.0.1:8000/api/v1/search/hybrid"
                    headers = {
                        "X-API-Key": api_key,
                        "Content-Type": "application/json"
                    }
                    
                    # Build request body
                    payload = {
                        "query": query,
                        "limit": limit
                    }
                    
                    # Add city filter if provided
                    if city_filter.strip():
                        payload["city"] = city_filter.strip()
                    
                    # Make API request
                    response = requests.post(url, headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Display AI summary
                        if "ai_summary" in data and data["ai_summary"]:
                            st.info(f"**AI Summary:**\n\n{data['ai_summary']}")
                        
                        # Display hotels
                        if "hotels" in data and data["hotels"]:
                            st.success(f"✅ Found {len(data['hotels'])} hotels")
                            st.markdown("---")
                            
                            # Display hotels in a grid (3 columns)
                            for i in range(0, len(data["hotels"]), 3):
                                cols = st.columns(3)
                                
                                for j in range(3):
                                    if i + j < len(data["hotels"]):
                                        hotel = data["hotels"][i + j]
                                        
                                        with cols[j]:
                                            # Hotel card
                                            st.markdown(f"""
                                                <div class="hotel-card">
                                                    <div class="hotel-name">{hotel.get('name', 'N/A')}</div>
                                                    <div class="hotel-location">📍 {hotel.get('city', 'N/A')}, {hotel.get('country', 'N/A')}</div>
                                                </div>
                                            """, unsafe_allow_html=True)
                                            
                                            # Hotel details
                                            st.markdown(f"**⭐ Rating:** {hotel.get('rating', 'N/A')}")
                                            
                                            # Price
                                            if 'price' in hotel and hotel['price']:
                                                st.markdown(f"<div class='hotel-price'>💰 ${hotel['price']}</div>", unsafe_allow_html=True)
                                            
                                            # Amenities
                                            if 'amenities' in hotel and hotel['amenities']:
                                                amenities = hotel['amenities']
                                                if isinstance(amenities, list):
                                                    amenities_str = ", ".join(amenities[:3])
                                                    if len(amenities) > 3:
                                                        amenities_str += f" +{len(amenities) - 3} more"
                                                    st.caption(f"✨ {amenities_str}")
                                            
                                            # Description
                                            if 'description' in hotel and hotel['description']:
                                                desc = hotel['description']
                                                if len(desc) > 100:
                                                    desc = desc[:100] + "..."
                                                st.caption(desc)
                                            
                                            # Similarity score
                                            if 'similarity_score' in hotel:
                                                score = hotel['similarity_score']
                                                st.progress(float(score) if score else 0.0)
                                                st.caption(f"Match: {score:.2%}" if score else "")
                                            
                                            st.markdown("---")
                        else:
                            st.warning("⚠️ No hotels found matching your criteria")
                        
                    elif response.status_code == 401:
                        st.error("❌ Authentication failed. Please check your API Key")
                    elif response.status_code == 404:
                        st.error("❌ API endpoint not found. Please check if the server is running")
                    else:
                        st.error(f"❌ Error: {response.status_code} - {response.text}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Connection error. Please ensure the API server is running at http://127.0.0.1:8000")
                except requests.exceptions.Timeout:
                    st.error("❌ Request timed out. Please try again")
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
