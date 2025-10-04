# filename: plot_stocks.py
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Create directory if it doesn't exist
os.makedirs('/data/icy/code/Microsoft_AutoGen_Tutorial/sources_simple/pics', exist_ok=True)

# Get current year
current_year = datetime.now().year
start_date = f'{current_year}-01-01'
end_date = datetime.now().strftime('%Y-%m-%d')

# Download stock data
nvda = yf.download('NVDA', start=start_date, end=end_date)
tsla = yf.download('TSLA', start=start_date, end=end_date)

# Normalize prices to percentage change from start
nvda['Normalized'] = (nvda['Close'] / nvda['Close'].iloc[0]) * 100
tsla['Normalized'] = (tsla['Close'] / tsla['Close'].iloc[0]) * 100

# Plot the data
plt.figure(figsize=(12, 6))
plt.plot(nvda.index, nvda['Normalized'], label='NVDA')
plt.plot(tsla.index, tsla['Normalized'], label='TSLA')

# Add title and labels
plt.title(f'NVDA vs TSLA Stock Price Change YTD ({start_date} to {end_date})')
plt.xlabel('Date')
plt.ylabel('Price Change (%)')
plt.legend()
plt.grid(True)

# Save the plot
save_path = '/data/icy/code/Microsoft_AutoGen_Tutorial/sources_simple/pics/stock_chart.png'
plt.savefig(save_path)
print(f"Chart saved successfully to: {save_path}")