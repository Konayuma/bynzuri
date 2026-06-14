import re
from decimal import Decimal

from django.db import transaction

from apps.categories.models import Category
from apps.products.models import Product
from apps.delivery.models import Province, Town, DeliveryMethod
from apps.orders.models import Order

from .models import Conversation, WhatsAppMessage
from .services import MichoWAPIClient

MAIN_MENU_TEXT = (
    "Welcome to *By Nzuri*! 🛍️\n\n"
    "Reply with a number:\n"
    "1️⃣ Browse Products\n"
    "2️⃣ View Cart 🛒\n"
    "3️⃣ Check Order Status\n"
    "4️⃣ Talk to Us"
)

ORDER_STATUS_PROMPT = "Enter your order ID to check status:"


def _send(phone_number: str, message: str, conversation=None):
    msg = WhatsAppMessage.objects.create(
        conversation=conversation,
        direction='outbound',
        to_number=phone_number,
        body=message,
    )
    client = MichoWAPIClient()
    try:
        result = client.send_text_message(to=phone_number, message=message)
        msg.status = result.get('status', 'sent')
        msg.wapi_message_id = result.get('message_id', '')
        msg.save(update_fields=['status', 'wapi_message_id'])
    except Exception as e:
        msg.status = 'failed'
        msg.error_message = str(e)
        msg.save(update_fields=['status', 'error_message'])


def _fmt_product(p: Product) -> str:
    stock = "✅ In Stock" if p.is_in_stock else "❌ Out of Stock"
    return (
        f"*{p.title}*\n"
        f"💰 K{p.price}\n"
        f"⭐ {p.rating}/5 ({p.review_count} reviews)\n"
        f"{stock}\n"
        f"_{p.description[:100]}{'...' if len(p.description) > 100 else ''}_"
    )


def _fmt_cart(cart: list[dict]) -> str:
    if not cart:
        return "Your cart is empty."
    lines = ["*Your Cart 🛒*", ""]
    total = Decimal('0')
    for i, item in enumerate(cart, 1):
        line_total = Decimal(str(item['price'])) * item['quantity']
        total += line_total
        lines.append(f"{i}. {item['title']} x{item['quantity']} = K{line_total}")
    lines.append("")
    lines.append(f"*Total: K{total}*")
    return "\n".join(lines)


