import requests
import traceback

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static


from django.views.decorators.csrf import csrf_exempt

from product.models import Category,Product,Order,OrderDetail

import json

from linebot import LineBotApi
from linebot.models import TextSendMessage, TemplateSendMessage, CarouselTemplate, MessageAction, CarouselColumn,PostbackAction
from linebot.exceptions import LineBotApiError

ACCESS_TOKEN = ('6aAqRdYCU0Jxhw/8Wpbvdk7DlBHhKMP/wd3jZyck8DB7m56i2Lhpr3/drzdvvwFnh7Zayrsg37UxI0mQKNjn5QzSXZmh5rD3xYvXK9slfsJxs4eDXtGaiaKOpMCiJjHSK4ujYQNrbGmpDhu+KZGNfgdB04t89/1O/w1cDnyilFU=')
line_bot_api = LineBotApi(ACCESS_TOKEN)

@csrf_exempt
def callback(request):
    sent_json = json.loads(request.body)
    reply_token = sent_json['events'][0]['replyToken']
    sent_message = sent_json['events'][0]['message']['text']
    userId = sent_json['events'][0]['source']['userId']

    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
    result = requests.get(f'https://api.line.me/v2/bot/profile/{userId}', headers=headers)
    user_name = json.loads(result.text)['displayName']
    try:
        #購入開始
        if sent_message == '化粧水':

            categories = Category.object.all()

            columns = []

            for category in categories:
                actions = []
                for product in category.product_set.all():  
                        ma = MessageAction(
                            label=product.name,
                            text=product.name
                        )
                        actions.append(ma)    

                cm = CarouselColumn(
                            thumbnail_image_url='https://cosmeland.fs-storage.jp/fs2cabinet/291/291479/291479-m-01-dl.jpg',
                            title=category.name,
                            text='description1',
                            actions=actions
                        )
                columns.append(cm)

            message = TemplateSendMessage(
                alt_text='Carousel template',
                template=CarouselTemplate(
                    columns= columns 
                )
            )
        #購入中   
        elif Product.objects.filter(name=sent_message).first():
            product = Product.objects.filter(name=sent_message).first()
            order = Order.objects.filter(customer = userId ,status = 0).first()
            #購入品がなかった場合
            if not order:
                order = Order(customer=userId)
                order.save()
            #購入品のカウント
            order_detail = OrderDetail.objects.filter(order = order,product__name = sent_message).first()
            if order_detail:
                order_detail.amount = order_detail.amount + 1
            else:
                order_detail = OrderDetail(order = order, product = product,amount = 1)
            order_detail.save()
            message = TextSendMessage(text = 'ほかに購入するものはありますか？')

            #購入完了時
        elif Order.objects.filter(customer=userId, status=0).first()\
                and sent_message == '完了':
                order = Order.objects.filter(customer=userId, status=0).first()
                if not order:
                    order = Order(customer = userId)
                    order.save()
                order_details =order.orderdetail_set.all()
                message = TextSendMessage(text = f'{order.ordertime:%Y年%m月%d日 %H時%M分}に購入品が確定しました。\n{output_order_details(order_details)}')
                order.status = 1
                order.save()
        else:
            message = TextSendMessage(text=f'{user_name}さん いらっしゃいませ。\n「メニュー」と送信すると、注文を開始できます。')
    except Exception:
        message = TextSendMessage(text=f'{user_name}さん いらっしゃいませ。\n「メニュー」と送信すると、注文を開始できます。')
        
        traceback.print_exc()    

    line_bot_api.reply_message(reply_token, message)

def output_order_details(order_details):
    result = ''
    for order_detail in order_details:    
        result += f'{order_detail.product.name}:{order_detail.amount}個\n'
    return result

urlpatterns = [
    path('admin/', admin.site.urls),
    path('callback/',callback)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
