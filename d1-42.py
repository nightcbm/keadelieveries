#Delievery 1, modul 4.2
#Camilla B. Madsen, BE-IT A20 DK1, 4. semester 

# Imports
# Dash
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output

# Div.
import pandas as pd
import numpy as np
import calendar

# Plotly
import plotly.express as px
import plotly.graph_objects as go


#All 4 sheets in excel file
df_customers= pd.read_excel("my_shop_data.xlsx", sheet_name="customers")
df_order = pd.read_excel("my_shop_data.xlsx", sheet_name="order")
df_employee = pd.read_excel("my_shop_data.xlsx", sheet_name="employee")
df_products = pd.read_excel("my_shop_data.xlsx", sheet_name="products")

def get_data():
    # Employee
    df_employee['emp_name'] = df_employee['firstname'] + ' ' + df_employee['lastname']

    # Customer
    df_customers['cust_name'] = df_customers['first_name'] + ' ' + df_customers['last_name']

    # Data 
    df_order['total'] = df_order['unitprice'] * df_order['quantity']
    df_order['deliverytime'] = df_order['deliverydate'] - df_order['orderdate']
    df_order['orderyear'] = df_order['orderdate'].dt.strftime("%Y")
    df_order['ordermonth'] = pd.to_datetime(df_order['orderdate'])
    df_order['ordermonth'] = df_order['ordermonth'].dt.month_name()


    # Relationer
    order = pd.merge(df_order, df_products, on='product_id')
    order = pd.merge(order, df_employee, on='employee_id')
    order = pd.merge(order, df_customers, on='customer_id')

    #Select colomns in order
    order = order[['order_id', 
                'product_id', 'productname', 'type',
                'customer_id', 'cust_name', 'city', 'country',
                'employee_id', 'emp_name', 
                'orderdate', 'deliverydate', 'deliverytime', 'orderyear', 'ordermonth',
                'total']]

    return order


def get_year():
    # Year
    df_year = df_order['orderdate'].dt.strftime("%Y").unique()
    df_year.sort()

    return df_year


def get_month():
     # Month
    months = []
    for x in range(1, 13):
        months.append(calendar.month_name[x])

    df_month = pd.DataFrame(months, columns=["monthnames"])

    return df_month

#rename for calling
order = get_data()
df_year = get_year()
df_month = get_month()


# Diagram 1 - Employee Sales

fig_employee = px.bar(order, 
    x='emp_name', y='total', 
    color='type', text='total', title='Sales by Employee',
    hover_data=[],
    labels={'total':'Total sales', 'emp_name':'Employee', 'type':'Product Type'})
fig_employee.update_traces(texttemplate='%{text:.2s}', textposition='outside')
fig_employee.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', xaxis_tickangle=45)

# Diagram 2 - Products Sales

fig_products = px.bar(order, 
    x='productname', y='total', 
    color='type', title='Sales of Products',
    labels={'total':'Total sales', 'productname':'Products', 'type':'Product Type'})
fig_products.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', xaxis_tickangle=45)


# Activate the app for website
dash_app = dash.Dash(__name__)
app = dash_app.server


# Layout for website (HTML)

dash_app.layout = html.Div(
    children=[
        html.Div(className='row',
                children=[
                    html.Div(className='four columns div-user-controls',
                            children=[
                                html.H2('Sales by employee'),
                                html.P('Select filters from dropdown'),

                    html.Div(children="Month", className="menu-title"),
                            dcc.Dropdown(
                                id='drop_month',
                                options=[{'label':selectmonth, 'value':selectmonth} for selectmonth in df_month['monthnames']],
                            ),
                    html.Div(children="Year", className="menu-title"),
                            dcc.Dropdown(
                                id='drop_year',
                                options=[{'label':selectyear, 'value':selectyear} for selectyear in df_year]
                            ),
                            ]
                    ),
                    html.Div(className='eight columns div-for-charts bg-grey',
                            children=[
                                dcc.Graph(id="sales_employee", figure=fig_employee),
                            ]
                    ),

                    html.Div(className='eight colums div-for-chart 2',
                    children = [
                        html.H2('Products sold'),
                        dcc.Graph(
                        id='graph2',
                        figure=fig_products)]
        ),
                ]
            )
        ]
)


# Callbacks for running app

# Output er diagrammet
# Input er DropDown
@dash_app.callback(Output('sales_employee', 'figure'),
              [Input('drop_month', 'value')],
              [Input('drop_year', 'value')])

def update_graph(drop_month, drop_year):
    if drop_year:
        if drop_month:
            # Data i både drop_month og drop_year
            order_fig1 = order.loc[(order['orderyear'] == drop_year) & (order['ordermonth'] == drop_month)]
        else:
            # Data i drop_year. men ikke drop_month
            order_fig1 = order.loc[order['orderyear'] == drop_year]
    else:
        if drop_month:
            # Data i drop_month, men ikke drop_year
            order_fig1 = order.loc[order['ordermonth'] == drop_month]
        else:
            # Ingen data - ikke noget valgt
            order_fig1 = order
        
    return {'data':[go.Bar(
        x = order_fig1['emp_name'],
        y = order_fig1['total']
            )
        ]
    }


# Call the app to run

if __name__ == '__main__':
    dash_app.run_server(debug=True)
