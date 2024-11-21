import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

import pandas as pd
import seaborn as sns;sns.set()

sns.set(style="whitegrid")
def create_signup_dates_plot(signup_dates, start_date=None, end_date=None):

    df = pd.DataFrame(signup_dates, columns=['created_at'])
    df['created_at'] = pd.to_datetime(df['created_at']).dt.date
    
    if start_date and end_date:
        df = df[(df['created_at'] >= pd.to_datetime(start_date).date()) & (df['created_at'] <= pd.to_datetime(end_date).date())]
    
    signup_counts = df['created_at'].value_counts().sort_index().reset_index()
    signup_counts.columns = ['created_at', 'signup_count']
    
    colors = sns.color_palette("Set2")
    plt.figure(figsize=(10, 6))
    plot = sns.barplot(x='created_at', y='signup_count', data=signup_counts, palette=colors)
    plot.set_title(f'Signups from {start_date} to {end_date}' if start_date and end_date else 'Signups for All Dates', fontsize=14)
    plot.set_xlabel('Date', fontsize=12)
    plot.set_ylabel('Signups', fontsize=12)
    plot.set_xticklabels(plot.get_xticklabels(), rotation=45)
    plot.yaxis.set_major_locator(MaxNLocator(integer=True, prune='lower'))
    plt.tight_layout()
    plt.grid()
    plt.savefig("static/img/signup_dates.png")
    plt.close()
