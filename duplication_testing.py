invs = {'date':[],'Total Revenue':[],'customer_id_list':[]}
for inv in invoices:
    invs['date'].append(inv.TxnDate)
    invs['Total Revenue'].append(inv.TotalAmt)
    invs['customer_id_list'].append(inv.CustomerRef.value)

df = pd.DataFrame(invs)

df['date'] =(df.date.apply(lambda x: datetime.strptime(x,"%Y-%m-%d")))
# df.groupby(df.date.dt.isocalendar().week)['amount'].sum()

total_customers = Customer.choose(df.customer_id_list.to_list(),field="Id",qb=client)

active_customer_ids = [x.Id for x in total_customers if x.Active==True]

def get_active_customers(n):
    l = set([x for x in n if x in active_customer_ids])
    return len(l)

df1 = df.pivot_table(index=df.date.dt.month,values='customer_id_list',aggfunc=list)

df1['Active Monthly Customers'] = df1.customer_id_list.apply(get_active_customers)

df1 = df1.reset_index().rename(columns={'date':'Month'})

df2 = df.pivot_table(index=df.date.dt.month,values='Total Revenue',aggfunc=sum)
df2 = df2.reset_index().rename(columns={'date':'Month'})

cdf = pd.merge(left=df2,right=df1)

cdf['Headcount'] = 25
cdf['Revenue / Employee'] = cdf['Total Revenue']/cdf['Headcount']

cdf['Total Customers']=cdf.customer_id_list.apply(lambda x:len(set(x)))

cdf['Revenue / Active Customer'] = cdf['Total Revenue']/cdf['Active Monthly Customers']


cdf[['Month','Total Revenue','Headcount','Revenue / Employee',
 'Active Monthly Customers',
 'Revenue / Active Customer',
 'Total Customers',]].to_excel('monthlydata.xlsx',index=False)
