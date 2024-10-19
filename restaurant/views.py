from datetime import date, datetime, timedelta, time
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Avg, Sum, Min, Max
from django.db.models import Count, Q
from django.db.models import F
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import generic, View
from django.http import HttpResponseRedirect
from urllib.parse import urlencode 
from django.utils import timezone
from django.utils.timezone import now

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
    # 【実験中】高速化のため数を絞っている⇒劇的に早い
    restaurant_list = models.Restaurant.objects.order_by('-rate')[:18]
    new_restaurant_list = models.Restaurant.objects.all().order_by('-created_at')[:18]

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

    is_favorite = False
    if user.is_authenticated:
      is_favorite = models.Favorite.objects.filter(customer=user).filter(restaurant=models.Restaurant.objects.get(pk=pk)).exists()
    
    total_seats = models.DiningTable.objects.filter(restaurant=restaurant).aggregate(total=Sum('max_people'))['total'] or 0

    context.update({
      'is_favorite': is_favorite,
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

    total_seats = models.DiningTable.objects.filter(restaurant=restaurant).aggregate(total=Sum('max_people'))['total'] or 0
      
    context = {
      'object': models.Restaurant.objects.get(pk=kwargs['pk']),
      'is_favorite': is_favorite,
      'total_seats': total_seats,
      }
    return render(request, self.template_name, context)

""" レストラン一覧画面 ================================== """
class RestaurantListView(generic.ListView):
    template_name = "restaurant_list.html"
    model = models.Restaurant
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(RestaurantListView, self).get_context_data(**kwargs)

        # Get input values and set defaults
        keyword = self.request.GET.get('keyword', '')
        category = self.request.GET.get('category', '')
        price = self.request.GET.get('price', '0')
        select_sort = self.request.GET.get('select_sort', '-created_at')
        button_type = self.request.GET.get('button_type')

        # Session control
        if button_type == 'keyword':
            self.request.session.update({
                'keyword_session': keyword,
                'category_session': '',
                'price_session': '0',
                'select_sort': select_sort,
            })
        elif button_type == 'category':
            self.request.session.update({
                'category_session': category,
                'keyword_session': '',
                'price_session': '0',
                'select_sort': select_sort,
            })
        elif button_type == 'price':
            self.request.session.update({
                'price_session': price,
                'keyword_session': '',
                'category_session': '',
                'select_sort': select_sort,
            })
        elif button_type == 'select_sort':
            self.request.session['select_sort'] = select_sort

        # Retrieve session values
        keyword_session = self.request.session.get('keyword_session', '')
        category_session = self.request.session.get('category_session', '')
        price_session = self.request.session.get('price_session', '0')
        select_sort_session = self.request.session.get('select_sort', '-created_at')

        # Filtering queryset
        restaurant_list = models.Restaurant.objects.all()
        restaurant_list = restaurant_list.filter(
            Q(shop_name__icontains=keyword_session) |
            Q(address__icontains=keyword_session) |
            Q(category__name__icontains=keyword_session)
        )

        if category_session:
            restaurant_list = restaurant_list.filter(category__name__icontains=category_session)

        if int(price_session) > 0:
            restaurant_list = restaurant_list.filter(min_price__lte=price_session, max_price__gte=price_session)

        # Annotate reservation counts
        today = date.today()
        restaurant_list = restaurant_list.annotate(
            reservation_count=Count(
                'reservation',
                filter=Q(
                    reservation__is_booked=True,
                    reservation__is_dependent=False,
                    reservation__date__gte=today
                )
            )
        )

        # Sorting
        if select_sort_session == 'price':
            restaurant_list = restaurant_list.order_by('min_price')
        else:
            restaurant_list = restaurant_list.order_by(select_sort_session)

        total_restaurant_count = restaurant_list.count()
        category_list = models.Category.objects.all()

        # Pagination
        paginator = Paginator(restaurant_list, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context.update({
            'category_list': category_list,
            'keyword_session': keyword_session,
            'category_session': category_session,
            'price_session': price_session,
            'select_sort_session': select_sort_session,
            'total_restaurant_count': total_restaurant_count,
            'page_obj': page_obj,
        })
        return context


    # def get_queryset(self):
    #     # Capture select_sort from the query parameters
    #     select_sort = self.request.GET.get('select_sort', '-created_at')
    #     self.request.session['select_sort'] = select_sort

    #     # Retrieve filter parameters from the GET request
    #     keyword = self.request.GET.get('keyword', '')
    #     category = self.request.GET.get('category', '')
    #     price = self.request.GET.get('price', '0')

    #     # Update session with the latest filter values
    #     self.request.session['keyword_session'] = keyword
    #     self.request.session['category_session'] = category
    #     self.request.session['price_session'] = price

    #     today = date.today()

    #     # Start with all restaurants
    #     queryset = models.Restaurant.objects.all()

    #     # Apply keyword filter if keyword is not empty
    #     if keyword:
    #         queryset = queryset.filter(
    #             Q(shop_name__icontains=keyword) |
    #             Q(address__icontains=keyword) |
    #             Q(category__name__icontains=keyword)
    #         )

    #     # Apply category filter if category is not empty
    #     if category:
    #         queryset = queryset.filter(category__name__icontains=category)

    #     # Apply price filter if price is greater than 0
    #     if int(price) > 0:
    #         queryset = queryset.filter(min_price__lte=price, max_price__gte=price)

    #     # Annotate reservation counts
    #     queryset = queryset.annotate(
    #         reservation_count=Count(
    #             'reservation',
    #             filter=Q(
    #                 reservation__is_booked=True,
    #                 reservation__is_dependent=False,
    #                 reservation__date__gte=today
    #             )
    #         )
    #     )

    #     # Apply sorting after filtering
    #     if select_sort == 'price':
    #         queryset = queryset.order_by('min_price')
    #     else:
    #         queryset = queryset.order_by(select_sort)

    #     return queryset

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)

    #     # Get the filtered queryset for counting total restaurants
    #     total_restaurant_count = self.get_queryset().count()

    #     context.update({
    #         'select_sort_session': self.request.session.get('select_sort', '-created_at'),
    #         'keyword_session': self.request.session.get('keyword_session', ''),
    #         'category_session': self.request.session.get('category_session', ''),
    #         'price_session': self.request.session.get('price_session', '0'),
    #         'category_list': models.Category.objects.all(),
    #         'total_restaurant_count': total_restaurant_count,
    #     })
    #     return context


""" お気に入り一覧画面 ================================== """
class FavoriteListView(generic.ListView):
  model = models.Favorite
  template_name = 'favorite/favorite_list.html'
  def get_queryset(self):
    user_id = self.request.user.id
    queryset = models.Favorite.objects.filter(customer_id=user_id).order_by('-created_at')
    return queryset

""" お気に入り削除機能 ================================== """
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
        context['hours'] = range(9, 23)  # 予約時間リスト作成

        # 予約条件を取得
        reservation_date = self.request.GET.get('date')  # フロントからの取得
        reservation_time = self.request.GET.get('time')  # フロントからの取得
        number_of_people = self.request.GET.get('number_of_people')  # フロントからの取得

        # 予約可能なスロットを取得
        if reservation_date and reservation_time and number_of_people:
            reservation_time_obj = datetime.strptime(reservation_time, "%H:%M").time()

            # 同じテーブルの予約が持つ予約時間を確認
            potential_slots = models.Reservation.objects.filter(
                is_booked=False,
                restaurant=restaurant,
                date=reservation_date,
                time_start= reservation_time,
                duration_min__gt= 0,
                dining_table__min_people__lte=number_of_people,
                dining_table__max_people__gte=number_of_people,
            )

            valid_slots = []
            for slot in potential_slots:
                # 現在のスロットの終了時間を計算
                slot_end_time = (
                    datetime.combine(datetime.today(), slot.time_start) +
                    timedelta(minutes=slot.duration_min)
                ).time()

                # 同じテーブルで重複する予約があるか確認
                conflicting_reservations = models.Reservation.objects.filter(
                    dining_table=slot.dining_table,  # 同じテーブル
                    date=reservation_date,
                    is_booked=True,
                    time_start__lt=slot_end_time,  # 終了時間前に始まる
                    time_start__gt=slot.time_start,  # スロットの開始時間以降
                )

                if not conflicting_reservations.exists():
                    valid_slots.append(slot)

            context['available_slots'] = valid_slots  # コンテキストに追加
            context['reservation_date'] = reservation_date  # コンテキストに追加
            context['reservation_time'] = reservation_time  # コンテキストに追加
            context['number_of_people'] = number_of_people  # コンテキストに追加

            # 提供可能なメニューの取得
            menus = models.Menu.objects.filter(
                restaurant=restaurant,
                available_from__lte=reservation_time_obj,
                available_end__gte=reservation_time_obj,
            ).order_by('price')
            context['menus'] = menus  # コンテキストに追加

        # 検索窓のデフォルト値設定＆直前検索データ維持用
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        context['tomorrow'] = tomorrow.strftime('%Y-%m-%d')
        context['people_range'] = range(1, 13)  # 1人から12人までのリストを作成
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
        reservation_to_book.menu = models.Menu.objects.filter(id=menu_id).first()
        reservation_to_book.save()
        # reservation_numの更新

        # 予約の終了時間を計算
        end_time = (
            datetime.combine(datetime.today(), reservation_to_book.time_start) +
            timedelta(minutes=reservation_to_book.duration_min)
            ).time()

        # 依存スロット（予約終了時間よりも手前のスロット）を取得
        dependent_reservations = models.Reservation.objects.filter(
            dining_table=reservation_to_book.dining_table,
            is_booked=False,
            is_dependent=False,
            date=reservation_to_book.date,
            time_start__gt=reservation_to_book.time_start,  # 現在の予約の開始時間以降
            time_start__lt=end_time,  # 終了時間よりも早い
            )

        # 取得した予約に対して、is_booked=True and is_dependent=Trueを設定
        for dep_reservation in dependent_reservations:
            dep_reservation.is_booked = True
            dep_reservation.is_dependent = True
            dep_reservation.customer = user_instance
            dep_reservation.save()

        # 予約数の更新
        restaurant = reservation_to_book.restaurant
        booked_count = models.Reservation.objects.filter(restaurant=restaurant, is_booked=True, is_dependent=False).count()
        restaurant.reservation_num = booked_count
        restaurant.save()

        messages.success(self.request, "予約が完了しました。")

        return redirect(self.success_url) 
  
""" 予約一覧表示画面 ================================== """
class ReservationListView(generic.ListView):
  model = models.Reservation
  template_name = 'reservation/reservation_list.html'
  paginate_by = 5
  
  def get_queryset(self):
    queryset = models.Reservation.objects.filter(
      customer_id=self.request.user.id,
      is_booked = True,
      is_dependent = False
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

    if pk:
        try:
            # 該当する予約レコードを取得
            reservation = models.Reservation.objects.get(id=pk)

            # 予約と依存する予約をリセットする関数
            def reset_reservation(res):
                res.is_booked = False
                res.is_dependent = False  # 依存フラグもリセット
                res.customer = None  # customer_idをnullにする
                res.number_of_people = None  # number_of_peopleをnullにする
                res.menu = None  # menuをnullにする
                res.save()

            # 現在の予約をリセット
            reset_reservation(reservation)

            # 現在の予約の終了時間を計算（datetimeに変換して処理）
            current_datetime = datetime.combine(reservation.date, reservation.time_start)
            next_time = current_datetime + timedelta(minutes=30)

            dependent_slots = []

            # 依存する連続スロットを取得（逐次探索）
            while True:
                next_reservation = models.Reservation.objects.filter(
                    dining_table=reservation.dining_table,
                    date=next_time.date(),  # 同じ日付
                    time_start=next_time.time(),  # 次の30分後のスロット
                    is_dependent=True,
                    is_booked=True  # 予約されている依存スロットのみ
                ).first()

                if next_reservation:
                    dependent_slots.append(next_reservation)
                    next_time += timedelta(minutes=30)  # 次のスロットの探索
                else:
                    break  # 連続スロットの探索終了

            # 取得した依存スロットをリセット
            for dep_res in dependent_slots:
                reset_reservation(dep_res)

            # 予約数の更新
            restaurant = reservation.restaurant
            booked_count = models.Reservation.objects.filter(
                restaurant=restaurant, is_booked=True, is_dependent=False
            ).count()
            restaurant.reservation_num = booked_count
            restaurant.save()

        except models.Reservation.DoesNotExist:
            is_success = False
        except Exception as e:
            print(f"Error: {e}")  # Debugging: エラーを表示
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
    is_posted = models.Review.objects.filter(customer=self.request.user).filter(restaurant=restaurant).exists()

    context.update({
      'restaurant': restaurant,
      'is_posted': is_posted,
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
        restaurant.rate = average_rate
    else:
        restaurant.rate = None
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

    context.update({
      'restaurant': restaurant,
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
        restaurant.rate = average_rate
    else:
        restaurant.rate = None
    restaurant.save()

    return response
  
  def form_invalid(self, form):
    return super().form_invalid(form)
  
  def get_context_data(self, **kwargs):
    pk = self.kwargs['pk']
    context = super(ReviewUpdateView, self).get_context_data(**kwargs)
    restaurant_id = models.Review.objects.filter(id=pk).first().restaurant.id
    restaurant = models.Restaurant.objects.filter(id=restaurant_id).first()

    context.update({
      'restaurant': restaurant,
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
        restaurant.rate = average_rate
      else:
        restaurant.rate = None
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
      restaurant.reservation_count = restaurant.reservation_set.filter(date__gte=today, is_booked=True, is_dependent = False).count()
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
  paginate_by = 20

  def get_queryset(self):
    restaurant_id = self.kwargs['restaurant_id']
    return models.DiningTable.objects.filter(restaurant_id=restaurant_id)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    restaurant_id = self.kwargs['restaurant_id']
        
    try:
        context['restaurant'] = models.Restaurant.objects.get(id=restaurant_id)
    except models.Restaurant.DoesNotExist:
        context['restaurant'] = None  # Handle gracefully in template
            
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
      context = super().get_context_data(**kwargs)
      restaurant_id = self.kwargs.get('restaurant_id')
      context['restaurant'] = models.Restaurant.objects.get(id=restaurant_id)
      return context

"""ダイニングテーブル削除 ================================== """
def dining_table_delete(request, restaurant_id, pk):
    table = get_object_or_404(models.DiningTable, pk=pk)

    if request.method == "POST":
        # Check if there are any reservations where is_booked=True or not-null
        existing_reservations = table.reservations.filter(Q(is_booked=True) | Q(is_booked__isnull=False))
        # existing_reservations = table.reservations.filter(Q(is_booked=True) | Q(is_booked__isnull=False))

        if existing_reservations.exists():
            # Set error message if deletion is blocked
            query_string = urlencode({'message': 'このテーブルは予約があるため削除できません。', 'type': 'error'})
        else:
            # Delete the table if no booked reservations exist
            table.delete()
            query_string = urlencode({'message': 'テーブルを削除しました。', 'type': 'success'})

        # Redirect with the appropriate message
        return redirect(f"{redirect('dining_table_list', restaurant_id=restaurant_id).url}?{query_string}")

    # Redirect to the list for non-POST requests
    return redirect('dining_table_list', restaurant_id=restaurant_id)

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


  # def form_valid(self, form):
  #   # Link the table to the correct restaurant using the restaurant_id from the URL
  #   restaurant_id = self.kwargs['restaurant_id']
  #   form.instance.restaurant = models.Restaurant.objects.get(id=restaurant_id)
  #   return super().form_valid(form)

  def form_valid(self, form):
    restaurant_id = self.kwargs['restaurant_id']
    restaurant = get_object_or_404(models.Restaurant, id=restaurant_id)
    form.instance.restaurant = restaurant
    
    # Call the parent class's form_valid method to save the menu
    response = super().form_valid(form)
    
    # Update the min_price and max_price after the menu is created
    min_price = models.Menu.objects.filter(restaurant=restaurant).aggregate(Min('price'))['price__min']
    max_price = models.Menu.objects.filter(restaurant=restaurant).aggregate(Max('price'))['price__max']
    
    # Update the restaurant's price information
    restaurant.min_price = min_price if min_price is not None else None
    restaurant.max_price = max_price if max_price is not None else None
    restaurant.save()

    return response

  def get_success_url(self):
    # Redirect to the list of dining tables for the restaurant after creating the table
    restaurant_id = self.kwargs['restaurant_id']
    return reverse_lazy('menu_list', kwargs={'restaurant_id': restaurant_id})

  def get_context_data(self, **kwargs):
    # Pass the restaurant context to the template
    context = super().get_context_data(**kwargs)
    context['restaurant'] = models.Restaurant.objects.get(id=self.kwargs['restaurant_id'])
    return context

""" メニュー削除 ================================== """
class MenuDeleteView(generic.DeleteView):
  model = models.Menu
  context_object_name = 'menu'

  def get_success_url(self):
    # Redirect to the list of menus for the restaurant after deletion
    restaurant_id = self.object.restaurant.id  # Get the restaurant ID from the object being deleted
    return reverse_lazy('menu_list', kwargs={'restaurant_id': restaurant_id})

  def form_valid(self, form):
    # First, delete the menu item
    response = super().form_valid(form)

    # Update the min_price and max_price of the restaurant
    restaurant = self.object.restaurant  # Get the associated restaurant
    min_price = models.Menu.objects.filter(restaurant=restaurant).aggregate(Min('price'))['price__min']
    max_price = models.Menu.objects.filter(restaurant=restaurant).aggregate(Max('price'))['price__max']
    restaurant.min_price = min_price if min_price is not None else None
    restaurant.max_price = max_price if max_price is not None else None
    restaurant.save()

    return response

  def delete(self, request, *args, **kwargs):
    # Call the super delete method to perform the deletion
    self.object = self.get_object()
    return super().delete(request, *args, **kwargs)
# class MenuDeleteView(generic.DeleteView):
#   model = models.Menu
#   template_name = 'menu/menu_delete.html'
#   context_object_name = 'menu'

#   def get_success_url(self):
#     # Redirect to the list of menus for the restaurant after deletion
#     restaurant_id = self.object.restaurant.id  # Get the restaurant ID from the object being deleted
#     return reverse_lazy('menu_list', kwargs={'restaurant_id': restaurant_id})

#   def form_valid(self, form):
#    # First, delete the menu item
#     response = super().form_valid(form)

#     # Update the min_price and max_price of the restaurant
#     restaurant = self.object.restaurant  # Get the associated restaurant
#     min_price = models.Menu.objects.filter(restaurant=restaurant).aggregate(Min('price'))['price__min']
#     max_price = models.Menu.objects.filter(restaurant=restaurant).aggregate(Max('price'))['price__max']
#     restaurant.min_price = min_price if min_price is not None else None
#     restaurant.max_price = max_price if max_price is not None else None
#     restaurant.save()

#     return response

#   def delete(self, request, *args, **kwargs):
#     # Call the super delete method to perform the deletion
#     self.object = self.get_object()
#     return super().delete(request, *args, **kwargs)

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

""" レビューの返信 ================================== """
class ReviewUpdateView2(generic.UpdateView):
    model = models.Review
    fields = ['reply']
    template_name = "review/review_update2.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add restaurant to the context
        context['restaurant'] = self.object.restaurant
        return context

    def get_success_url(self):
        restaurant_id = self.object.restaurant.id
        return reverse_lazy('review_list_2', kwargs={'pk': restaurant_id})

""" 誹謗中傷レビューの非表示対応 ================================== """
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
      restaurant.rate = average_rate
    else:
      restaurant.rate = None
    restaurant.save()

    return redirect(reverse('review_list_2', kwargs={'pk': review.restaurant.id}))

""" 予約リスト（店用） ================================== """
class ReservationListView2(generic.ListView):
    model = models.Reservation
    template_name = 'reservation/reservation_list2.html'
    context_object_name = 'reservations'
    paginate_by = 10

    def get_queryset(self):
        restaurant_id = self.kwargs['restaurant_id']
        restaurant = get_object_or_404(models.Restaurant, id=restaurant_id)

        # Handle 'from_date' parameter, with fallback to today's date.
        from_date = self.request.GET.get('from_date') or str(now().date())
        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()

        # Handle 'to_date' parameter, with optional filtering.
        to_date = self.request.GET.get('to_date')
        if to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

        queryset = models.Reservation.objects.filter(
            restaurant=restaurant,
            is_booked=True,
            is_dependent=False,
            date__gte=from_date
        ).select_related('menu', 'dining_table')

        if to_date:
            queryset = queryset.filter(date__lte=to_date)

        order_by = self.request.GET.get('order_by', 'date,time_start')
        fields = [field.strip() for field in order_by.split(',')]
        queryset = queryset.order_by(*fields)

        self.total_reservations_count = queryset.count()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant_id = self.kwargs['restaurant_id']
        context['restaurant'] = get_object_or_404(models.Restaurant, id=restaurant_id)

        # Ensure dates persist in the context
        context['from_date'] = self.request.GET.get('from_date') or str(now().date())
        context['to_date'] = self.request.GET.get('to_date') or ''

        context['total_reservations_count'] = self.total_reservations_count
        return context

""" 予約枠管理（店用） ================================== """
class ReservationManagementView(generic.TemplateView):
    template_name = 'reservation/reservation_management.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant_id = self.kwargs['restaurant_id']
        restaurant = get_object_or_404(models.Restaurant, id=restaurant_id)

        # Handle date selection from query parameters
        selected_date_str = self.request.GET.get('date')
        selected_date = timezone.now().date()
        if selected_date_str:
            try:
                selected_date = timezone.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass  # fallback to today's date if parsing fails

        # Handle table selection
        dining_table_id = self.request.GET.get('dining_table')
        dining_table = get_object_or_404(models.DiningTable, id=dining_table_id) if dining_table_id else None

        # Calculate week start and end
        week_start = selected_date - timedelta(days=selected_date.weekday())
        week_end = week_start + timedelta(days=6)

        # Get reservations for the selected week and table
        reservations = models.Reservation.objects.filter(
            restaurant=restaurant,
            dining_table=dining_table,
            date__range=[week_start, week_end]
        ).select_related('menu', 'dining_table')

        # Generate 30-minute time slots from 9:00 to 22:30
        time_slots = [timezone.datetime.combine(selected_date, timezone.datetime.min.time()) + timedelta(hours=9) + timedelta(minutes=30 * i) for i in range(28)]

        # Provide context data
        context['restaurant'] = restaurant
        context['selected_date'] = selected_date
        context['dining_table'] = dining_table
        context['week_dates'] = [week_start + timedelta(days=i) for i in range(7)]
        context['time_slots'] = [slot.time() for slot in time_slots]
        context['reservations'] = reservations
        context['tables'] = models.DiningTable.objects.filter(restaurant=restaurant)

        # Calculate previous and next weeks' dates for easy access
        context['prev_week'] = (selected_date - timedelta(weeks=1)).strftime('%Y-%m-%d')
        context['this_week'] = timezone.now().date().strftime('%Y-%m-%d')
        context['next_week'] = (selected_date + timedelta(weeks=1)).strftime('%Y-%m-%d')

        return context

""" 予約枠作成（店用） ================================== """
class ReservationSlotCreateView(View):
    template_name = 'reservation/reservation_slot_create.html'

    def get_context_data(self, **kwargs):
        """Provide context for the form with restaurant and table details."""
        restaurant = get_object_or_404(models.Restaurant, id=self.kwargs['restaurant_id'])
        tables = models.DiningTable.objects.filter(restaurant=restaurant)

        # Generate 30-minute time slots from 9:00 to 22:30
        start_time = timezone.datetime.combine(timezone.now(), timezone.datetime.min.time()) + timedelta(hours=9)
        time_slots = [(start_time + timedelta(minutes=30 * i)).time() for i in range(28)]

        return {'restaurant': restaurant, 'tables': tables, 'time_slots': time_slots}

    def get(self, request, *args, **kwargs):
        """Render the template with the form to create reservation slots."""
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """Handle slot creation for selected tables and date range."""
        restaurant = get_object_or_404(models.Restaurant, id=kwargs['restaurant_id'])
        
        # Retrieve the date range and table selections from the form
        selected_start_date = request.POST.get('from_date')
        selected_end_date = request.POST.get('to_date')
        selected_tables = request.POST.getlist('tables')
        duration_mins = request.POST.getlist('duration_min')  # Retrieve as a list

        # Convert selected dates to datetime.date objects
        start_date = timezone.datetime.fromisoformat(selected_start_date).date()
        end_date = timezone.datetime.fromisoformat(selected_end_date).date()

        # Debugging: Print values to ensure they're retrieved correctly
        print("Selected Start Date:", selected_start_date)
        print("Selected End Date:", selected_end_date)
        print("Selected Tables:", selected_tables)
        print("Durations (minutes):", duration_mins)

        created_slots_count = 0

        # Iterate through each date in the selected range
        current_date = start_date
        while current_date <= end_date:
            # Iterate through selected tables to create time slots for the current date
            for table_id in selected_tables:
                table = get_object_or_404(models.DiningTable, id=table_id)
                start_time = timezone.datetime.combine(current_date, timezone.datetime.min.time()) + timedelta(hours=9)

                for i in range(len(duration_mins)):  # Loop through each duration
                    slot_time = start_time + timedelta(minutes=30 * i)

                    # Check for existing reservations to avoid duplicates
                    reservation = models.Reservation.objects.filter(
                        restaurant=restaurant,
                        dining_table=table,
                        date=current_date,
                        time_start=slot_time
                        ).first()
                    
                    # 枠が存在している場合、予約なしならduration_minを上書き、予約ありなら変更せず
                    if reservation:
                        if not reservation.is_booked:
                          reservation.duration_min = int(duration_mins[i])
                          reservation.save()
                          print(f"Updated duration for {table.name_for_customer} at {slot_time} on {current_date}")
                        else:
                          print(f"Slot is already booked for {table.name_for_customer} at {slot_time} on {current_date}")
                    # 枠がなければ予約枠を作成
                    else:
                        models.Reservation.objects.create(
                            restaurant=restaurant,
                            dining_table=table,
                            date=current_date,
                            time_start=slot_time,
                            duration_min=int(duration_mins[i]),  # Use the corresponding duration
                        )
                        created_slots_count += 1

            # Move to the next date
            current_date += timedelta(days=1)

        # Provide user feedback on the number of created slots
        messages.success(request, f"{created_slots_count}件の予約枠が作成されました。")
        return redirect('reservation_management', restaurant_id=restaurant.id)