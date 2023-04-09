class ProductCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if 'cart' in request.session:
            cart = request.session['cart']
            product_count_in_cart = sum(item['quantity'] for item in cart.values())
        else:
            product_count_in_cart = 0
        response.set_cookie('product_count_in_cart', str(product_count_in_cart))
        return response
