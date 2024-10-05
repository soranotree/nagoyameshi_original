from django import forms
from .models import Reservation, Review, Restaurant

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
    # fields = ('visit_date', 'comment', 'rate')
    # widgets = {'rate': forms.RadioSelect()}
  
  # def __init__(self, *args, **kwargs):
  #   super().__init__(*args, **kwargs)
  #   self.fields['visit_date'].widget.attrs['class'] = 'form-control'
  #   self.fields['visit_date'].widget.attrs['id'] = 'visit_date'
  #   self.fields['visit_date'].widget.attrs['name'] = 'visit_date'
  #   self.fields['comment'].widget.attrs['class'] = 'form-control'
  #   self.fields['comment'].widget.attrs['cols'] = '30'
  #   self.fields['comment'].widget.attrs['rows'] = '5'
  #   self.fields['rate'].widget.attrs['class'] = 'form-check-input'

class RestaurantUpdateForm(forms.ModelForm):
  class Meta:
    model = Restaurant
    fields = '__all__'
    exclude = ['rate', 'review_num', 'reservation_num', 'price', 'max_price', 'min_price', 'shop_owner']
    # fields = ('visit_date', 'comment', 'rate')
    # widgets = {'rate': forms.RadioSelect()}
  
  # def __init__(self, *args, **kwargs):
  #   super().__init__(*args, **kwargs)
  #   self.fields['visit_date'].widget.attrs['class'] = 'form-control'
  #   self.fields['visit_date'].widget.attrs['id'] = 'visit_date'
  #   self.fields['visit_date'].widget.attrs['name'] = 'visit_date'
  #   self.fields['comment'].widget.attrs['class'] = 'form-control'
  #   self.fields['comment'].widget.attrs['cols'] = '30'
  #   self.fields['comment'].widget.attrs['rows'] = '5'
  #   self.fields['rate'].widget.attrs['class'] = 'form-check-input'
