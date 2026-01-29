import pandas as pd
import numpy as np

class TallyDataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.stats = {}
    
    def load_and_process(self):
        """Load and process the Excel file"""
        try:
            # Read Excel from uploaded file (BytesIO)
            df = pd.read_excel(self.file_path)
            
            # Clean column names
            df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]
            
            # Map Tally column names
            column_mapping = {
                'particulars': 'buyer_name',
                'buyer': 'buyer_name',
                'buyer_name': 'buyer_name',
                'value': 'value',
                'amount': 'value',
                'date': 'date',
                'state': 'state'
            }
            
            # Rename only existing columns
            df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
            
            # Handle Tally format: forward fill empty cells
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df['date'] = df['date'].ffill()  # Use ffill() instead of fillna(method='ffill')
            
            if 'buyer_name' in df.columns:
                df['buyer_name'] = df['buyer_name'].ffill()
            
            if 'state' in df.columns:
                df['state'] = df['state'].ffill()
            
            # Clean value column
            if 'value' in df.columns:
                df['value'] = df['value'].astype(str).str.replace(r'[₹,\s]', '', regex=True)
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
            
            # Extract product names and clean buyer names
            if 'buyer_name' in df.columns:
                # Detect rows that contain product codes (items)
                df['is_item'] = df['buyer_name'].str.contains(
                    r'Hydraulic|Broomer|CFGH|Gearbox', 
                    case=False, 
                    na=False
                )
                
                # Clean buyer name (exclude item rows)
                df['clean_buyer'] = np.where(df['is_item'], np.nan, df['buyer_name'])
                df['clean_buyer'] = df['clean_buyer'].ffill()
                
                # Extract item name
                df['item_name'] = np.where(df['is_item'], df['buyer_name'], 'Unknown')
                
                # Remove header rows with zero values
                df = df[df['value'] > 0]
            
            # Add time dimensions
            if 'date' in df.columns:
                df['year'] = df['date'].dt.year
                df['month'] = df['date'].dt.month
                df['month_name'] = df['date'].dt.month_name()
            
            self.df = df
            return df
            
        except Exception as e:
            raise Exception(f"Error processing Excel: {str(e)}")
    
    def get_summary_stats(self):
        """Calculate summary statistics"""
        if self.df is None or self.df.empty:
            return {}
        
        df = self.df
        
        stats = {
            'total_sales': float(df['value'].sum()) if 'value' in df.columns else 0,
            'total_transactions': len(df),
            'avg_transaction': float(df['value'].mean()) if 'value' in df.columns else 0,
            'date_range': {
                'start': df['date'].min() if 'date' in df.columns else None,
                'end': df['date'].max() if 'date' in df.columns else None
            },
            'state_wise_sales': df.groupby('state')['value'].sum().to_dict() if 'state' in df.columns else {},
            'buyer_wise_sales': df.groupby('clean_buyer')['value'].sum().to_dict() if 'clean_buyer' in df.columns else {}
        }
        
        return stats
    
    def get_dataframe(self):
        """Return processed dataframe"""
        return self.df