from datetime import date, datetime, timedelta
from django.contrib import messages
from django.db.models import Avg
from django.db.models import Q
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from . import models
from . import forms

""" トップ画面 ================================== """
class TopPageView(generic.ListView):
  template_name = "top_page.html"
  model = models.Restaurant
  queryset = models.Restaurant.objects.order_by('-rate')
  context_object_name = 'restaurant_list'
  
  def get_context_data(self, **kwargs):
    if 'price_session' in self.request.session:
      self.request.session['price_session'] = 0
    if 'keyword_session' in self.request.session:
      self.request.session['keyword_session'] = ''
    if 'category_session' in self.request.session:
      self.request.session['category_session'] = ''
    if 'select_sort' in self.request.session:
      self.request.session['select_sort'] = '-created_at'
    
    context = super(TopPageView, self).get_context_data(**kwargs)
    category_list = models.Category.objects.all()
    new_restaurant_list = models.Restaurant.objects.all().order_by('-created_at')
    
    # querysetに含まれるレストランの平均レートを、レストランごとに取得して配列に格納
    average_rate_list = []
    average_rate_star_list = []
    for restaurant in context['restaurant_list']:
      average_rate = models.Review.objects.filter(restaurant=restaurant).aggregate(Avg('rate'))
      average_rate = average_rate['rate__avg'] if average_rate['rate__avg'] is not None else 0
      average_rate_list.append(round(average_rate, 2))
      if average_rate % 1 == 0:
        average_rate = int(average_rate)
      else:
        average_rate = round(average_rate * 2) / 2
      average_rate_star_list.append(average_rate)

    context.update({
      'category_list': category_list,
      'new_restaurant_list': new_restaurant_list,
      'restaurant_list': zip(self.queryset, average_rate_list, average_rate_star_list),
      })
    
    return context

""" 利用規約 ================================== """
class CompanyView(generic.TemplateView):
  template_name = "layout/company.html"
 
class TermsView(generic.TemplateView):
  template_name = "layout/terms.html"

""" レストラン詳細画面 ================================== """
class RestaurantDetailView(generic.DetailView):
  template_name = "restaurant/restaurant_detail.html"
  model = models.Restaurant
  def get_context_data(self, **kwargs):
    user = self.request.user
    pk = self.kwargs['pk']
    
    context = super(RestaurantDetailView, self).get_context_data(**kwargs)
    restaurant = models.Restaurant.objects.filter(id=pk).first()
    
    is_favorite = False
    if user.is_authenticated:
      is_favorite = models.Favorite.objects.filter(customer=user).filter(restaurant=models.Restaurant.objects.get(pk=pk)).exists()
    average_rate = models.Review.objects.filter(restaurant=restaurant).aggregate(Avg('rate'))
    average_rate = average_rate['rate__avg'] if average_rate['rate__avg'] is not None else 0
    average_rate = round(average_rate, 2)
    if average_rate % 1 == 0:
      average_rate_star = int(average_rate)
    else:
      average_rate_star = round(average_rate * 2) / 2
      
    rate_count = models.Review.objects.filter(restaurant=restaurant).count()
    context.update({
      'is_favorite': is_favorite,
      'average_rate': average_rate,
      'average_rate_star': average_rate_star,
      'rate_count': rate_count,
      })
    return context
    
  def post(self, request, **kwargs):
    user = request.user
    if not user.is_authenticated:
      return redirect(reverse_lazy('account_login'))
      
    if not user.is_subscribed:
      return redirect(reverse_lazy('subscribe_register'))
      
    pk = kwargs['pk']
    is_favorite = models.Favorite.objects.filter(customer=user).filter(restaurant=models.Restaurant.objects.get(pk=pk)).exists()
    if is_favorite:
      models.Favorite.objects.filter(customer=user).filter(restaurant=models.Restaurant.objects.get(pk=pk)).delete()
      is_favorite = False
    else:
      favorite = models.Favorite()
      user = request.user
      favorite.restaurant = models.Restaurant.objects.get(pk=pk)
      favorite.customer = user
      favorite.save()
      is_favorite = True
      
    restaurant = models.Restaurant.objects.filter(id=pk).first()
    average_rate = models.Review.objects.filter(restaurant=restaurant).aggregate(Avg('rate'))
    average_rate = average_rate['rate__avg'] if average_rate['rate__avg'] is not None else 0
    average_rate = round(average_rate, 2)
    if average_rate % 1 == 0:
      average_rate_star = int(average_rate)
    else:
      average_rate_star = round(average_rate * 2) / 2
      
    rate_count = models.Review.objects.filter(restaurant=restaurant).count()
    context = {
      'object': models.Restaurant.objects.get(pk=kwargs['pk']),
      'is_favorite': is_favorite,
      'average_rate': average_rate,
      'average_rate_star': average_rate_star,
      'rate_count': rate_count,
      }
    return render(request, self.template_name, context)

