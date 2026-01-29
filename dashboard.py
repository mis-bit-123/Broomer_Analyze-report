import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

class Dashboard:
    def __init__(self, df, stats):
        """Initialize with dataframe and stats"""
        self.df = df
        self.stats = stats
    
    def render_kpi_cards(self):
        """Render KPI cards at top"""
        st.markdown("## 📊 Key Performance Indicators")
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            st.metric(
                label="💰 Total Sales",
                value=f"₹{self.stats.get('total_sales', 0):,.0f}",
                delta=f"{self.stats.get('total_transactions', 0)} Transactions"
            )
        
        with c2:
            st.metric(
                label="📊 Avg Transaction",
                value=f"₹{self.stats.get('avg_transaction', 0):,.0f}"
            )
        
        with c3:
            dr = self.stats.get('date_range', {})
            if dr.get('start') and dr.get('end'):
                months = (dr['end'] - dr['start']).days / 30.44
                st.metric(
                    label="📅 Period",
                    value=f"{months:.1f} Months",
                    delta=f"{dr['start'].strftime('%b %Y')} - {dr['end'].strftime('%b %Y')}"
                )
            else:
                st.metric(label="📅 Period", value="N/A")
        
        with c4:
            state_sales = self.stats.get('state_wise_sales', {})
            if state_sales:
                top_state = max(state_sales.items(), key=lambda x: x[1])
                st.metric(
                    label="🏆 Top State",
                    value=top_state[0],
                    delta=f"₹{top_state[1]:,.0f}"
                )
            else:
                st.metric(label="🏆 Top State", value="N/A")
        
        st.markdown("---")
    
    def render_sales_trend(self):
        """Sales trend over time"""
        st.subheader("📈 Sales Trend Analysis")
        
        if 'date' not in self.df.columns or self.df['date'].isna().all():
            st.warning("Date information not available")
            return
        
        # Monthly aggregation
        monthly = self.df.groupby(self.df['date'].dt.to_period('M')).agg({
            'value': 'sum',
            'date': 'count'
        }).rename(columns={'date': 'transaction_count'})
        monthly.index = monthly.index.to_timestamp()
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(
                x=monthly.index,
                y=monthly['value'],
                name='Sales Value',
                line=dict(color='#1f77b4', width=3),
                fill='tozeroy',
                fillcolor='rgba(31, 119, 180, 0.2)'
            ),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Bar(
                x=monthly.index,
                y=monthly['transaction_count'],
                name='Transactions',
                marker_color='rgba(255, 127, 14, 0.6)'
            ),
            secondary_y=True,
        )
        
        fig.update_layout(
            title='Monthly Sales Trend',
            hovermode='x unified',
            template='plotly_white',
            height=450,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        
        fig.update_yaxes(title_text="Sales Value (₹)", secondary_y=False)
        fig.update_yaxes(title_text="Number of Transactions", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_state_analysis(self):
        """State-wise analysis"""
        st.subheader("🗺️ State-wise Sales Distribution")
        
        if 'state' not in self.df.columns:
            st.warning("State information not found")
            return
        
        col1, col2 = st.columns(2)
        
        state_data = self.df.groupby('state')['value'].sum().sort_values(ascending=False).reset_index()
        state_data.columns = ['State', 'Sales']
        
        with col1:
            fig = px.pie(
                state_data,
                values='Sales',
                names='State',
                title='Sales by State',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                state_data.head(10),
                y='State',
                x='Sales',
                orientation='h',
                title='Top States by Sales',
                color='Sales',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)
    
    def render_buyer_analysis(self):
        """Top buyers analysis"""
        st.subheader("🏢 Buyer Analytics")
        
        if 'clean_buyer' not in self.df.columns:
            st.warning("Buyer information not found")
            return
        
        # Calculate buyer statistics
        buyer_stats = self.df.groupby('clean_buyer').agg({
            'value': ['sum', 'count', 'mean']
        }).round(2)
        buyer_stats.columns = ['Total_Sales', 'Transactions', 'Avg_Value']
        buyer_stats = buyer_stats.sort_values('Total_Sales', ascending=False)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            top_10 = buyer_stats.head(10).reset_index()
            fig = px.bar(
                top_10,
                y='clean_buyer',
                x='Total_Sales',
                orientation='h',
                title='Top 10 Buyers',
                color='Total_Sales',
                color_continuous_scale='Blues'
            )
            fig.update_layout(yaxis=dict(autorange="reversed"), height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Buyer Details")
            display_df = buyer_stats.head(10).copy()
            display_df['Total_Sales'] = display_df['Total_Sales'].apply(lambda x: f'₹{x:,.0f}')
            display_df['Avg_Value'] = display_df['Avg_Value'].apply(lambda x: f'₹{x:,.0f}')
            st.dataframe(display_df, use_container_width=True)
            
            # Show concentration
            if len(buyer_stats) > 0:
                top_5_share = buyer_stats.head(5)['Total_Sales'].sum() / self.stats.get('total_sales', 1) * 100
                st.metric("Top 5 Buyers Share", f"{top_5_share:.1f}%")
    
    def render_product_analysis(self):
        """Product performance analysis"""
        st.subheader("🔧 Product Performance")
        
        if 'item_name' not in self.df.columns:
            st.warning("Product information not found")
            return
        
        # Filter out unknown items
        prod_df = self.df[self.df['item_name'] != 'Unknown']
        
        if prod_df.empty:
            st.info("No product data available")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Product sales treemap
            product_sales = prod_df.groupby('item_name')['value'].sum().sort_values(ascending=False).head(10)
            fig = px.treemap(
                product_sales.reset_index(),
                path=['item_name'],
                values='value',
                title='Sales by Product',
                color='value',
                color_continuous_scale='RdBu'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Product trend
            product_time = prod_df.groupby([
                prod_df['date'].dt.to_period('M').astype(str),
                'item_name'
            ])['value'].sum().reset_index()
            product_time['date'] = pd.to_datetime(product_time['date'])
            
            fig = px.line(
                product_time,
                x='date',
                y='value',
                color='item_name',
                title='Product Trends',
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def render_data_table(self):
        """Raw data table with filters"""
        st.subheader("📋 Transaction Data")
        
        with st.expander("View & Filter Raw Data"):
            # Filters
            col1, col2 = st.columns(2)
            
            with col1:
                if 'state' in self.df.columns:
                    states = ['All'] + list(self.df['state'].unique())
                    selected_state = st.selectbox("Filter by State", states)
            
            with col2:
                if 'clean_buyer' in self.df.columns:
                    buyers = ['All'] + list(self.df['clean_buyer'].unique())
                    selected_buyer = st.selectbox("Filter by Buyer", buyers)
            
            # Apply filters
            filtered_df = self.df.copy()
            if 'state' in self.df.columns and selected_state != 'All':
                filtered_df = filtered_df[filtered_df['state'] == selected_state]
            if 'clean_buyer' in self.df.columns and selected_buyer != 'All':
                filtered_df = filtered_df[filtered_df['clean_buyer'] == selected_buyer]
            
            # Display
            display_cols = ['date', 'clean_buyer', 'state', 'item_name', 'value']
            display_cols = [col for col in display_cols if col in filtered_df.columns]
            
            st.dataframe(filtered_df[display_cols], use_container_width=True, height=400)
            
            # Download button
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Filtered CSV",
                csv,
                "tally_sales_data.csv",
                "text/csv"
            )