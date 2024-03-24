from django.shortcuts import render
from yahoo_fin.stock_info import get_quote_table, tickers_nifty50
from django.http.response import HttpResponse
import time
import queue
from threading import Thread
from asgiref.sync import sync_to_async


# Create your views here.
def stockPicker(request):
    stock_picker = tickers_nifty50()
    print(stock_picker)
    return render(request, "mainapp/stockpicker.html", {"stockpicker": stock_picker})


@sync_to_async
def checkAuthenticated(request):
    if not request.user.is_authenticated:
        return False
    else:
        return True


async def stockTracker(request):
    is_loginned = await checkAuthenticated(request)
    if not is_loginned:
        return HttpResponse("Login First")
    stockpicker = request.GET.getlist("stockpicker")
    stockshare = str(stockpicker)[1:-1]

    print(stockpicker)
    data = {}
    available_stocks = tickers_nifty50()
    for i in stockpicker:
        if i not in available_stocks:
            return HttpResponse("error")

    n_threads = len(stockpicker)
    thread_list = []
    que = queue.Queue()
    start = time.time()

    def get_stock_data(q, stock):
        q.put({stock: get_quote_table(stock)})

    for i in range(n_threads):
        thread = Thread(
            target=get_stock_data,
            args=(que, stockpicker[i]),
        )
        thread_list.append(thread)
        thread.start()

    for thread in thread_list:
        thread.join()

    while not que.empty():
        result = que.get()
        data.update(result)

    end = time.time()
    time_taken = end - start
    print(time_taken)

    print(data)
    return render(
        request,
        "mainapp/stocktracker.html",
        {"data": data, "room_name": "track", "selectedstock": stockshare},
    )