""" レストラン一覧画面 ================================== """
class RestaurantListView(generic.ListView):
  template_name = "restaurant_list.html"
  model = models.Restaurant
  
  def get_context_data(self, **kwargs):
    context = super(RestaurantListView, self).get_context_data(**kwargs)
    # get input value
    keyword = self.request.GET.get('keyword')
    category = self.request.GET.get('category')
    price = self.request.GET.get('price')
    select_sort = self.request.GET.get('select_sort')
    button_type = self.request.GET.get('button_type')
    keyword = keyword if keyword is not None else ''
    category = category if category is not None else ''
    price = price if price is not None else '0'
    select_sort = select_sort if select_sort is not None else '-created_at'
    
    # session control
    self.request.session['select_sort'] = select_sort
    
    if button_type == 'keyword':
      self.request.session['keyword_session'] = keyword
      self.request.session['category_session'] = ''
      self.request.session['price_session'] = '0'

    if button_type == 'category':
      self.request.session['category_session'] = category
      self.request.session['keyword_session'] = ''
      self.request.session['price_session'] = '0'

    if button_type == 'price':
      self.request.session['price_session'] = price
      self.request.session['keyword_session'] = ''
      self.request.session['category_session'] = ''

    if button_type == 'select_sort':
      self.request.session['select_sort'] = select_sort
    
    keyword_session = self.request.session.get('keyword_session')
    category_session = self.request.session.get('category_session')
    price_session = self.request.session.get('price_session')
    select_sort_session = self.request.session.get('select_sort')
      
    # filtering queryset
    restaurant_list = models.Restaurant.objects.filter(
      Q(shop_name__icontains=keyword_session) | Q(address__icontains=keyword_session) | Q(category__name__icontains=keyword_session))
    restaurant_list = restaurant_list.filter(category__name__icontains=category_session)

    if int(price_session) > 0:
      restaurant_data = models.Restaurant.objects.values('id', 'price')
      target_id_list = []
      
      for data in restaurant_data:
        price_str = data['price']
        price_str = price_str.replace('円', '')
        price_str = price_str.replace(',', '')
        price_list = price_str.split('～')
        
        if int(price_list[0]) <= int(price_session) <= int(price_list[1]):
          target_id_list.append(data['id'])
          restaurant_list = restaurant_list.filter(id__in=target_id_list)
            
    # 表示順
    restaurant_list = restaurant_list.order_by(select_sort_session)
    
    category_list = models.Category.objects.all()
    
    # querysetに含まれるレストランの平均レートを、レストランごとに取得して配列に格納
    average_rate_list = []
    average_rate_star_list = []
    rate_num_list = []
    
    for restaurant in restaurant_list:
      average_rate = models.Review.objects.filter(restaurant=restaurant).aggregate(Avg('rate'))
      average_rate = average_rate['rate__avg'] if average_rate['rate__avg'] is not None else 0
      average_rate_list.append(round(average_rate, 2))
      
      if average_rate % 1 == 0:
        average_rate = int(average_rate)
      else:
        average_rate = round(average_rate * 2) / 2
      average_rate_star_list.append(average_rate)
      
      rate_num = models.Review.objects.filter(restaurant=restaurant).count()
      rate_num_list.append(rate_num)
      
# 後述の件数表示不具合対応
    restaurant_list_count = restaurant_list.count()
    
    context.update({
      'category_list': category_list,
      'keyword_session': keyword_session,
      'category_session': category_session,
      'price_session': price_session,
      'select_sort_session': select_sort_session,
      'restaurant_list': zip(restaurant_list, average_rate_list, average_rate_star_list, rate_num_list),
# 上記のごとくrestaurant_listがzipされるとイテラブルに変換されquerysetでなくなり、テンプレでrestaurant_list.countが使えなくなるとのGPT指摘
# 以下を改めて追加することとした
      'restaurant_list_count': restaurant_list_count,
      })
    return context

""" お気に入り一覧画面 ================================== """
class FavoriteListView(generic.ListView):
  model = models.Favorite
  template_name = 'favorite/favorite_list.html'
  def get_queryset(self):
    user_id = self.request.user.id
    queryset = models.Favorite.objects.filter(customer_id=user_id).order_by('-created_at')
    return queryset

