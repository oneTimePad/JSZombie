from django.conf.urls import url
from rest_framework.routers import SimpleRouter


from .views import *


urlpatterns=[
	url(r'^$',IndexPage.as_view(),name='approot'),
	url(r'^zombieconnect$',ZombieConnection.as_view(),name='zc'),
	url(r'^createinjection$',InjectionCreate.as_view(),name='injection'),
]

router = SimpleRouter(trailing_slash=False)
router.register(r'control',ZombieControl,'control')
urlpatterns+=router.urls
