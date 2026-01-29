import streamlit as st
from data_processor import TallyDataProcessor
from dashboard import Dashboard

# Page config
st.set_page_config(page_title="Tally Sales Dashboard", layout="wide", initial_sidebar_state="expanded")

# ---------- MAIN DASHBOARD (NO LOGIN) ----------
def main():
    # Sidebar info only (no login)
    st.sidebar.title("📊 Tally Dashboard")
    st.sidebar.info("Upload Excel to view analytics")
    st.sidebar.markdown("---")
    
    # Main Title
    st.title("📊 CMPL Sales Analytics Dashboard")
    st.markdown("### Upload your Tally GST Sales Register Excel file")
    st.markdown("---")
    
    # File Upload Section
    uploaded_file = st.file_uploader(
        "📁 Choose Excel File",
        type=["xlsx", "xls"],
        help="Upload the Excel file exported from Tally GST Sales Register"
    )

    if uploaded_file is not None:
        try:
            with st.spinner("🔍 Processing data... Please wait"):
                # Save temporarily
                with open("temp_data.xlsx", "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                # Process the data
                processor = TallyDataProcessor("temp_data.xlsx")
                df = processor.load_and_process()
                stats = processor.get_summary_stats()
                
                if df is not None and not df.empty:
                    st.success(f"✅ Successfully loaded **{len(df)}** transactions!")
                    
                    # Initialize Dashboard
                    dashboard = Dashboard(df, stats)
                    
                    # Render KPI Cards
                    dashboard.render_kpi_cards()
                    
                    # Create tabs for different views
                    tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "📈 Sales Trends", 
                        "🗺️ State Analysis", 
                        "🏢 Buyer Analytics", 
                        "🔧 Product Performance", 
                        "📋 Data Table"
                    ])
                    
                    with tab1:
                        dashboard.render_sales_trend()
                    
                    with tab2:
                        dashboard.render_state_analysis()
                    
                    with tab3:
                        dashboard.render_buyer_analysis()
                    
                    with tab4:
                        dashboard.render_product_analysis()
                    
                    with tab5:
                        dashboard.render_data_table()
                        
                    # Footer
                    st.markdown("---")
                    st.caption("📊 CMPL Sales Dashboard | Data processed from Tally Export")
                    
                else:
                    st.error("❌ No valid data found in the uploaded file!")
                    st.info("💡 Tip: Make sure you're uploading the GST Sales Register from Tally")
                    
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("💡 Expected columns: Date, Particulars/Buyer, State, Value/Amount")
    
    else:
        # Show instructions when no file uploaded
        st.info("👆 **Getting Started:**")
        st.markdown("""
        1. Open **Tally** → Go to **GST Sales Register**
        2. Click **Export** → Select **Excel** format
        3. Upload the file here using the button above
        4. View interactive charts and analytics!
        """)
        
        # Show sample data structure
        with st.expander("📋 Expected Data Format"):
            st.markdown("""
            Your Excel file should have these columns:
            - **Date** - Invoice date
            - **Particulars/Buyer** - Customer name and item details
            - **State** - Buyer state
            - **Value** - Invoice amount
            
            The dashboard will automatically detect and clean the data.
            """)

if __name__ == "__main__":
    main()