def favorite_delete(request):
  pk = request.GET.get('pk')
  is_success = True
  if pk:
    try:
      models.Favorite.objects.filter(id=pk).delete()
    except:
      is_success = False
  else:
    is_success = False
  return JsonResponse({'is_success': is_success})

""" 新規予約登録画面 ================================== """
class ReservationCreateView(generic.CreateView):
  template_name = "reservation/reservation_create.html"
  model = models.Reservation
  fields = []  # フォームは後で動的に生成します
  # ガイドからの改修によりコメントアウト、フォームなしで実装にトライ
  # form_class = forms.ReservationCreateForm
  success_url = reverse_lazy('reservation_list')
  
  def get(self, request, **kwargs):
    user = request.user
    if user.is_authenticated and user.is_subscribed:
      return super().get(request, **kwargs)
    
    if not user.is_authenticated:
      return redirect(reverse_lazy('account_login'))
    
    if not user.is_subscribed:
      return redirect(reverse_lazy('subscribe_register'))
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    restaurant = get_object_or_404(models.Restaurant, id=self.kwargs['pk'])
    context['restaurant'] = restaurant
    context['hours'] = range(9, 23) # 予約時間リスト作成

    # レート関連
    average_rate = models.Review.objects.filter(restaurant=restaurant).aggregate(Avg('rate'))
    average_rate = average_rate['rate__avg'] if average_rate['rate__avg'] is not None else 0
    average_rate = round(average_rate, 2)
    if average_rate % 1 == 0:
      average_rate_star = int(average_rate)
    else:
      average_rate_star = round(average_rate * 2) / 2
      
    rate_count = models.Review.objects.filter(restaurant=restaurant).count()
    context['average_rate'] = average_rate # コンテキストに追加
    context['average_rate_star'] = average_rate_star # コンテキストに追加
    context['rate_count'] = rate_count # コンテキストに追加


    # 予約条件を取得
    reservation_date = self.request.GET.get('date')  # フロントからの取得
    reservation_time = self.request.GET.get('time')  # フロントからの取得
    number_of_people = self.request.GET.get('number_of_people')  # フロントからの取得
    
    # 予約可能なスロットを取得
    if reservation_date and reservation_time and number_of_people:
      self.available_slots = models.Reservation.objects.filter(
        is_booked = False,
        restaurant = restaurant,
        date = reservation_date,
        time_start= reservation_time,
        dining_table__min_people__lte=number_of_people,  # 最小人数以上
        dining_table__max_people__gte=number_of_people  # 最大人数以下
        )
      context['available_slots'] = self.available_slots # コンテキストに追加
      context['reservation_date'] = reservation_date # コンテキストに追加
      context['reservation_time'] = reservation_time # コンテキストに追加
      context['number_of_people'] = number_of_people # コンテキストに追加
      
    # 予約時間帯で提供可能なメニューを取得
      menus = models.Menu.objects.filter(
        restaurant = restaurant,
        available_from__lte=reservation_time, 
        available_end__gte=reservation_time
        )
      context['menus'] = menus # コンテキストに追加
    
    # 検索窓のデフォルト値設定＆直前検索データ維持用
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    context['tomorrow'] = tomorrow.strftime('%Y-%m-%d')
    context['people_range'] = range(1, 13)  # 1人から(n-1)人までのリストを作成
    context['default_time'] = reservation_time if reservation_time else f"{context['hours'].start}:00"
    
    return context
  
  def form_valid(self, form):
    # POSTデータから予約する予約レコードのIDを取得
    reservation_id = self.request.POST.get('reservation_id')
    # その予約レコードを取得
    reservation_to_book = get_object_or_404(models.Reservation, id=reservation_id)
    # ログインしているユーザーを取得
    user_instance = self.request.user
    # 予約レコードの更新
    reservation_to_book.is_booked = True  # 予約済みにする
    reservation_to_book.customer = user_instance  # 予約ユーザー
    reservation_to_book.number_of_people = self.request.POST.get('number_of_people')  # 予約人数
    # 予約メニュー
    menu_id = self.request.POST.get('menu')  # 予約メニュー
    if menu_id == 'NULL':
      reservation_to_book.menu = None
    else:
      reservation_to_book.menu = models.Menu.objects.get(id=int(menu_id))
    reservation_to_book.save()
    # 予約成功時の処理（必要に応じて追加）
    messages.success(self.request, "予約が完了しました。")
    # 予約が成功したらトップページにリダイレクト
    return redirect(self.success_url)      

  # ガイドからの改修によりコメントアウト
  #   def form_valid(self, form):
  #   user_instance = self.request.user
  #   # GPTのアドバイスにより修正。元の書き方はDB参照ではなくインスタンス生成では？と。
  #   restaurant_instance = models.Restaurant.objects.get(id=self.kwargs['pk'])
  #   # restaurant_instance = models.Restaurant(id=self.kwargs['pk'])
  #   reservation = form.save(commit=False)
  #   reservation.user = user_instance
  #   reservation.restaurant = restaurant_instance
  #   reservation.save()
  #   return super().form_valid(form)
    
  # def form_invalid(self, form):
  #   return super().form_invalid(form)

    
  # ガイドからの改修によりコメントアウト、フォームなしで実装にトライ
  # def get_context_data(self, **kwargs):
  #   pk = self.kwargs['pk']
  #   context = super(ReservationCreateView, self).get_context_data(**kwargs)
  #   restaurant = models.Restaurant.objects.filter(id=pk).first()
  #   average_rate = models.Review.objects.filter(restaurant=restaurant).aggregate(Avg('rate'))
  #   average_rate = average_rate['rate__avg'] if average_rate['rate__avg'] is not None else 0
  #   average_rate = round(average_rate, 2)
  #   if average_rate % 1 == 0:
  #     average_rate_star = int(average_rate)
  #   else:
  #     average_rate_star = round(average_rate * 2) / 2
      
  #   rate_count = models.Review.objects.filter(restaurant=restaurant).count()
  #   close_day_list = self.make_close_list(restaurant.close_day_of_week)
  #   context.update({
  #     'restaurant': restaurant,
  #     'close_day_list': close_day_list,
  #     'average_rate': average_rate,
  #     'average_rate_star': average_rate_star,
  #     'rate_count': rate_count,
  #     })
  #   return context
    
  # def make_close_list(self, close_day):
  #   close_list = []
  #   if '月' in close_day:
  #     close_list.append(1)
  #   if '火' in close_day:
  #     close_list.append(2)
  #   if '水' in close_day:
  #     close_list.append(3)
  #   if '木' in close_day:
  #     close_list.append(4)
  #   if '金' in close_day:
  #     close_list.append(5)
  #   if '土' in close_day:
  #     close_list.append(6)
  #   if '日' in close_day:
  #     close_list.append(0)
  #   return close_list
  
