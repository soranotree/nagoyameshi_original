from django import forms
from .models import Reservation, Review

class ReservationCreateForm(forms.ModelForm):
  class Meta:
    model = Reservation
    fields = ('date', 'time_start', 'time_end', 'number_of_people', 'dining_table',)
  
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
    # Reservation.TIMES を使用して time_end に選択肢を設定
    self.fields['time_end'].widget = forms.Select(
      choices=Reservation.TIMES
      )
    self.fields['time_end'].widget.attrs['class'] = 'form-control'
    self.fields['number_of_people'].widget.attrs['class'] = 'form-control'
    self.fields['dining_table'].widget.attrs['class'] = 'form-control'

# class ReviewCreateForm(forms.ModelForm):
  # class Meta:
    # model = Review
    # fields = ('comment', 'rate')
    # widgets = {'rate': forms.RadioSelect()}
  # 
  # def __init__(self, *args, **kwargs):
    # super().__init__(*args, **kwargs)
    # self.fields['comment'].widget.attrs['class'] = 'form-control'
    # self.fields['comment'].widget.attrs['cols'] = '30'
    # self.fields['comment'].widget.attrs['rows'] = '5'
    # self.fields['rate'].widget.attrs['class'] = 'form-check-input'
