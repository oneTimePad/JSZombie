from django.conf.urls import url
from rest_framework.routers import SimpleRouter
from .views import *

urlpatterns=[
	url(r'^$',IndexPage.as_view(),name='approot'),

]

router = SimpleRouter(trailing_slash=False)
router.register(r'control',Controller,'control')
urlpatterns+=router.urls
router = SimpleRouter(trailing_slash=False)
router.register(r'zombie',ZombieInterface,'zombie')
urlpatterns+=router.urls