""" 予約一覧表示画面 ================================== """
class ReservationListView(generic.ListView):
  model = models.Reservation
  template_name = 'reservation/reservation_list.html'
  paginate_by = 5
  
  def get_queryset(self):
    queryset = models.Reservation.objects.filter(
      customer_id=self.request.user.id,
      is_booked = True
      ).order_by('-date')
    return queryset
  
  def get_context_data(self, **kwargs):
    context = super(ReservationListView, self).get_context_data(**kwargs)
    context.update({'today': date.today(),})
    return context

""" 予約の削除 ================================== """
def reservation_delete(request):
  pk = request.GET.get('pk')
  is_success = True

# レコード削除ではなく、is_booked=Falseとcostomer = Noneにするよう変更
  if pk:
    try:
      # 該当する予約レコードを取得
      reservation = models.Reservation.objects.get(id=pk)
      # レコードを削除する代わりに、is_booked, customer, number_of_peopleを元に戻す
      reservation.is_booked = False
      reservation.customer = None  # customer_idをnullにする
      reservation.number_of_people = None  # number_of_peopleをnullにする
      reservation.menu = None  # menuをnullにする
      reservation.save()
    except models.Reservation.DoesNotExist:
      is_success = False
    except Exception as e:
      is_success = False
  else:
    is_success = False
  
  return JsonResponse({'is_success': is_success})

  
  # if pk:
  #   try:
  #     models.Reservation.objects.filter(id=pk).delete()
  #   except:
  #     is_success = False
  # else:
  #   is_success = False
  # return JsonResponse({'is_success': is_success})
  
  """ レビューの一覧表示 ================================== """
