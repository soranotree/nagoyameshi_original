from datetime import date, datetime, timedelta
from django.contrib import messages
from django.db.models import Avg, Sum, Min, Max
from django.db.models import Q
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import generic

from . import models
from . import forms

""" トップ画面 ================================== """
class TopPageView(generic.ListView):
  template_name = "top_page.html"
  model = models.Restaurant
  queryset = models.Restaurant.objects.order_by('-rate')
  
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
    restaurant_list = models.Restaurant.objects.order_by('-rate')
    new_restaurant_list = models.Restaurant.objects.all().order_by('-created_at')
    
    for restaurant in restaurant_list:
      restaurant.rate_star = round(restaurant.rate * 2) / 2
      if restaurant.rate_star % 1 == 0:
        restaurant.rate_star = int(restaurant.rate_star)
      restaurant.save()

    context.update({
      'category_list': category_list,
      'restaurant_list': restaurant_list,
      'new_restaurant_list': new_restaurant_list,
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
    if restaurant.rate_star % 1 == 0:
      average_rate_star = int(restaurant.rate_star)
    else:
      average_rate_star = restaurant.rate_star

    is_favorite = False
    if user.is_authenticated:
      is_favorite = models.Favorite.objects.filter(customer=user).filter(restaurant=models.Restaurant.objects.get(pk=pk)).exists()
    
    total_seats = models.DiningTable.objects.filter(restaurant=restaurant).aggregate(total=Sum('max_people'))['total'] or 0

    context.update({
      'is_favorite': is_favorite,
      'average_rate_star': average_rate_star,
      'total_seats': total_seats,
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
    if restaurant.rate_star % 1 == 0:
      average_rate_star = int(restaurant.rate_star)
    else:
      average_rate_star = restaurant.rate_star

    total_seats = models.DiningTable.objects.filter(restaurant=restaurant).aggregate(total=Sum('max_people'))['total'] or 0
      
    context = {
      'object': models.Restaurant.objects.get(pk=kwargs['pk']),
      'is_favorite': is_favorite,
      'average_rate_star': average_rate_star,
      'total_seats': total_seats,
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
    print(f'select sort session: { select_sort_session }')

    # filtering queryset
    restaurant_list = models.Restaurant.objects.filter(
      Q(shop_name__icontains=keyword_session) | Q(address__icontains=keyword_session) | Q(category__name__icontains=keyword_session))
    restaurant_list = restaurant_list.filter(category__name__icontains=category_session)
    # print(f'restaurant_list_count: { restaurant_list.count() }')
    # 予算から探す場合
    if int(price_session) > 0:
      restaurant_list = restaurant_list.filter(min_price__lte=price_session, max_price__gte=price_session)

    # DB Update before filtering/ sorting
    for restaurant in restaurant_list:
      # Restaurantのrateはレビュー登録・編集・削除時に実施するようにしたので不要になった
      # average_rate = models.Review.objects.filter(restaurant=restaurant).aggregate(Avg('rate'))['rate__avg']
      # if average_rate is not None:
      #   average_rate = round(average_rate, 2)
      #   restaurant.rate = average_rate
      # else:
      #   restaurant.rate = None
      
      # メニュー登録＆変更時に実施するため不要になった
      # menus = models.Menu.objects.filter(restaurant=restaurant)
      # if menus.exists():
      #   prices = menus.values_list('price', flat=True)
      #   restaurant.min_price = min(prices)
      #   restaurant.max_price = max(prices)
      # else:
      #   restaurant.min_price = None
      #   restaurant.max_price = None

      # レビュー登録・削除時に実施するため不要になった
      # restaurant.review_num = models.Review.objects.filter(restaurant=restaurant).count()

      # 本日移行の処理があり、予約時ではなくソート時に実施する必要があるのでview側に残る
      today = date.today()
      restaurant.reservation_num = models.Reservation.objects.filter(restaurant=restaurant, is_booked=True, is_dependent=False, date__gte=today).count()

      restaurant.save()
    
    print(f'price session: { price_session }')    # 表示順
    if select_sort_session == 'price':
    # if int(price_session) > 0:
      restaurant_list = restaurant_list.order_by('min_price')
      print(f'価格でソート')
      # print(restaurant_list.query)
    else:
      restaurant_list = restaurant_list.order_by(select_sort_session)
      print(f'{ select_sort_session }でソート')

    # print(f'restaurant_list: { restaurant_list }')
    
    category_list = models.Category.objects.all()
    
    # querysetに含まれるレストランの平均レートを、レストランごとに取得して配列に格納
    average_rate_list = []
    average_rate_star_list = []
    # review_numフィールドをレビュー投稿＆削除の都度更新し不要化。時期が来たら削除してもOK。
    # rate_num_list = []
    
    for restaurant in restaurant_list:
      # average_rate = models.Review.objects.filter(restaurant=restaurant).aggregate(Avg('rate'))
      # print(f'avaratge_rate: { average_rate }')
      # average_rate = average_rate['rate__avg'] if average_rate['rate__avg'] is not None else 0
      # print(f'avaratge_rate: { average_rate }')
      # average_rate_list.append(round(average_rate, 2))
      average_rate = restaurant.rate
      average_rate_list.append(round(average_rate, 2))
      # print(f'avaratge_rate_list: { len(average_rate_list) }')
      
      # rate_starに持っていく際に、整数になるケースは最後にintで整数にしなければならない
      # そもそも一発目で整数になるケースは超レア⇒最後に整数処理するように修正
      # if average_rate % 1 == 0:
      #   average_rate = int(average_rate)
      # else:
      #   average_rate = round(average_rate * 2) / 2
      average_rate = round(average_rate * 2) / 2
      if average_rate % 1 == 0:
        average_rate = int(average_rate)
      
      average_rate_star_list.append(average_rate)
      # print(f'avaratge_rate_star_list: { len(average_rate_star_list) }' )
      
      # rate_num = models.Review.objects.filter(restaurant=restaurant).count()
      # rate_num = models.Restaurant.review_num
      # rate_num_list.append(rate_num)
      
# 後述の件数表示不具合対応
    restaurant_list_count = restaurant_list.count()
    
    context.update({
      'category_list': category_list,
      'keyword_session': keyword_session,
      'category_session': category_session,
      'price_session': price_session,
      'select_sort_session': select_sort_session,
      'restaurant_list': zip(restaurant_list, average_rate_list, average_rate_star_list),
      # 'restaurant_list': zip(restaurant_list, average_rate_list, average_rate_star_list, rate_num_list),
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
    # if average_rate % 1 == 0:
    #   average_rate_star = int(average_rate)
    # else:
    #   average_rate_star = round(average_rate * 2) / 2

    average_rate_star = round(average_rate * 2) / 2
    if average_rate_star % 1 == 0:
      average_rate_star = int(average_rate)

      
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

  
""" レビューの一覧表示 ================================== """
class ReviewListView(generic.ListView):
  template_name = "review/review_list.html"
  model = models.Review
  restaurant_id = None
  ordering = ['-created_at']
  paginate_by = 5

  def get(self, request, **kwargs):
    user = request.user
    if user.is_authenticated and user.is_subscribed:
      return super().get(request, **kwargs)
    if not user.is_authenticated:
      return redirect(reverse_lazy('account_login'))
    if not user.is_subscribed:
      return redirect(reverse_lazy('subscribe_register'))
  
  def get_queryset(self):
    restaurant_id = self.kwargs['pk']
    queryset = super(ReviewListView, self).get_queryset().order_by('-visit_date')
    return queryset.filter(restaurant=restaurant_id, display_masked=0)

  def get_context_data(self, **kwargs):
    pk = self.kwargs['pk']
    context = super(ReviewListView, self).get_context_data(**kwargs)
    restaurant = models.Restaurant.objects.filter(id=pk).first()
    if restaurant.rate_star % 1 == 0:
      average_rate_star = int(restaurant.rate_star)
    else:
      average_rate_star = restaurant.rate_star

    is_posted = models.Review.objects.filter(customer=self.request.user).filter(restaurant=restaurant).exists()

    context.update({
      'restaurant': restaurant,
      'is_posted': is_posted,
      'average_rate_star': average_rate_star,
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

    # Update the restaurant's rate field
    restaurant = get_object_or_404(models.Restaurant, id=form.instance.restaurant.id)
    restaurant.review_num = models.Review.objects.filter(restaurant=restaurant, display_masked = 0).count()
    average_rate = models.Review.objects.filter(restaurant=restaurant, display_masked = 0).aggregate(Avg('rate'))['rate__avg']
    if average_rate is not None:
        average_rate = round(average_rate, 2)
        average_rate_star = round(average_rate * 2) / 2
        if average_rate_star % 1 == 0:
          average_rate_star = int(average_rate_star)
        restaurant.rate = average_rate
        restaurant.rate_star = average_rate_star
    else:
        restaurant.rate = None
        restaurant.rate_star = None
    restaurant.save()

    self.success_url = reverse_lazy('review_list', kwargs={'pk':self.kwargs['pk']})
    return super().form_valid(form)
    
  def form_invalid(self, form):
    self.success_url = reverse_lazy('review_create', kwargs={'pk':self.kwargs['pk']})
    return super().form_invalid(form)
    
  def get_context_data(self, **kwargs):
    pk = self.kwargs['pk']
    context = super(ReviewCreateView, self).get_context_data(**kwargs)
    restaurant = models.Restaurant.objects.filter(id=pk).first()

    if restaurant.rate_star % 1 == 0:
      average_rate_star = int(restaurant.rate_star)
    else:
      average_rate_star = restaurant.rate_star

    context.update({
      'restaurant': restaurant,
      'average_rate_star': average_rate_star,
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
    response = super().form_valid(form)
    restaurant = get_object_or_404(models.Restaurant, id=form.instance.restaurant.id)
    restaurant.review_num = models.Review.objects.filter(restaurant=restaurant, display_masked = 0).count()
    average_rate = models.Review.objects.filter(restaurant=restaurant, display_masked = 0).aggregate(Avg('rate'))['rate__avg']
    if average_rate is not None:
        average_rate = round(average_rate, 2)
        average_rate_star = round(average_rate * 2) / 2
        if average_rate_star % 1 == 0:
          average_rate_star = int(average_rate_star)
        restaurant.rate = average_rate
        restaurant.rate_star = average_rate_star
    else:
        restaurant.rate = None
        restaurant.rate_star = None
    restaurant.save()

    return response
  
  def form_invalid(self, form):
    return super().form_invalid(form)
  
  def get_context_data(self, **kwargs):
    pk = self.kwargs['pk']
    context = super(ReviewUpdateView, self).get_context_data(**kwargs)
    restaurant_id = models.Review.objects.filter(id=pk).first().restaurant.id
    restaurant = models.Restaurant.objects.filter(id=restaurant_id).first()

    if restaurant.rate_star % 1 == 0:
      average_rate_star = int(restaurant.rate_star)
    else:
      average_rate_star = restaurant.rate_star

    context.update({
      'restaurant': restaurant,
      'average_rate_star': average_rate_star,
      })
    return context

""" レビューの削除 ================================== """
def review_delete(request):
  pk = request.GET.get('pk')
  is_success = True
  if pk:
    try:
      review = get_object_or_404(models.Review, id=pk)
      restaurant = review.restaurant
      review.delete()
      # Update the restaurant
      restaurant.review_num = models.Review.objects.filter(restaurant=restaurant, display_masked = 0).count()
      average_rate = models.Review.objects.filter(restaurant=restaurant, display_masked = 0).aggregate(Avg('rate'))['rate__avg']
      if average_rate is not None:
        average_rate = round(average_rate, 2)
        average_rate_star = round(average_rate * 2) / 2
        if average_rate_star % 1 == 0:
          average_rate_star = int(average_rate_star)
        restaurant.rate = average_rate
        restaurant.rate_star = average_rate_star
      else:
        restaurant.rate = None
        restaurant.rate_star = None
      restaurant.save()
    except:
      is_success = False
  else:
    is_success = False
  return JsonResponse({'is_success': is_success})


# 店舗側画面
""" 保有レストラン一覧表示 ================================== """
class RestaurantListView2(generic.ListView):
  template_name = "restaurant/restaurant_list_2.html"
  model = models.Restaurant
  ordering = ['-created_at']
  paginate_by = 5
  
  def get_queryset(self):
    return models.Restaurant.objects.filter(shop_owner=self.request.user)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    today = datetime.now()
    # Add extra data (counts) for each restaurant in the context
    restaurants = context['object_list']
    for restaurant in restaurants:
      restaurant.dining_table_count = restaurant.diningtable_set.count()
      restaurant.reservation_count = restaurant.reservation_set.filter(date__gte=today).count()
      restaurant.menu_count = restaurant.menu_set.count()
      restaurant.replies_count = models.Review.objects.filter(restaurant=restaurant, reply__isnull=True).count()
    return context

""" レストランの作成 ================================== """
class RestaurantCreateView(generic.CreateView):
  template_name = "restaurant/restaurant_create.html"
  model = models.Restaurant
  form_class = forms.RestaurantCreateForm
  
  def form_valid(self, form):
  # Set the `shop_owner` to the currently logged-in user before saving
    form.instance.shop_owner = self.request.user
    return super().form_valid(form)

  def get_success_url(self):
    return reverse_lazy('restaurant_list_2', kwargs={'pk': self.request.user.pk})

""" 保有レストランの更新 ================================== """
class RestaurantUpdateView(generic.UpdateView):
    model = models.Restaurant
    template_name = 'restaurant/restaurant_update.html'
    form_class = forms.RestaurantUpdateForm

    def get_success_url(self):
        return reverse_lazy('restaurant_list_2', kwargs={'pk': self.request.user.id})


""" レストランの削除 ================================== """
# def review_delete(request):
#   pk = request.GET.get('pk')
#   is_success = True
#   if pk:
#     try:
#       review = get_object_or_404(models.Review, id=pk)
#       restaurant = review.restaurant
#       review.delete()
#       # Update the review_num
#       restaurant.review_num = models.Review.objects.filter(restaurant=restaurant).count()
#       # Update the restaurant's rate field
#       average_rate = models.Review.objects.filter(restaurant=restaurant).aggregate(Avg('rate'))['rate__avg']
#       if average_rate is not None:
#         average_rate = round(average_rate, 2)
#         restaurant.rate = average_rate
#       else:
#         restaurant.rate = None
#       restaurant.save()
#     except:
#       is_success = False
#   else:
#     is_success = False
  
#   return JsonResponse({'is_success': is_success})

""" ダイニングテーブル一覧 ================================== """
class DiningTableListView(generic.ListView):
  template_name = "dining_table/dining_table_list.html"
  model = models.DiningTable
  # ordering = ['-created_at']
  paginate_by = 20
  
  def get_queryset(self):
    restaurant_id = self.kwargs.get('restaurant_id')
    return models.DiningTable.objects.filter(restaurant_id=restaurant_id)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    restaurant_id = self.kwargs.get('restaurant_id')
    context['restaurant'] = models.Restaurant.objects.get(id=restaurant_id)
    return context

""" ダイニングテーブル編集 ================================== """
class DiningTableUpdateView(generic.UpdateView):
    model = models.DiningTable
    form_class = forms.DiningTableUpdateForm
    template_name = 'dining_table/dining_table_update.html'

    def get_queryset(self):
        # Ensure only dining tables for the specified restaurant are allowed
        restaurant_id = self.kwargs['restaurant_id']
        return models.DiningTable.objects.filter(restaurant__id=restaurant_id)

    def get_success_url(self):
        # Redirect back to the dining table list after updating
        restaurant_id = self.kwargs['restaurant_id']
        return reverse_lazy('dining_table_list', kwargs={'restaurant_id': restaurant_id})

    def get_context_data(self, **kwargs):
        # Pass the restaurant object to the template
        context = super().get_context_data(**kwargs)
        restaurant_id = self.kwargs['restaurant_id']
        context['restaurant'] = get_object_or_404(models.Restaurant, pk=restaurant_id)
        return context

""" ダイニングテーブル作成 ================================== """
class DiningTableCreateView(generic.CreateView):
    template_name = 'dining_table/dining_table_create.html'
    model = models.DiningTable
    form_class = forms.DiningTableCreateForm

    def form_valid(self, form):
        # Link the table to the correct restaurant using the restaurant_id from the URL
        restaurant_id = self.kwargs['restaurant_id']
        form.instance.restaurant = models.Restaurant.objects.get(id=restaurant_id)
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the list of dining tables for the restaurant after creating the table
        restaurant_id = self.kwargs['restaurant_id']
        return reverse_lazy('dining_table_list', kwargs={'restaurant_id': restaurant_id})

    def get_context_data(self, **kwargs):
        # Pass the restaurant context to the template
        context = super().get_context_data(**kwargs)
        context['restaurant'] = models.Restaurant.objects.get(id=self.kwargs['restaurant_id'])
        return context

""" メニュー一覧 ================================== """
class MenuListView(generic.ListView):
  template_name = "menu/menu_list.html"
  model = models.DiningTable
  paginate_by = 5
  
  def get_queryset(self):
    restaurant_id = self.kwargs.get('restaurant_id')
    return models.Menu.objects.filter(restaurant_id=restaurant_id)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    restaurant_id = self.kwargs.get('restaurant_id')
    context['restaurant'] = models.Restaurant.objects.get(id=restaurant_id)
    return context

""" メニュー編集 ================================== """
class MenuUpdateView(generic.UpdateView):
    model = models.Menu
    form_class = forms.MenuUpdateForm
    template_name = 'menu/menu_update.html'

    def get_queryset(self):
        # Ensure only dining tables for the specified restaurant are allowed
        restaurant_id = self.kwargs['restaurant_id']
        return models.Menu.objects.filter(restaurant__id=restaurant_id)

    def get_success_url(self):
        # Redirect back to the dining table list after updating
        restaurant_id = self.kwargs['restaurant_id']
        return reverse_lazy('menu_list', kwargs={'restaurant_id': restaurant_id})

    def get_context_data(self, **kwargs):
        # Pass the restaurant object to the template
        context = super().get_context_data(**kwargs)
        restaurant_id = self.kwargs['restaurant_id']
        context['restaurant'] = get_object_or_404(models.Restaurant, pk=restaurant_id)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        restaurant = get_object_or_404(models.Restaurant, id=form.instance.restaurant.id)
        # restaurant = form.instance.restaurant
        min_price = models.Menu.objects.filter(restaurant=restaurant).aggregate(Min('price'))['price__min']
        max_price = models.Menu.objects.filter(restaurant=restaurant).aggregate(Max('price'))['price__max']
        
        # 価格情報の更新
        if min_price is not None:
            restaurant.min_price = min_price
        else:
            restaurant.min_price = None
        if max_price is not None:
            restaurant.max_price = max_price
        else:
            restaurant.max_price = None

        restaurant.save()
        return response

""" メニュー作成 ================================== """
class MenuCreateView(generic.CreateView):
    template_name = 'menu/menu_create.html'
    model = models.Menu
    form_class = forms.MenuCreateForm

    def form_valid(self, form):
        # Link the table to the correct restaurant using the restaurant_id from the URL
        restaurant_id = self.kwargs['restaurant_id']
        form.instance.restaurant = models.Restaurant.objects.get(id=restaurant_id)
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the list of dining tables for the restaurant after creating the table
        restaurant_id = self.kwargs['restaurant_id']
        return reverse_lazy('menu_list', kwargs={'restaurant_id': restaurant_id})

    def get_context_data(self, **kwargs):
        # Pass the restaurant context to the template
        context = super().get_context_data(**kwargs)
        context['restaurant'] = models.Restaurant.objects.get(id=self.kwargs['restaurant_id'])
        return context


""" レビューの一覧表示 ================================== """
class ReviewListView2(generic.ListView):
    template_name = "review/review_list2.html"
    model = models.Review
    ordering = ['-visit_date']
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        """Ensure only shop owners (account_type = 2) can access this view."""
        user = request.user
        if not user.is_authenticated:
            return redirect(reverse_lazy('account_login'))
        if user.account_type != 2:  # Ensure only shop owners can access.
            return redirect(reverse_lazy('top_page'))  # Redirect if not owner.
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Filter reviews for the restaurant managed by the shop owner."""
        restaurant_id = self.kwargs['pk']
        return (
            super()
            .get_queryset()
            .filter(restaurant_id=restaurant_id)
            .order_by('-visit_date')  # Ordered by latest first
        )

    def get_context_data(self, **kwargs):
        """Add additional context such as restaurant and pending replies."""
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        restaurant = models.Restaurant.objects.get(id=pk)
        
        # Filter reviews without replies for easier focus
        pending_replies = models.Review.objects.filter(
            restaurant=restaurant, reply__isnull=True
        )

        context.update({
            'restaurant': restaurant,
            'pending_replies': pending_replies,
        })
        return context

class ReviewUpdateView2(generic.UpdateView):
    model = models.Review
    fields = ['reply']
    template_name = "review/review_update2.html"

    def get_success_url(self):
        restaurant_id = self.object.restaurant.id
        return reverse_lazy('review_list2', kwargs={'pk': restaurant_id})

def toggle_display_masked(request, pk):
    review = get_object_or_404(models.Review, pk=pk)
    review.display_masked = not review.display_masked
    review.save()

    # Update the restaurant
    restaurant = review.restaurant
    restaurant.review_num = models.Review.objects.filter(restaurant=restaurant, display_masked = 0).count()
    average_rate = models.Review.objects.filter(restaurant=restaurant, display_masked = 0).aggregate(Avg('rate'))['rate__avg']
    if average_rate is not None:
      average_rate = round(average_rate, 2)
      average_rate_star = round(average_rate * 2) / 2
      if average_rate_star % 1 == 0:
        average_rate_star = int(average_rate_star)
      restaurant.rate = average_rate
      restaurant.rate_star = average_rate_star
    else:
      restaurant.rate = None
      restaurant.rate_star = None
    restaurant.save()

    return redirect(reverse('review_list2', kwargs={'pk': review.restaurant.id}))