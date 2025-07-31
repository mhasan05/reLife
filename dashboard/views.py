from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F, ExpressionWrapper, DecimalField, Sum
from django.utils.timezone import now
from datetime import datetime

from accounts.models import UserAuth
from products.models import Product
from orders.models import Order, OrderItem
from django.db.models.functions import TruncMonth
from django.utils.timezone import localtime
from django.utils.dateformat import DateFormat

class DashboardInfoView(APIView):
    """
    View to handle dashboard information.
    """
    def get(self, request, *args, **kwargs):
        # Basic counts
        all_users = UserAuth.objects.filter(is_active=True).count()
        all_products = Product.objects.filter(is_active=True).count()
        total_orders = Order.objects.all().count()
        total_pending_orders = Order.objects.filter(order_status='pending').count()
        total_shipped_orders = Order.objects.filter(order_status='shipped').count()
        total_delivered_orders = Order.objects.filter(order_status='delivered').count()
        total_cancelled_orders = Order.objects.filter(order_status='cancelled').count()

        # Total sales and delivery cost
        total_sales = Order.objects.filter(order_status='delivered').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_delivery_cost = Order.objects.filter(order_status='delivered').aggregate(Sum('delivery_charge'))['delivery_charge__sum'] or 0

        # Get current month range
        current_date = now()
        start_of_month = datetime(current_date.year, current_date.month, 1)
        if current_date.month == 12:
            end_of_month = datetime(current_date.year + 1, 1, 1)
        else:
            end_of_month = datetime(current_date.year, current_date.month + 1, 1)

        # Query top-selling product this month
        top_product = Product.objects.filter(
            orderitem__order__order_status='delivered',
            orderitem__order__order_date__gte=start_of_month,
            orderitem__order__order_date__lt=end_of_month
        ).annotate(
            total_quantity_sold=Sum('orderitem__quantity')
        ).order_by('-total_quantity_sold').first()

        # Serialize the result
        if top_product:
            top_selling_product = {
                "product_id": top_product.product_id,
                "product_name": top_product.product_name,
                "total_quantity_sold": top_product.total_quantity_sold or 0
            }
        else:
            top_selling_product = None

        # Profit expression: (selling_price - cost_price) * quantity
        profit_expr = ExpressionWrapper(
            (F('product__selling_price') - F('product__cost_price')) * F('quantity'),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )

        # Total profit (monthly revenue)
        monthly_revenue = OrderItem.objects.filter(
            order__order_status='delivered',
            order__order_date__gte=start_of_month,
            order__order_date__lt=end_of_month
        ).aggregate(
            total_profit=Sum(profit_expr)
        )['total_profit'] or 0

        # sales_by_month (monthly sales)
        sales_by_month = (
            Order.objects.filter(order_status='delivered')
            .annotate(month=TruncMonth('order_date'))
            .values('month')
            .annotate(total_sales=Sum('total_amount'))
            .order_by('month')
        )

        # Format the response
        report = []
        for entry in sales_by_month:
            month_date = localtime(entry['month'])  # Ensures timezone-aware formatting
            month_name = DateFormat(month_date).format('F')  # 'F' gives full month name
            report.append({
                "month": month_name,
                "total_sales": float(entry['total_sales'] or 0)
            })



        profit_expr = ExpressionWrapper(
            (F('product__selling_price') - F('product__cost_price')) * F('quantity'),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )

        # Annotate revenue grouped by month from delivered orders
        monthly_revenue = (
            OrderItem.objects
            .filter(order__order_status='delivered')
            .annotate(month=TruncMonth('order__order_date'))
            .values('month')
            .annotate(total_revenue=Sum(profit_expr))
            .order_by('month')
        )

        # Format month name
        data = []
        for item in monthly_revenue:
            month_name = DateFormat(localtime(item['month'])).format('F')
            data.append({
                "month": month_name,
                "revenue": float(item['total_revenue'] or 0)
            })

        # Response data
        dashboard_data = {
            "total_customers": all_users,
            "total_products": all_products,
            "total_orders": total_orders,
            "total_pending_orders": total_pending_orders,
            "total_shipped_orders": total_shipped_orders,
            "total_delivered_orders": total_delivered_orders,
            "total_cancelled_orders": total_cancelled_orders,
            "total_sales": total_sales,
            "total_delivery_cost": total_delivery_cost,
            "monthly_revenue": monthly_revenue,
            "top_selling_product": top_selling_product,
            "sales_by_month": report,
            "profit_by_month": data

        }

        return Response({'status': 'success', 'data': dashboard_data}, status=status.HTTP_200_OK)
