from django import forms
from .models import Reservation, Review, Restaurant, DiningTable, Menu

class ReservationCreateForm(forms.ModelForm):
  class Meta:
    model = Reservation
    fields = ('date', 'time_start', 'number_of_people', 'dining_table',)
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['date'].widget.attrs['class'] = 'form-control'
    self.fields['date'].widget.attrs['id'] = 'reservation_date'
    self.fields['date'].widget.attrs['name'] = 'reservation_date'
    # Reservation.TIMES を使用して time_start に選択肢を設定
    self.fields['time_start'].widget = forms.Select(
      choices=Reservation.TIMES
      )
    self.fields['time_start'].widget.attrs['class'] = 'form-control'
    self.fields['number_of_people'].widget.attrs['class'] = 'form-control'
    self.fields['dining_table'].widget.attrs['class'] = 'form-control'

class ReviewCreateForm(forms.ModelForm):
  class Meta:
    model = Review
    fields = ('visit_date', 'comment', 'rate')
    widgets = {'rate': forms.RadioSelect()}
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['visit_date'].widget.attrs['class'] = 'form-control'
    self.fields['visit_date'].widget.attrs['id'] = 'visit_date'
    self.fields['visit_date'].widget.attrs['name'] = 'visit_date'
    self.fields['comment'].widget.attrs['class'] = 'form-control'
    self.fields['comment'].widget.attrs['cols'] = '30'
    self.fields['comment'].widget.attrs['rows'] = '5'
    self.fields['rate'].widget.attrs['class'] = 'form-check-input'

class RestaurantCreateForm(forms.ModelForm):
  class Meta:
    model = Restaurant
    fields = '__all__'
    exclude = ['rate', 'review_num', 'reservation_num', 'price', 'max_price', 'min_price', 'shop_owner']
    # fields = ('visit_date', 'comment', 'rate')
    # widgets = {'rate': forms.RadioSelect()}

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['description'].widget = forms.Textarea()
    self.fields['description'].widget.attrs['class'] = 'form-control'
    self.fields['description'].widget.attrs['rows'] = '10'  # Specify the number of rows for the textarea
    self.fields['description'].widget.attrs['placeholder'] = '店舗の詳細を記入してください'  # Optional placeholder text  #   self.fields['visit_date'].widget.attrs['class'] = 'form-control'
    self.fields['business_time'].widget.attrs['placeholder'] = '例：9:30～22:00'  # Optional placeholder text  #   self.fields['visit_date'].widget.attrs['class'] = 'form-control'
    self.fields['close_day_of_week'].widget.attrs['placeholder'] = '例：「火、水」、「不定休」、「年中無休」'  # Optional placeholder text  #   self.fields['visit_date'].widget.attrs['class'] = 'form-control'

class RestaurantUpdateForm(forms.ModelForm):
  class Meta:
    model = Restaurant
    fields = '__all__'
    exclude = ['rate', 'review_num', 'reservation_num', 'price', 'max_price', 'min_price', 'shop_owner']
    # fields = ('visit_date', 'comment', 'rate')
    # widgets = {'rate': forms.RadioSelect()}
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # self.fields['description'].widget.attrs['class'] = 'form-control'
    # self.fields['description'].widget.attrs['rows'] = '15'  # Specify the number of rows for the textarea
    self.fields['description'].widget = forms.Textarea()
    self.fields['description'].widget.attrs['class'] = 'form-control'
    self.fields['description'].widget.attrs['cols'] = '30'
    self.fields['description'].widget.attrs['rows'] = '5'


    # self.fields['description'].widget.attrs['placeholder'] = '店舗の詳細を記入してください'  # Optional placeholder text  #   self.fields['visit_date'].widget.attrs['class'] = 'form-control'
  #   self.fields['visit_date'].widget.attrs['id'] = 'visit_date'
  #   self.fields['visit_date'].widget.attrs['name'] = 'visit_date'
  #   self.fields['comment'].widget.attrs['class'] = 'form-control'
  #   self.fields['comment'].widget.attrs['cols'] = '30'
  #   self.fields['comment'].widget.attrs['rows'] = '5'
  #   self.fields['rate'].widget.attrs['class'] = 'form-check-input'

class DiningTableUpdateForm(forms.ModelForm):
    class Meta:
        model = DiningTable
        fields = ['name_for_internal', 'name_for_customer', 'min_people', 'max_people']
        
class DiningTableCreateForm(forms.ModelForm):
    class Meta:
        model = DiningTable
        fields = ['name_for_internal', 'name_for_customer', 'min_people', 'max_people']
        
class MenuUpdateForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'description', 'price', 'available_from', 'available_end', 'photo']

    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.fields['available_from'].widget = forms.TimeInput(
            format='%H:%M',
            attrs={
                'class': 'form-control',  # Add Bootstrap or custom class if needed
            }
        )
      self.fields['available_end'].widget = forms.TimeInput(
            format='%H:%M',
            attrs={
                'class': 'form-control',  # Add Bootstrap or custom class if needed
            }
        )

class MenuCreateForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'description', 'price', 'available_from', 'available_end', 'photo']
        
    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.fields['name'].widget.attrs['placeholder'] = '例：〇〇定食、〇〇コース'  # Optional placeholder text  #   self.fields['visit_date'].widget.attrs['class'] = 'form-control'
      self.fields['description'].widget.attrs['placeholder'] = '例：当店おススメのメニューです。ごゆっくりお召し上がりください。'  # Optional placeholder text  #   self.fields['visit_date'].widget.attrs['class'] = 'form-control'
      self.fields['price'].widget.attrs['placeholder'] = '例：800'  # Optional placeholder text  #   self.fields['visit_date'].widget.attrs['class'] = 'form-control'
      self.fields['available_from'].widget = forms.TimeInput(
            format='%H:%M',
            attrs={
                'class': 'form-control',  # Add Bootstrap or custom class if needed
                'placeholder': '例：9:00',  # Optional placeholder text
            }
        )
      self.fields['available_end'].widget = forms.TimeInput(
            format='%H:%M',
            attrs={
                'class': 'form-control',  # Add Bootstrap or custom class if needed
                'placeholder': '例：21:30',  # Optional placeholder text
            }
        )