class ReviewListView(generic.ListView):
  template_name = "review/review_list.html"
  model = models.Review
  restaurant_id = None
  ordering = ['-created_at']
  paginate_by = 5
  
  def get_queryset(self):
    restaurant_id = self.kwargs['pk']
    queryset = super(ReviewListView, self).get_queryset().order_by('-visit_date')
    return queryset.filter(restaurant=restaurant_id)

  def get_context_data(self, **kwargs):
    pk = self.kwargs['pk']
    context = super(ReviewListView, self).get_context_data(**kwargs)
    restaurant = models.Restaurant.objects.filter(id=pk).first()
    is_posted = models.Review.objects.filter(customer=self.request.user).filter(restaurant=restaurant).exists()
    average_rate = models.Review.objects.filter(restaurant=restaurant).aggregate(Avg('rate'))
    average_rate = average_rate['rate__avg'] if average_rate['rate__avg'] is not None else 0
    average_rate = round(average_rate, 2)
    if average_rate % 1 == 0:
      average_rate_star = int(average_rate)
    else:
      average_rate_star = round(average_rate * 2) / 2
    rate_count = models.Review.objects.filter(restaurant=restaurant).count()

    context.update({
      'restaurant': restaurant,
      'is_posted': is_posted,
      'average_rate': average_rate,
      'average_rate_star': average_rate_star,
      'rate_count': rate_count,
      })
    return context

""" レビューの作成 ================================== """
class ReviewCreateView(generic.CreateView):
  template_name = "review/review_create.html"
  model = models.Review
  form_class = forms.ReviewCreateForm
  success_url = None
  
  def get(self, request, **kwargs):
    user = request.user
    if user.is_authenticated and user.is_subscribed:
      return super().get(request, **kwargs)
    if not user.is_authenticated:
      return redirect(reverse_lazy('account_login'))
    if not user.is_subscribed:
      return redirect(reverse_lazy('subscribe_register'))
    
  def form_valid(self, form):
    user_instance = self.request.user
    restaurant_instance = models.Restaurant(id=self.kwargs['pk'])
    review = form.save(commit=False)
    review.restaurant = restaurant_instance
    review.customer = user_instance
    review.save()
    self.success_url = reverse_lazy('review_list', kwargs={'pk':self.kwargs['pk']})
    return super().form_valid(form)
    
  def form_invalid(self, form):
    self.success_url = reverse_lazy('review_create', kwargs={'pk':self.kwargs['pk']})
    return super().form_invalid(form)
    
  def get_context_data(self, **kwargs):
    pk = self.kwargs['pk']
    context = super(ReviewCreateView, self).get_context_data(**kwargs)
    restaurant = models.Restaurant.objects.filter(id=pk).first()
    average_rate = models.Review.objects.filter(restaurant=restaurant).aggregate(Avg('rate'))
    average_rate = average_rate['rate__avg'] if average_rate['rate__avg'] is not None else 0
    average_rate = round(average_rate, 2)
    if average_rate % 1 == 0:
      average_rate_star = int(average_rate)
    else:
      average_rate_star = round(average_rate * 2) / 2
    rate_count = models.Review.objects.filter(restaurant=restaurant).count()
    context.update({
      'restaurant': restaurant,
      'average_rate': average_rate,
      'average_rate_star': average_rate_star,
      'rate_count': rate_count,
      })
    return context

""" レビューの更新 ================================== """
class ReviewUpdateView(generic.UpdateView):
  model = models.Review
  template_name = 'review/review_update.html'
  form_class = forms.ReviewCreateForm
  
  def get_success_url(self):
    pk = self.kwargs['pk']
    restaurant_id = models.Review.objects.filter(id=pk).first().restaurant.id
    return reverse_lazy('review_list', kwargs={'pk': restaurant_id})
  
  def form_valid(self, form):
    return super().form_valid(form)
  
  def form_invalid(self, form):
    return super().form_invalid(form)
  
  def get_context_data(self, **kwargs):
    pk = self.kwargs['pk']
    context = super(ReviewUpdateView, self).get_context_data(**kwargs)
    restaurant_id = models.Review.objects.filter(id=pk).first().restaurant.id
    restaurant = models.Restaurant.objects.filter(id=restaurant_id).first()
    average_rate = models.Review.objects.filter(restaurant=restaurant).aggregate(Avg('rate'))
    average_rate = average_rate['rate__avg'] if average_rate['rate__avg'] is not None else 0
    average_rate = round(average_rate, 2)
    if average_rate % 1 == 0:
      average_rate_star = int(average_rate)
    else:
      average_rate_star = round(average_rate * 2) / 2
    rate_count = models.Review.objects.filter(restaurant=restaurant).count()
    context.update({
      'restaurant': restaurant,
      'average_rate': average_rate,
      'average_rate_star': average_rate_star,
      'rate_count': rate_count,
    })
    
    return context

""" レビューの削除 ================================== """
def review_delete(request):
  pk = request.GET.get('pk')
  is_success = True
  if pk:
    try:
      models.Review.objects.filter(id=pk).delete()
    except:
      is_success = False
  else:
    is_success = False
  
  return JsonResponse({'is_success': is_success})