def _paginate(items: list, page: int = 1, per_page: int = 9) -> tuple[list, int]:
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], max(1, (len(items) + per_page - 1) // per_page)


def process_message(phone_number: str, text: str):
    conv, created = Conversation.objects.get_or_create(
        phone_number=phone_number,
        defaults={'state': 'main_menu', 'state_data': {}},
    )

    WhatsAppMessage.objects.create(
        conversation=conv,
        direction='inbound',
        from_number=phone_number,
        to_number='',
        body=text,
    )

    handler = _STATE_HANDLERS.get(conv.state)
    if handler:
        handler(conv, text.strip())
    else:
        conv.state = 'main_menu'
        conv.state_data = {}
        conv.save()
        _send(phone_number, MAIN_MENU_TEXT, conv)


def _handle_main_menu(conv: Conversation, text: str):
    choice = text.strip()
    if choice == '1':
        conv.state = 'browsing_categories'
        conv.state_data = {'page': 1}
        conv.save()
        _list_categories(conv)
    elif choice == '2':
        conv.state = 'viewing_cart'
        conv.save()
        _show_cart(conv)
    elif choice == '3':
        conv.state = 'order_status'
        conv.state_data = {}
        conv.save()
        _send(conv.phone_number, ORDER_STATUS_PROMPT, conv)
    elif choice == '4':
        _send(
            conv.phone_number,
            "Contact us at support@bynzuri.com or call +260-XXX-XXXX. "
            "Reply *0* to return to the main menu.",
            conv,
        )
    else:
        _send(conv.phone_number, MAIN_MENU_TEXT, conv)


def _list_categories(conv: Conversation):
    cats = list(Category.objects.filter(is_active=True))
    if not cats:
        _send(
            conv.phone_number,
            "No categories available. Reply *0* to go back.",
            conv,
        )
        return

    lines = ["*Categories* 📂", ""]
    for i, cat in enumerate(cats, 1):
        count = cat.products.filter(is_active=True).count()
        lines.append(f"{i}. {cat.name} ({count} items)")
    lines.append("")
    lines.append("Reply a number to browse, or *0* for main menu.")

    conv.state_data = {
        'categories': [str(cat.id) for cat in cats],
        'page': 1,
    }
    conv.state = 'browsing_categories'
    conv.save()
    _send(conv.phone_number, "\n".join(lines), conv)


def _handle_browsing_categories(conv: Conversation, text: str):
    if text == '0':
        conv.state = 'main_menu'
        conv.state_data = {}
        conv.save()
        _send(conv.phone_number, MAIN_MENU_TEXT, conv)
        return

    cat_ids = conv.state_data.get('categories', [])
    try:
        idx = int(text) - 1
        if idx < 0 or idx >= len(cat_ids):
            raise ValueError
        cat_id = cat_ids[idx]
    except (ValueError, IndexError):
        _send(conv.phone_number, "Invalid choice. Try again or reply *0* for main menu.", conv)
        return

    conv.state_data = {'category_id': cat_id, 'page': 1}
    conv.state = 'browsing_products'
    conv.save()
    _list_products(conv)


def _list_products(conv: Conversation):
    cat_id = conv.state_data.get('category_id')
    page = conv.state_data.get('page', 1)
    products = list(Product.objects.filter(category_id=cat_id, is_active=True, stock__gt=0))
    total_pages = max(1, (len(products) + 4 - 1) // 4)

    if not products:
        _send(
            conv.phone_number,
            "No products in this category. Reply *0* for categories, *00* for main menu.",
            conv,
        )
        return

    page_products = products[(page - 1) * 4: page * 4]
    lines = ["*Products* 📦", ""]
    for i, p in enumerate(page_products, 1):
        lines.append(f"{i}. {p.title} - K{p.price}")
    lines.append("")
    if total_pages > 1:
        lines.append(f"Page {page}/{total_pages} — reply *n* for more")
    lines.append("Reply a number for details, *0* for categories, *00* for main menu.")

    conv.state_data['product_ids'] = [str(p.id) for p in products]
    conv.state_data['page'] = page
    conv.state_data['total_pages'] = total_pages
    conv.save()
    _send(conv.phone_number, "\n".join(lines), conv)


def _handle_browsing_products(conv: Conversation, text: str):
    if text == '0':
        conv.state = 'browsing_categories'
        conv.state_data = {'page': 1}
        conv.save()
        _list_categories(conv)
        return
    if text == '00':
        conv.state = 'main_menu'
        conv.state_data = {}
        conv.save()
        _send(conv.phone_number, MAIN_MENU_TEXT, conv)
        return
    if text == 'n' and conv.state_data.get('total_pages', 1) > 1:
        conv.state_data['page'] = min(
            conv.state_data.get('page', 1) + 1,
            conv.state_data['total_pages'],
        )
        conv.save()
        _list_products(conv)
        return

    product_ids = conv.state_data.get('product_ids', [])
    try:
        idx = int(text) - 1
        if idx < 0 or idx >= len(product_ids):
            raise ValueError
        product = Product.objects.get(id=product_ids[idx])
    except (ValueError, IndexError, Product.DoesNotExist):
        _send(conv.phone_number, "Invalid choice. Try again.", conv)
        return

    conv.state_data['selected_product_id'] = str(product.id)
    conv.state = 'viewing_product'
    conv.save()

    msg = (
        f"{_fmt_product(product)}\n\n"
        "Reply:\n"
        "1️⃣ Add to Cart\n"
        "2️⃣ Back to Products\n"
        "*0* Main Menu"
    )
    _send(conv.phone_number, msg, conv)


def _handle_viewing_product(conv: Conversation, text: str):
    if text == '1':
        conv.state = 'adding_quantity'
        conv.save()
        _send(conv.phone_number, "How many would you like to add? Reply a number (1-99):", conv)
    elif text == '2':
        conv.state = 'browsing_products'
        conv.state_data.pop('selected_product_id', None)
        conv.save()
        _list_products(conv)
    elif text == '0':
        conv.state = 'main_menu'
        conv.state_data = {}
        conv.save()
        _send(conv.phone_number, MAIN_MENU_TEXT, conv)
    else:
        _send(conv.phone_number, "Reply *1* to add to cart, *2* for products, or *0* for menu.", conv)


def _handle_adding_quantity(conv: Conversation, text: str):
    try:
        qty = int(text.strip())
        if qty < 1 or qty > 99:
            raise ValueError
    except ValueError:
        _send(conv.phone_number, "Please enter a valid number between 1 and 99:", conv)
        return

    product_id = conv.state_data.get('selected_product_id')
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        conv.state = 'main_menu'
        conv.state_data = {}
        conv.save()
        _send(conv.phone_number, "Product not found. " + MAIN_MENU_TEXT, conv)
        return

    if product.stock < qty:
        _send(
            conv.phone_number,
            f"Sorry, only {product.stock} in stock. Enter a lower quantity or *0* to cancel:",
            conv,
        )
        return

    cart = conv.state_data.get('cart', [])
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += qty
            break
    else:
        cart.append({
            'product_id': product_id,
            'title': product.title,
            'price': str(product.price),
            'quantity': qty,
        })

    conv.state_data['cart'] = cart
    conv.state_data.pop('selected_product_id', None)
    conv.state = 'main_menu'
    conv.save()

    _send(
        conv.phone_number,
        f"✅ Added {qty}x {product.title} to your cart!\n\n" + MAIN_MENU_TEXT,
        conv,
    )


def _show_cart(conv: Conversation):
    cart = conv.state_data.get('cart', [])
    if not cart:
        _send(conv.phone_number, "Your cart is empty.\n\n" + MAIN_MENU_TEXT, conv)
        conv.state = 'main_menu'
        conv.save()
        return

    msg = _fmt_cart(cart) + "\n\nReply:\n1️⃣ Checkout\n2️⃣ Clear Cart\n3️⃣ Keep Shopping\n*0* Main Menu"
    conv.state = 'viewing_cart'
    conv.save()
    _send(conv.phone_number, msg, conv)


def _handle_viewing_cart(conv: Conversation, text: str):
    if text == '1':
        conv.state = 'checkout_province'
        conv.state_data['checkout'] = {}
        conv.save()
        _list_provinces(conv)
    elif text == '2':
        conv.state_data['cart'] = []
        conv.state = 'main_menu'
        conv.save()
        _send(conv.phone_number, "Cart cleared.\n\n" + MAIN_MENU_TEXT, conv)
    elif text == '3' or text == '0':
        conv.state = 'main_menu'
        conv.save()
        _send(conv.phone_number, MAIN_MENU_TEXT, conv)
    else:
        _send(conv.phone_number, "Reply *1* checkout, *2* clear, *3* keep shopping.", conv)


def _list_provinces(conv: Conversation):
    provinces = list(Province.objects.all())
    if not provinces:
        conv.state = 'main_menu'
        conv.save()
        _send(conv.phone_number, "No delivery locations configured.\n\n" + MAIN_MENU_TEXT, conv)
        return

    lines = ["*Select Province* 📍", ""]
    for i, p in enumerate(provinces, 1):
        lines.append(f"{i}. {p.name}")
    lines.append("")
    lines.append("Reply a number, or *0* to cancel.")

    conv.state_data['checkout']['provinces'] = [str(p.id) for p in provinces]
    conv.save()
    _send(conv.phone_number, "\n".join(lines), conv)


def _handle_checkout_province(conv: Conversation, text: str):
    if text == '0':
        conv.state = 'main_menu'
        conv.state_data.pop('checkout', None)
        conv.save()
        _send(conv.phone_number, MAIN_MENU_TEXT, conv)
        return

    province_ids = conv.state_data.get('checkout', {}).get('provinces', [])
    try:
        idx = int(text) - 1
        if idx < 0 or idx >= len(province_ids):
            raise ValueError
        province = Province.objects.get(id=province_ids[idx])
    except (ValueError, IndexError, Province.DoesNotExist):
        _send(conv.phone_number, "Invalid choice. Try again or *0* to cancel.", conv)
        return

    conv.state_data['checkout']['province_id'] = str(province.id)
    conv.state_data['checkout']['province_name'] = province.name
    conv.state = 'checkout_town'
    conv.save()
    _list_towns(conv)


def _list_towns(conv: Conversation):
    province_id = conv.state_data['checkout']['province_id']
    towns = list(Town.objects.filter(province_id=province_id))

    if not towns:
        _send(conv.phone_number, "No towns available for this province. Reply *0* to go back.", conv)
        return

    lines = ["*Select Town* 🏙️", ""]
    for i, t in enumerate(towns, 1):
        lines.append(f"{i}. {t.name}")
    lines.append("")
    lines.append("Reply a number, or *0* to go back.")

    conv.state_data['checkout']['towns'] = [str(t.id) for t in towns]
    conv.save()
    _send(conv.phone_number, "\n".join(lines), conv)


def _handle_checkout_town(conv: Conversation, text: str):
    if text == '0':
        conv.state = 'checkout_province'
        conv.state_data['checkout'].pop('province_id', None)
        conv.state_data['checkout'].pop('province_name', None)
        conv.save()
        _list_provinces(conv)
        return

    town_ids = conv.state_data['checkout'].get('towns', [])
    try:
        idx = int(text) - 1
        if idx < 0 or idx >= len(town_ids):
            raise ValueError
        town = Town.objects.get(id=town_ids[idx])
    except (ValueError, IndexError, Town.DoesNotExist):
        _send(conv.phone_number, "Invalid choice. Try again or *0* to go back.", conv)
        return

    conv.state_data['checkout']['town_id'] = str(town.id)
    conv.state_data['checkout']['town_name'] = town.name
    conv.state = 'checkout_address'
    conv.save()
    _send(
        conv.phone_number,
        "Please enter your street address (e.g., 123 Main Road, Olympia):\n\nReply *0* to go back.",
        conv,
    )


def _handle_checkout_address(conv: Conversation, text: str):
    if text == '0':
        conv.state = 'checkout_town'
        conv.state_data['checkout'].pop('town_id', None)
        conv.state_data['checkout'].pop('town_name', None)
        conv.save()
        _list_towns(conv)
        return

    if len(text.strip()) < 5:
        _send(conv.phone_number, "Please enter a valid address (at least 5 characters):", conv)
        return

    conv.state_data['checkout']['address'] = text.strip()
    conv.state = 'checkout_phone'
    conv.save()
    _send(
        conv.phone_number,
        "Please enter your phone number for delivery contact:\n\nReply *0* to go back.",
        conv,
    )


def _handle_checkout_phone(conv: Conversation, text: str):
    if text == '0':
        conv.state = 'checkout_address'
        conv.state_data['checkout'].pop('address', None)
        conv.save()
        _send(
            conv.phone_number,
            "Please enter your street address:\n\nReply *0* to go back.",
            conv,
        )
        return

    phone = text.strip()
    if not re.match(r'^\+?\d{7,15}$', phone):
        _send(
            conv.phone_number,
            "Please enter a valid phone number (e.g., 260977000000):",
            conv,
        )
        return

    conv.state_data['checkout']['phone'] = phone
    conv.state = 'checkout_delivery'
    conv.save()
    _list_delivery_methods(conv)


def _list_delivery_methods(conv: Conversation):
    methods = list(DeliveryMethod.objects.filter(is_active=True))
    if not methods:
        conv.state = 'main_menu'
        conv.save()
        _send(conv.phone_number, "No delivery methods available.\n\n" + MAIN_MENU_TEXT, conv)
        return

    lines = ["*Delivery Method* 🚚", ""]
    for i, m in enumerate(methods, 1):
        lines.append(f"{i}. {m.name} - K{m.price} ({m.estimated_days})")
    lines.append("")
    lines.append("Reply a number, or *0* to go back.")

    conv.state_data['checkout']['delivery_methods'] = [str(m.id) for m in methods]
    conv.save()
    _send(conv.phone_number, "\n".join(lines), conv)


def _handle_checkout_delivery(conv: Conversation, text: str):
    if text == '0':
        conv.state = 'checkout_phone'
        conv.state_data['checkout'].pop('phone', None)
        conv.save()
        _send(
            conv.phone_number,
            "Please enter your phone number for delivery contact:\n\nReply *0* to go back.",
            conv,
        )
        return

    method_ids = conv.state_data['checkout'].get('delivery_methods', [])
    try:
        idx = int(text) - 1
        if idx < 0 or idx >= len(method_ids):
            raise ValueError
        method = DeliveryMethod.objects.get(id=method_ids[idx])
    except (ValueError, IndexError, DeliveryMethod.DoesNotExist):
        _send(conv.phone_number, "Invalid choice. Try again or *0* to go back.", conv)
        return

    conv.state_data['checkout']['delivery_method_id'] = str(method.id)
    conv.state_data['checkout']['delivery_method_name'] = method.name
    conv.state_data['checkout']['delivery_fee'] = str(method.price)
    conv.state = 'checkout_payment'
    conv.save()

    payment_options = (
        "*Payment Method* 💳\n\n"
        "1. MTN Mobile Money\n"
        "2. Airtel Money\n"
        "3. Visa / Mastercard\n\n"
        "Reply a number, or *0* to go back."
    )
    _send(conv.phone_number, payment_options, conv)


def _handle_checkout_payment(conv: Conversation, text: str):
    if text == '0':
        conv.state = 'checkout_delivery'
        conv.state_data['checkout'].pop('delivery_method_id', None)
        conv.state_data['checkout'].pop('delivery_method_name', None)
        conv.state_data['checkout'].pop('delivery_fee', None)
        conv.save()
        _list_delivery_methods(conv)
        return

    payment_map = {'1': 'mtn_momo', '2': 'airtel_money', '3': 'visa'}
    method = payment_map.get(text.strip())
    if not method:
        _send(conv.phone_number, "Invalid choice. Reply *1*, *2*, *3*, or *0* to go back.", conv)
        return

    conv.state_data['checkout']['payment_method'] = method
    conv.state = 'checkout_confirm'
    conv.save()
    _show_order_summary(conv)


def _show_order_summary(conv: Conversation):
    data = conv.state_data['checkout']
    cart = conv.state_data.get('cart', [])

    subtotal = sum(Decimal(str(i['price'])) * i['quantity'] for i in cart)
    delivery = Decimal(data.get('delivery_fee', '0'))
    total = subtotal + delivery

    lines = ["*Order Summary* 📋", ""]
    lines.append(f"📍 {data.get('province_name')}, {data.get('town_name')}")
    lines.append(f"🏠 {data.get('address')}")
    lines.append(f"📞 {data.get('phone')}")
    lines.append(f"🚚 {data.get('delivery_method_name')} (K{delivery})")
    lines.append(f"💳 {data.get('payment_method')}")
    lines.append("")
    lines.append("Items:")
    for item in cart:
        lines.append(f"  • {item['title']} x{item['quantity']} = K{Decimal(item['price']) * item['quantity']}")
    lines.append("")
    lines.append(f"Subtotal: K{subtotal}")
    lines.append(f"Delivery: K{delivery}")
    lines.append(f"*Total: K{total}*")
    lines.append("")
    lines.append("Reply *1* to confirm order, or *0* to cancel.")

    conv.state_data['checkout']['subtotal'] = str(subtotal)
    conv.state_data['checkout']['total'] = str(total)
    conv.save()
    _send(conv.phone_number, "\n".join(lines), conv)


def _handle_checkout_confirm(conv: Conversation, text: str):
    if text == '0':
        conv.state = 'main_menu'
        conv.state_data.pop('checkout', None)
        conv.save()
        _send(conv.phone_number, "Order cancelled.\n\n" + MAIN_MENU_TEXT, conv)
        return

    if text != '1':
        _send(conv.phone_number, "Reply *1* to confirm or *0* to cancel.", conv)
        return

    data = conv.state_data['checkout']
    cart = conv.state_data.get('cart', [])

    if not cart:
        conv.state = 'main_menu'
        conv.state_data = {}
        conv.save()
        _send(conv.phone_number, "Your cart is empty.\n\n" + MAIN_MENU_TEXT, conv)
        return

    try:
        with transaction.atomic():
            from apps.orders.models import Order, OrderItem

            total_amount = sum(Decimal(str(i['price'])) * i['quantity'] for i in cart)
            delivery_fee = Decimal(data.get('delivery_fee', '0'))

            order = Order.objects.create(
                total_amount=total_amount,
                delivery_fee=delivery_fee,
                grand_total=total_amount + delivery_fee,
                province=data.get('province_name', ''),
                town=data.get('town_name', ''),
                street_address=data.get('address', ''),
                phone=data.get('phone', conv.phone_number),
                delivery_method=data.get('delivery_method_name', ''),
                payment_method=data.get('payment_method', ''),
                notes='Ordered via WhatsApp',
            )

            for item in cart:
                try:
                    product = Product.objects.select_for_update().get(id=item['product_id'])
                    if product.stock < item['quantity']:
                        raise ValueError(f"Insufficient stock for {product.title}")
                    product.stock -= item['quantity']
                    product.save()
                except Product.DoesNotExist:
                    pass

                OrderItem.objects.create(
                    order=order,
                    product_id=item['product_id'],
                    product_title=item['title'],
                    quantity=item['quantity'],
                    price_at_purchase=Decimal(item['price']),
                )

            conv.state_data['cart'] = []
            conv.state_data.pop('checkout', None)
            conv.state_data['last_order_id'] = str(order.id)
            conv.state = 'main_menu'
            conv.save()

            for msg in conv.messages.filter(order__isnull=True):
                msg.order = order
                msg.save(update_fields=['order'])

            _send(
                conv.phone_number,
                f"✅ *Order Confirmed!* 🎉\n\n"
                f"Your order ID: `{order.id}`\n"
                f"Total: K{order.grand_total}\n"
                f"Payment: {order.payment_method}\n\n"
                f"We'll send updates via WhatsApp. Thank you for shopping with By Nzuri! ❤️\n\n"
                + MAIN_MENU_TEXT,
                conv,
            )
    except ValueError as e:
        _send(conv.phone_number, f"❌ {e}. Please review your cart and try again.", conv)
    except Exception as e:
        _send(
            conv.phone_number,
            "❌ Something went wrong while creating your order. Please try again later.",
            conv,
        )


def _handle_order_status(conv: Conversation, text: str):
    if text == '0':
        conv.state = 'main_menu'
        conv.state_data = {}
        conv.save()
        _send(conv.phone_number, MAIN_MENU_TEXT, conv)
        return

    try:
        order = Order.objects.get(id=text.strip())
    except (Order.DoesNotExist, ValueError):
        _send(
            conv.phone_number,
            "Order not found. Check your order ID and try again, or reply *0* for main menu.",
            conv,
        )
        return

    status_emojis = {
        'awaiting_payment': '⏳',
        'paid': '✅',
        'processing': '🔄',
        'dispatched': '🚚',
        'delivered': '📦',
        'cancelled': '❌',
    }
    emoji = status_emojis.get(order.status, '❓')

    msg = (
        f"*Order #{order.id}*\n\n"
        f"Status: {emoji} {order.get_status_display()}\n"
        f"Total: K{order.grand_total}\n"
        f"Delivery: {order.town}, {order.province}\n"
        f"Items: {order.items.count()}\n"
        f"Placed: {order.created_at.strftime('%d %b %Y, %H:%M')}\n\n"
        "Reply *0* for main menu."
    )

    conv.state = 'main_menu'
    conv.state_data = {}
    conv.save()
    _send(conv.phone_number, msg, conv)


_STATE_HANDLERS = {
    'main_menu': _handle_main_menu,
    'browsing_categories': _handle_browsing_categories,
    'browsing_products': _handle_browsing_products,
    'viewing_product': _handle_viewing_product,
    'adding_quantity': _handle_adding_quantity,
    'viewing_cart': _handle_viewing_cart,
    'checkout_province': _handle_checkout_province,
    'checkout_town': _handle_checkout_town,
    'checkout_address': _handle_checkout_address,
    'checkout_phone': _handle_checkout_phone,
    'checkout_delivery': _handle_checkout_delivery,
    'checkout_payment': _handle_checkout_payment,
    'checkout_confirm': _handle_checkout_confirm,
    'order_status': _handle_order_status,
}
